import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';

puppeteer.use(StealthPlugin());

async function run() {
  const setId = '31160'; // Race Plane
  console.log(`Testing product scrape for Set ${setId}...`);
  
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  // Set headers and user agent
  await page.setExtraHTTPHeaders({
    'Accept-Language': 'en-US,en;q=0.9',
  });
  
  await page.goto(`https://www.lego.com/en-us/product/-${setId}`, { waitUntil: 'networkidle2' });
  
  const productInfo = await page.evaluate(() => {
    // There's typically a main title h1
    const titleEl = document.querySelector('h1 span');
    const title = titleEl ? titleEl.innerText : null;

    // Piece count might be inside a span with text like '171' and label 'Pieces' nearby
    // Let's try to extract from script tags if possible, or common classes
    const scriptTags = Array.from(document.querySelectorAll('script[type="application/ld+json"]'));
    let pieces = null;
    let price = null;
    let age = null;
    let img = null;
    
    for (const tag of scriptTags) {
      try {
        const data = JSON.parse(tag.innerText);
        if (data['@type'] === 'Product') {
          // Sometimes price is here
          if (data.offers && data.offers.price) {
            price = `$${data.offers.price}`;
          }
          if (data.image) {
            img = Array.isArray(data.image) ? data.image[0] : data.image;
          }
        }
      } catch (e) {}
    }

    // Attempt to extract from the DOM natively if ld+json fails
    const listItems = Array.from(document.querySelectorAll('li, div, span'));
    for (const el of listItems) {
      const text = el.innerText || '';
      if (text.includes('Pieces') && /\d+/.test(text)) {
        const match = text.match(/(\d+)\s*Pieces/i);
        if (match) pieces = parseInt(match[1], 10);
      }
      if (text.includes('Ages') && /\d+\+/.test(text)) {
        const match = text.match(/(\d+\+)/);
        if (match) age = match[1];
      }
    }

    return { title, pieces, price, age, img };
  });

  console.log('Extracted Info:', productInfo);
  await browser.close();
}

run().catch(console.error);
