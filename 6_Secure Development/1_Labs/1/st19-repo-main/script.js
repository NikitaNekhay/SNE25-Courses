
// Register service worker for PWA (only works over http/https)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('sw.js')
            .then(reg => {
                console.log('Service Worker registered successfully', reg.scope);
            })
            .catch(err => {
                console.error('Service Worker registration failed:', err);
                // Optional: show message in UI if needed
                // document.body.insertAdjacentHTML('beforeend', '<p style="color:red;">Note: Installable PWA features require running via http/https (not file://). Use a local server.</p>');
            });
    });
} else {
    console.warn('Service Workers not supported in this browser.');
}

// Fetch currency rates
fetch('https://www.cbr-xml-daily.ru/daily_json.js')
    .then(response => response.json())
    .then(data => {
        const usd = data.Valute.USD.Value.toFixed(2);
        const eur = data.Valute.EUR.Value.toFixed(2);
        document.getElementById('currency-data').innerHTML = `USD: ${usd} RUB<br>EUR: ${eur} RUB`; // nosemgrep: javascript.browser.security.insecure-document-method.insecure-document-method
    })
    .catch(() => {
        document.getElementById('currency-data').innerHTML = 'Error loading currency data.';
    });

// Fetch weather – use open-meteo.com (free, no CORS issues, no API key)
fetch('https://api.open-meteo.com/v1/forecast?latitude=55.7558&longitude=37.6173&current=temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m&timezone=Europe%2FMoscow')
    .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    })
    .then(data => {
        const current = data.current;
        const temp = current.temperature_2m.toFixed(1);
        const humidity = current.relative_humidity_2m;
        const wind = current.wind_speed_10m.toFixed(1);
        // Simple weather code to description (WMO codes: https://open-meteo.com/en/docs)
        let desc = 'Unknown';
        const code = current.weather_code;
        if (code === 0) desc = 'Clear sky';
        else if (code <= 3) desc = 'Mainly clear / cloudy';
        else if (code <= 48) desc = 'Fog / rime';
        else if (code <= 67 || code === 80 || code === 81) desc = 'Rain / showers';
        else if (code <= 86) desc = 'Snow / sleet';
        else if (code >= 95) desc = 'Thunderstorm';

        document.getElementById('weather-data').innerHTML = // nosemgrep: javascript.browser.security.insecure-document-method.insecure-document-method
            `Moscow (via Open-Meteo)<br>` +
            `Temperature: ${temp}°C<br>` +
            `Condition: ${desc}<br>` +
            `Humidity: ${humidity}%<br>` +
            `Wind: ${wind} km/h`;
    })
    .catch(err => {
        console.error('Weather fetch error:', err);
        document.getElementById('weather-data').innerHTML = 'Error loading weather. (Try refreshing or check network)';
    });

// Fetch DW RUSSIA RSS – using corsproxy.io (very common & simple prefix style)
const tassUrl = 'https://rss.dw.com/rdf/rss-ru-all';
const proxyPrefix = 'https://corsproxy.io/?';
const fullUrl = proxyPrefix + encodeURIComponent(tassUrl);

fetch(fullUrl)
    .then(response => {
        if (!response.ok) {
            throw new Error(`Proxy responded with status ${response.status}`);
        }
        return response.text();
    })
    .then(str => {
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(str, "text/xml");

        // Better parse error check
        if (xmlDoc.getElementsByTagName('parsererror').length > 0) {
            const errorNode = xmlDoc.getElementsByTagName('parsererror')[0];
            throw new Error('XML parse failed: ' + (errorNode.textContent || 'Unknown error'));
        }

        const items = xmlDoc.querySelectorAll('item');
        const list = document.getElementById('news-list');
        list.innerHTML = '';  // clear old content

        if (items.length === 0) {
            list.innerHTML = '<li>No news items found in feed.</li>';
            return;
        }

        Array.from(items).slice(0, 5).forEach(item => {
            const title = item.querySelector('title')?.textContent.trim() || 'No title';
            const link = item.querySelector('link')?.textContent.trim() || '#';
            const pubDate = item.querySelector('pubDate')?.textContent.trim() || '';
            const desc = item.querySelector('description')?.textContent.trim() || '';

            const dateStr = pubDate 
                ? new Date(pubDate).toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'short' })
                : '';

            const li = document.createElement('li');
            // nosemgrep: javascript.browser.security.insecure-document-method.insecure-document-method
            li.innerHTML = `
                <a href="${link}" target="_blank" rel="noopener noreferrer" class="news-title">${title}</a>
                ${dateStr ? `<div class="news-date">${dateStr}</div>` : ''}
                ${desc ? `<div class="news-desc">${desc.substring(0, 140)}${desc.length > 140 ? '…' : ''}</div>` : ''}
            `;
            list.appendChild(li);
        });
    })
    .catch(err => {
        console.error('DW RUSSIA RSS fetch failed:', err);
        document.getElementById('news-list').innerHTML = 
            '<li>Failed to load DW RUSSIA news.<br>Possible reasons: proxy limit, network issue, or RSS unavailable.<br>Refresh page or try later.</li>';
    });

// Dots animation
const canvas = document.getElementById('dots-canvas');
const ctx = canvas.getContext('2d');
canvas.width = canvas.offsetWidth;
canvas.height = canvas.offsetHeight;

let particles = [];

function createParticles(x, y) {
    for (let i = 0; i < 50; i++) {
        particles.push({
            x: x,
            y: y,
            vx: Math.random() * 4 - 2,
            vy: Math.random() * 4 - 2,
            radius: Math.random() * 3 + 1,
            color: `hsl(${Math.random() * 360}, 100%, 50%)`,
            alpha: 1
        });
    }
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach((p, i) => {
        p.x += p.vx;
        p.y += p.vy;
        p.alpha -= 0.01;
        if (p.alpha <= 0) {
            particles.splice(i, 1);
            return;
        }
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = `${p.color}`;
        ctx.globalAlpha = p.alpha;
        ctx.fill();
    });
    ctx.globalAlpha = 1;
    requestAnimationFrame(animate);
}

canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    createParticles(e.clientX - rect.left, e.clientY - rect.top);
});

animate();