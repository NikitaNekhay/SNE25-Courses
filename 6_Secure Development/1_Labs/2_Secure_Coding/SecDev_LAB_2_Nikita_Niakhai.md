# 2 Secure coding

Name of report: SecDev_LAB_2_Nikita_Niakhai
Course: Secure Development
Performed by Nikita Niakhai
Date submission: 19.02.2026
---

## Task 1: Analyze vulnerable hash table code

step 1
Reviewed hash.c and hash.h implementation. The code is a naive hash table using separate chaining for collision resolution.

Key structures:

- `PairValue`: key-value pair with linked list Next pointer
- `HashMap`: array of 128 buckets (PairValue pointers)

**CWE Detection Focus:** This lab targets CWE Top 25 weaknesses including CWE-787 (OOB Write), CWE-120/119 (Buffer Boundaries), CWE-416 (Use-After-Free), and CWE-908 (Uninitialized Resources).

step 2
Compiled original code to establish baseline:

```bash
gcc -Wall -Wextra -std=c11 hash.c -o hash_original
```

No compilation errors, but many warnings if using stricter flags.

step 3
Ran static analysis with cppcheck:

```
cppcheck --enable=all hash.c hash.h
```

Output revealed 7 security-related code issues. Documented each with CWE classification:

- **CWE-787** (OOB Write) - Critical
- **CWE-120/119** (Buffer Bounds) - Critical
- **CWE-416** (Use-After-Free) - Critical
- **CWE-908** (Uninitialized) - High
- **CWE-835** (Infinite Loop) - Medium
- **CWE-134** (Format String) - High
- **CWE-116** (Data Structure) - Medium

step 4
Analyzed each vulnerability for security impact. All vulnerabilities mapped to CWE Top 25:

| # | CWE | Location | Type | Impact | Top 25 Rank |
|---|-----|----------|------|--------|---|
| 1 | **CWE-835** | HashIndex():14 | Infinite loop | DoS, memory read OOB | Related to #23 |
| 2 | **CWE-787** | HashIndex():18 | Missing modulo (OOB Write) | Array index overflow, memory corruption | **#1** ⚠️ |
| 3 | **CWE-908** | HashInit():22 | Uninitialized memory | Garbage pointers, crash | Related to #19 |
| 4 | **CWE-116** | HashAdd():29 | Wrong pointer assignment | Data loss, memory leak | Not in Top 25 |
| 5 | **CWE-120** | HashFind():37 | Buffer overflow (strcpy) | Overflow, wrong logic | Part of #19 ⚠️ |
| 6 | **CWE-416** | HashDelete():48 | Use-after-free | Data corruption | **#7** ⚠️ |
| 7 | **CWE-134** | HashDump():60 | Format string injection | Memory leak/write via %x/%n | Related to #4 |

**⚠️ = Critical (Top 25 ranking)**

---

## Task 2: Annotate original files with bug explanations

step 1
Added inline comments to hash.c directly below each vulnerable code line. Comments follow format:

```
/* [BUG-N] LOCATION: ... SECURITY: ... CATEGORY: ... CWE: ... */
```

Each bug documented with:

- Exact code location and line number
- Why it's a security problem
- Affected CIA component (Confidentiality, Integrity, Availability)
- CWE classification

step 2
Annotated hash.h with security notes on struct constraints:

- `KEY_STRING_MAX = 255`: Buffer overflow risk with unbounded copy
- `MAP_MAX = 128`: HashIndex must respect this boundary

step 3
Completed files: hash.c and hash.h (annotated originals)

---

## Task 3: Create fixed versions with corrections

step 1
Copied hash.c → hash_fixed.c, hash.h → hash_fixed.h

step 2
Applied fixes for each vulnerability with CWE remediation:

```
BUG-1: CWE-835 (Infinite Loop)
OLD: for (char* c = key; c; c++)
NEW: for (const char* c = key; *c != '\0'; c++)
WHY: Check dereferenced character, not pointer
BUG-2: CWE-787 (Out-of-bounds Write) ⚠️ TOP 25 #1
OLD: return sum;
NEW: return sum % MAP_MAX;
WHY: Force index into 0-127 range
BUG-3: CWE-908 (Uninitialized Resource)
OLD: malloc(sizeof(HashMap))
NEW: calloc(1, sizeof(HashMap))
WHY: calloc zeros memory, all pointers = NULL
BUG-4: CWE-116 (Improper Data Structure)
OLD: value->Next = map->data[idx]->Next;
NEW: value->Next = map->data[idx];
WHY: Link to head, not head->next; maintains chain
BUG-5: CWE-120/CWE-119 (Buffer Bounds Violation) ⚠️ TOP 25 #19
OLD: if (strcpy(val->KeyName, key)) { ... }
NEW: if (strncmp(val->KeyName, key, KEY_STRING_MAX) == 0) { ... }
WHY: Correct comparison function, bounded input
BUG-6: CWE-416 (Use-After-Free) ⚠️ TOP 25 #7
ADD: break; after unlinking node
WHY: Prevent stale pointer access, delete only one node
BUG-7: CWE-134 (Format String Injection)
OLD: printf(val->KeyName);
NEW: printf("%s", val->KeyName);
WHY: Use literal format string, not user data
```

step 3
Compiled fixed version:

```bash
gcc -Wall -Wextra -Werror -std=c11 -fstack-protector-strong \

-D_FORTIFY_SOURCE=2 -Wformat=2 hash_fixed.c -o hash_fixed
```

Compiled cleanly with no warnings.

step 4
Verified fixed code against original bugs:

- Infinite loop fixed: String loop terminates at \0
- OOB prevented: Modulo forces valid indices
- Memory safe: calloc initializes pointers
- Collision chain: Correct prepend logic
- String safety: strncmp with bounds + printf("%s", ...)
- No use-after-free: break in delete loop
- No format string: literal "%s" format

---

## Task 4: Create system-level hardening instructions

step 1
Documented 10 hardening techniques in hardenings.txt:

1. Compiler flags: -Wall -Wextra -Werror -fstack-protector-strong -D_FORTIFY_SOURCE=2
2. Static analysis: cppcheck --enable=all
3. Dynamic analysis: valgrind --leak-check=full
4. Address sanitizer: -fsanitize=address -fsanitize=undefined
5. String safety: Replace strcpy → strncpy, sprintf → snprintf
6. Memory initialization: malloc → calloc for zero-init
7. Loop control: Check dereferenced values, not pointers
8. Bounds enforcement: Apply modulo to indices
9. Code review checklist
10. CI/CD integration (Makefile example)

step 2
Each hardening includes:

- How to apply it (commands, flags, code patterns)
- Why it protects against the vulnerabilities
- All instructions reproducible on Ubuntu 20.04+

step 3
Completed: hardenings.txt (ready for submission)

---

## Task 5: Prepare submission package

step 1
Verified all files present:

```bash
ls -l hash.c hash.h hash_fixed.c hash_fixed.h hardenings.txt
```

All 5 files created and annotated/fixed as required.

step 2
Created zip archive:

```bash
zip Nikita_Niakhai_lab_2.zip hash.c hash.h hash_fixed.c hash_fixed.h hardenings.txt
```

Zip structure matches lab requirements:

```
Nikita_Niakhai_lab_2.zip
├── hash.c (original + bug comments)
├── hash.h (original + security notes)
├── hash_fixed.c (fixed code + explanation comments)
├── hash_fixed.h (fixed code + hardening notes)
└── hardenings.txt (system-level protections)
```

---

## Summary

Completed secure coding lab with full vulnerability analysis:

**CWE Vulnerabilities Identified (7 total):**

- ⚠️ **CWE-787** (Out-of-bounds Write) — TOP 25 #1
- ⚠️ **CWE-120/CWE-119** (Buffer Bounds Violation) — TOP 25 #19
- ⚠️ **CWE-416** (Use-After-Free) — TOP 25 #7
- **CWE-908** (Uninitialized Resource)
- **CWE-835** (Infinite Loop)
- **CWE-134** (Format String Injection)
- **CWE-116** (Improper Data Structure)

**Analysis Summary:**

- **3 of 7 vulnerabilities ranked in CWE Top 25** Most Dangerous Software Weaknesses
- **3 critical memory safety issues** (CWE-787, CWE-120/119, CWE-416)
- **CIA impact documented**: 6 integrity issues, 3 availability issues, 2 confidentiality leaks
