import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';

puppeteer.use(StealthPlugin());

async function run() {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    
    await page.goto('https://www.lego.com/en-us/product/-31209', { waitUntil: 'networkidle2' });
    
    const elements = await page.evaluate(() => {
        const els = Array.from(document.querySelectorAll('[data-test]'));
        const testVals = els.map(el => {
            const dt = el.getAttribute('data-test');
            if (dt && (dt.includes('theme') || dt.includes('breadcrumb') || dt.includes('category'))) {
                return dt + ': ' + el.textContent.trim();
            }
            return null;
        }).filter(Boolean);
        return testVals;
    });
    
    console.log(elements);
    await browser.close();
}

run();
