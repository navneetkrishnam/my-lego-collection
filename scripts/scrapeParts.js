import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import fs from 'fs';
import path from 'path';

puppeteer.use(StealthPlugin());

async function run() {
  const setId = '31160';
  console.log(`Starting scrape for Set ${setId}...`);
  
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  await page.setViewport({ width: 1280, height: 800 });

  console.log('Navigating...');
  await page.goto(`https://www.lego.com/en-in/service/replacement-parts/missing/${setId}/pieces`, { waitUntil: 'networkidle2' });
  
  await new Promise(r => setTimeout(r, 3000));

  // Find and click "See all available pieces"
  const clicked = await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    const btn = buttons.find(b => b.innerText.includes('See all available pieces'));
    if (btn) {
      btn.click();
      return true;
    }
    return false;
  });

  if (!clicked) {
    console.log('Could not find "See all available pieces" button. Exiting.');
    await browser.close();
    return;
  }

  console.log('Clicked to load pieces. Waiting...');
  await new Promise(r => setTimeout(r, 5000));

  // Pagination loop (Show more)
  let hasMore = true;
  while (hasMore) {
    hasMore = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const btn = buttons.find(b => b.innerText.includes('Show more'));
      if (btn && !btn.disabled) {
        btn.click();
        return true;
      }
      return false;
    });
    if (hasMore) {
      console.log('Clicked Show More, waiting...');
      await new Promise(r => setTimeout(r, 3000));
    }
  }

  // Extract parts
  const parts = await page.evaluate(() => {
    const imgs = Array.from(document.querySelectorAll('img[src*="element"]'));
    return imgs.map(img => {
      const container = img.closest('li') || img.parentElement.parentElement.parentElement;
      const src = img.src;
      // Convert src to high res by removing query params or changing width/height
      const highResSrc = src.split('?')[0]; 
      const idMatch = highResSrc.match(/\/(\d+)\.jpg/);
      const id = idMatch ? idMatch[1] : null;
      
      const lines = container.innerText.split('\n').map(s => s.trim()).filter(s => s.length > 0);
      
      return { id, src: highResSrc, text: container.innerText, lines };
    });
  });

  console.log(`Scraped ${parts.length} parts.`);

  // Ensure directory exists
  const partsDir = path.join(process.cwd(), 'public', 'data', 'parts');
  if (!fs.existsSync(partsDir)) {
    fs.mkdirSync(partsDir, { recursive: true });
  }

  // Format data
  const formattedParts = parts.map(p => {
    // lines might look like:
    // "Element 6556257"
    // "Out of stock"
    // "Design 2871"
    let name = "Unknown Part";
    if (p.lines.length >= 2) {
      name = p.lines[0]; // best guess
    }
    return {
      id: p.id,
      name: name,
      imageUrl: p.src,
      rawText: p.text // keep raw text to inspect
    };
  });

  fs.writeFileSync(path.join(partsDir, `${setId}.json`), JSON.stringify(formattedParts, null, 2));
  console.log(`Saved parts data to public/data/parts/${setId}.json`);

  await browser.close();
}

run().catch(console.error);
