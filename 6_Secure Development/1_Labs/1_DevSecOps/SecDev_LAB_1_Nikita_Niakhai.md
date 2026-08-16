# 1 devsecops

Name of report: SecDev_LAB_1_Nikita_Niakhai
Course: Secure Development
Performed by Nikita Niakhai

---

Build a CI/CD pipeline where security checks are enforced automatically. The pipeline must block releases when security rules are violated and produce evidence that security controls were applied.

# Разбор GitLab CI/CD конфига (DevSecOps pipeline)

---

## Верхний уровень — структура файла

```yaml
stages:
  - security-scan
  - sast
  - sca
  - build
  - test
  - docker-build
  - image-scan
  - docker-push
  - deploy
  - security-report
```

**`stages`** — определяет порядок выполнения этапов. Джобы внутри одного stage выполняются **параллельно**. Следующий stage стартует только после успеха всех джоб текущего.

---

## Variables

```yaml
variables:
  DOCKER_IMAGE_NAME: "nikitanekhay/st19-spa"
  DOCKER_IMAGE_TAG: "${CI_COMMIT_SHORT_SHA}"
  ANSIBLE_FORCE_COLOR: "true"
```

**`variables`** — глобальные переменные, доступны во всех джобах.

`CI_COMMIT_SHORT_SHA` — встроенная переменная GitLab, первые 8 символов хеша коммита. Используется как тег образа — это правильная практика для traceability (можно по тегу найти точный коммит).

---

## Cache

```yaml
cache:
  key: "${CI_COMMIT_REF_SLUG}"
  paths:
    - node_modules/
    - .npm/
  policy: pull-push
```

**`cache`** — кеш между джобами и пайплайнами.

`key` — уникальный ключ кеша. `CI_COMMIT_REF_SLUG` = имя ветки в safe-формате (например `main`, `develop`). Разные ветки — разный кеш.

`policy: pull-push` — джоба скачивает кеш в начале и загружает в конце. Можно ставить `pull` если джоба только читает — ускоряет пайплайн.

---

## Джобы — общий синтаксис

Каждая джоба имеет одинаковую структуру:

```yaml
job-name:
  stage: <имя стейджа>
  tags:
    - st19-runner        # какой runner использовать
  needs: []              # DAG-зависимости
  dependencies: []       # от кого брать artifacts
  script: []             # что выполнять
  before_script: []      # до script
  after_script: []       # после script (выполняется даже при failure)
  artifacts: {}          # что сохранять
  only: []               # условия запуска
  when: manual           # триггер
  environment: {}        # окружение (для CD)
```

---

## Stage: security-scan — `secrets-scan`

```yaml
secrets-scan:
  stage: security-scan
  script:
    - docker run --rm -v "$CI_PROJECT_DIR:/repo" zricethezav/gitleaks:latest \
        detect --source=/repo --no-git --report-format=json --report-path=/repo/gitleaks-report.json
```

**Инструмент:** Gitleaks — сканирует файлы репозитория на наличие секретов (токены, пароли, ключи).

- `-no-git` — сканирует файловую систему, не git-историю.
- `-rm` — удаляет контейнер после выполнения.
- `v "$CI_PROJECT_DIR:/repo"` — монтирует папку проекта в контейнер.

Если `SCAN_EXIT != 0` — пайплайн падает. **Это gate — блокирует дальнейшие стейджи.**

```yaml
artifacts:
  when: always   # сохраняет репорт даже если джоба упала
  expire_in: 1 week
```

---

## Stage: sast — `sast-semgrep`

**Инструмент:** Semgrep — статический анализ кода (SAST).

- `-config=auto` — автоматически выбирает правила под язык проекта.

`|| true` — джоба не падает при находках. Результат анализируется кастомным скриптом `ci-scripts/sast-check.py`.

Это мягкий gate — находки логируются, но пайплайн продолжается. Правильно для начальной интеграции SAST.

---

## Stage: sca — `sca-trivy`

**Инструмент:** Trivy в режиме `fs` — Software Composition Analysis.

Сканирует зависимости проекта (package.json, go.mod и т.д.) на CVE.

- `-scanners vuln` — только уязвимости, без секретов и misconfig.
- `v trivy-cache:/root/.cache/trivy` — named volume для кеша базы CVE. Без этого Trivy качает базу при каждом запуске.

---

## Stage: build — `build-app`

```yaml
cache:
  policy: pull-push   # переопределяет глобальный cache
artifacts:
  paths:
    - .
    - Dockerfile
  expire_in: 1 hour
```

Собирает приложение. Артефакт — весь каталог проекта — передаётся в следующие джобы.

`expire_in: 1 hour` — артефакты билда не нужны долго, экономия места на runner.

---

## Stage: test — `test-app`

```yaml
needs:
  - job: build-app
    artifacts: true
dependencies:
  - build-app
```

**`needs`** — DAG (Directed Acyclic Graph). Джоба не ждёт всего предыдущего stage, а стартует сразу как завершится `build-app`. Ускоряет пайплайн.

**`dependencies`** — от кого скачивать artifacts. Без этого GitLab скачивает артефакты от всех предыдущих джоб.

Тесты здесь минимальные — проверка наличия файлов. На реальном проекте здесь `npm test` или `pytest`.

---

## Stage: docker-build — `build-docker`

```yaml
if [ "$CI_COMMIT_REF_NAME" = "main" ]; then
  docker build -t ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} .
  docker build -t ${DOCKER_IMAGE_NAME}:latest .
  docker build -t ${DOCKER_IMAGE_NAME}:production .
```

**Проблема:** `docker build` вызывается 3 раза для одного образа. Это лишняя работа. Правильно:

```bash
docker build -t ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} \
             -t ${DOCKER_IMAGE_NAME}:latest \
             -t ${DOCKER_IMAGE_NAME}:production .
```

Теги по веткам: `main` → `latest`, `production`. `develop` → `develop`.

---

## Stage: image-scan — `image-scan`

```yaml
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock ...
  aquasec/trivy:latest image ...
```

Trivy в режиме `image` — сканирует уже собранный Docker-образ.

- `v /var/run/docker.sock` — монтирует Docker socket, чтобы Trivy мог обратиться к локальному Docker daemon и получить образ.

**Это риск безопасности** — доступ к docker.sock = root на хосте. На продакшен runner лучше использовать Trivy с `--input` (tar-архив образа).

---

## Stage: docker-push — `push-docker`

```yaml
echo "$DOCKER_HUB_PASSWORD" | docker login -u "$DOCKER_HUB_USERNAME" --password-stdin
```

- `-password-stdin` — пароль читается из stdin, не попадает в `ps aux` и логи шелла. Правильная практика.

`$DOCKER_HUB_PASSWORD` и `$DOCKER_HUB_USERNAME` — CI/CD variables в GitLab (Settings → CI/CD → Variables), masked.

```yaml
dependencies: []   # не скачивает артефакты от предыдущих джоб — образ уже в локальном Docker
```

---

## Stage: deploy

### `deploy-production`

```yaml
when: manual          # ручной триггер, не запускается автоматически
environment:
  name: production
  url: http://deploy.st19.sne.com:8080
```

**`when: manual`** — деплой в прод требует ручного подтверждения в GitLab UI. Стандарт для production.

**`environment`** — создаёт окружение в GitLab (Deployments → Environments). Позволяет видеть историю деплоев и делать rollback через UI.

Деплой через Ansible:

```bash
ansible-playbook -i inventory.ini deploy-playbook.yml \
  -e "docker_image_name=${DOCKER_IMAGE_NAME}" -v
```

- `e` — передача переменных в playbook. `v` — verbose логи.

### `deploy-staging`

```yaml
when: on_success   # автоматически после успеха push-docker
```

Staging деплоится автоматически при push в `develop`. Production — только вручную.

### `rollback-production`

```yaml
script:
  - ssh deploy-server "docker stop st19-spa && docker rm st19-spa"
  - ssh deploy-server "docker run -d --name st19-spa -p 8080:80 ${DOCKER_IMAGE_NAME}:production"
```

Rollback через SSH — останавливает текущий контейнер, запускает с тегом `production`. **Проблема:** тег `production` всегда перезаписывается при новом деплое — это не надёжный механизм rollback. Правильно — хранить предыдущий SHA тег и откатываться на него.

---

## Stage: security-report

```yaml
needs:
  - job: secrets-scan
    artifacts: true
  - job: sast-semgrep
    artifacts: true
  - job: sca-trivy
    artifacts: true
  - job: image-scan
    artifacts: true
```

Агрегирует все JSON-репорты от security джоб и генерирует сводный отчёт.

`expire_in: 30 days` — security-репорты хранятся дольше для audit trail.

---

## `only` — условия запуска

```yaml
only:
  - main
  - develop
  - merge_requests
```

Джоба запускается только на указанных ветках и для MR. На feature-ветках пайплайн не запускается (кроме MR). Современная альтернатива — `rules:`, более гибкая.

---

## Итоговая схема пайплайна

```
secrets-scan ──┐
sast-semgrep ──┼── (параллельно) ──► build ──► test ──► docker-build ──► image-scan 
																										──► ppush ──► deploy
sca-trivy ─────┘                                                                              │
security-report
```
