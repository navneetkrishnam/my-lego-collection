import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import fs from 'fs';
import path from 'path';

puppeteer.use(StealthPlugin());

async function scrapeSet(browser, setId) {
  const partsDir = path.join(process.cwd(), 'public', 'data', 'parts');
  if (!fs.existsSync(partsDir)) {
    fs.mkdirSync(partsDir, { recursive: true });
  }

  const outPath = path.join(partsDir, `${setId}.json`);
  if (fs.existsSync(outPath)) {
    console.log(`Skipping Set ${setId}, already scraped.`);
    return;
  }

  console.log(`Starting scrape for Set ${setId}...`);
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  try {
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

  // Pagination loop (Continue)
  let hasMore = true;
  while (hasMore) {
    // Scroll down to trigger lazy loading of images
    await page.evaluate(async () => {
      await new Promise((resolve) => {
        let totalHeight = 0;
        const distance = 500;
        const timer = setInterval(() => {
          const scrollHeight = document.body.scrollHeight;
          window.scrollBy(0, distance);
          totalHeight += distance;

          if (totalHeight >= scrollHeight - window.innerHeight) {
            clearInterval(timer);
            resolve();
          }
        }, 100);
      });
    });

    hasMore = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const btn = buttons.find(b => b.innerText.includes('Continue'));
      if (btn && !btn.disabled) {
        btn.click();
        return true;
      }
      return false;
    });
    if (hasMore) {
      console.log('Clicked Continue, waiting...');
      await new Promise(r => setTimeout(r, 4000));
    }
  }

  // Final scroll to ensure the last page's images load
  await page.evaluate(async () => {
    await new Promise((resolve) => {
      let totalHeight = 0;
      const distance = 500;
      const timer = setInterval(() => {
        const scrollHeight = document.body.scrollHeight;
        window.scrollBy(0, distance);
        totalHeight += distance;
        if (totalHeight >= scrollHeight - window.innerHeight) {
          clearInterval(timer);
          resolve();
        }
      }, 100);
    });
  });

  // Extract parts
  const parts = await page.evaluate(() => {
    // Find all 'Select this piece' buttons to reliably locate part containers
    const buttons = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.includes('Select this piece'));
    return buttons.map(btn => {
      const container = btn.closest('li') || btn.parentElement.parentElement.parentElement;
      const img = container.querySelector('img');
      const src = img ? img.src : '';
      
      const highResSrc = src.split('?')[0]; 
      const idMatch = highResSrc.match(/\/(\d+)\.(jpg|png)/);
      const id = idMatch ? idMatch[1] : null;
      
      const lines = container.innerText.split('\n').map(s => s.trim()).filter(s => s.length > 0 && s !== 'Select this piece');
      
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
      rawText: p.text
    };
  });

  fs.writeFileSync(outPath, JSON.stringify(formattedParts, null, 2));
  console.log(`Saved parts data to ${outPath}`);
  } catch (err) {
    console.error(`Error scraping ${setId}:`, err.message);
  } finally {
    await page.close();
  }
}

async function run() {
  const setsPath = path.join(process.cwd(), 'public', 'data', 'sets.json');
  if (!fs.existsSync(setsPath)) {
    console.error('sets.json not found!');
    return;
  }

  const sets = JSON.parse(fs.readFileSync(setsPath, 'utf-8'));
  console.log(`Found ${sets.length} sets. Launching browser...`);

  const browser = await puppeteer.launch({ headless: 'new' });

  for (const set of sets) {
    await scrapeSet(browser, set.id);
    // Random delay between 3 and 7 seconds to avoid rate limiting
    const delay = Math.floor(Math.random() * 4000) + 3000;
    console.log(`Waiting ${delay}ms before next set...`);
    await new Promise(r => setTimeout(r, delay));
  }

  console.log('Finished scraping all sets!');
  await browser.close();
}

run().catch(console.error);
