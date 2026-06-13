import puppeteer from 'puppeteer';

async function run() {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    let hasErrors = false;

    page.on('pageerror', err => {
        console.error('Page error:', err);
        hasErrors = true;
    });

    page.on('console', msg => {
        if (msg.type() === 'error') {
            console.error('Console error:', msg.text());
            hasErrors = true;
        }
    });

    try {
        console.log("Loading http://localhost:5174/set/31209 ...");
        await page.goto('http://localhost:5174/set/31209', { waitUntil: 'networkidle0' });
        
        // Wait briefly to allow React to mount
        await new Promise(r => setTimeout(r, 2000));
        
        if (hasErrors) {
            console.log("RUNTIME ERRORS DETECTED.");
        } else {
            console.log("PAGE LOADED SUCCESSFULLY WITH NO ERRORS.");
        }
    } catch (e) {
        console.error("Failed to load page:", e.message);
    } finally {
        await browser.close();
    }
}

run();
