import puppeteer from 'puppeteer';

async function run() {
    const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
    const page = await browser.newPage();
    await page.goto('https://www.lego.com/en-us/search?q=60488', { waitUntil: 'networkidle2' });
    const html = await page.content();
    console.log(html.substring(0, 1000));
    console.log('... HTML truncated');
    
    const pageTitle = await page.title();
    console.log('Title:', pageTitle);
    
    await browser.close();
}

run();
