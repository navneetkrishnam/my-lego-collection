import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import fs from 'fs';
import path from 'path';

puppeteer.use(StealthPlugin());

const INDEX_PATH = path.join(process.cwd(), 'public', 'data', 'parts-index.json');
const CACHE_PATH = path.join(process.cwd(), 'public', 'data', 'parts-enrichment-cache.json');

async function scrapeVariant(page, id) {
  console.log(`[${id}] Navigating to PAB...`);
  await page.goto(`https://www.lego.com/en-us/pick-and-build/pick-a-brick?query=${id}`, { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 4000));

  const clicked = await page.evaluate(() => {
    const btn = document.querySelector('[data-test="pab-item-button"]');
    if (btn) {
      btn.click();
      return true;
    }
    return false;
  });

  if (!clicked) {
    console.log(`[${id}] Could not find part button.`);
    return null;
  }

  await new Promise(r => setTimeout(r, 3000));

  const data = await page.evaluate(async () => {
    let colorName = null;
    const colorSelect = document.querySelector('[data-test="pab-item-color-select"], select');
    if (colorSelect && colorSelect.options && colorSelect.selectedIndex >= 0) {
      colorName = colorSelect.options[colorSelect.selectedIndex].text.trim();
    } else {
       const spans = Array.from(document.querySelectorAll('span, p, div'));
       const colorLabel = spans.find(s => s.innerText && s.innerText.trim() === 'Color');
       if (colorLabel && colorLabel.nextElementSibling) {
          colorName = colorLabel.nextElementSibling.innerText.trim();
       }
    }

    const allImages = new Set();
    const collectImages = () => {
      const imgs = Array.from(document.querySelectorAll('img[src*="element.img"]'));
      imgs.forEach(img => {
        // extract base url without sizing params if possible, or keep as is.
        // removing .192x192 if it exists to get original resolution
        let src = img.src.split('?')[0].replace(/\.\d+x\d+/, '');
        allImages.add(src);
      });
    };

    collectImages();

    // try to click carousel next
    let attempts = 0;
    while (attempts < 5) {
      let nextBtn = document.querySelector('button[aria-label="Next image"], button[aria-label="Next"]');
      if (!nextBtn) {
        const dialogButtons = Array.from(document.querySelectorAll('[role="dialog"] button'));
        nextBtn = dialogButtons.find(b => {
          const svg = b.querySelector('svg');
          return svg && (svg.innerHTML.includes('right') || b.className.includes('next'));
        });
      }

      if (nextBtn && !nextBtn.disabled) {
        nextBtn.click();
        await new Promise(r => setTimeout(r, 800));
        collectImages();
        attempts++;
      } else {
        break;
      }
    }

    return { colorName, alternateImages: [...allImages] };
  });

  return data;
}

async function run() {
  if (!fs.existsSync(INDEX_PATH)) {
    console.error('parts-index.json not found. Run index builder first.');
    return;
  }

  const partsIndex = JSON.parse(fs.readFileSync(INDEX_PATH, 'utf-8'));
  let cache = {};
  if (fs.existsSync(CACHE_PATH)) {
    cache = JSON.parse(fs.readFileSync(CACHE_PATH, 'utf-8'));
    console.log(`Loaded ${Object.keys(cache).length} entries from cache.`);
  }

  // Get args
  const args = process.argv.slice(2);
  const testMode = args.includes('--test');
  const limit = testMode ? 5 : Infinity;

  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  let processedCount = 0;

  for (const shape of partsIndex) {
    for (const variant of shape.variants) {
      if (processedCount >= limit) break;

      if (cache[variant.id]) {
        console.log(`[${variant.id}] Skipping, already in cache.`);
        continue;
      }

      try {
        const enriched = await scrapeVariant(page, variant.id);
        if (enriched) {
          cache[variant.id] = enriched;
          fs.writeFileSync(CACHE_PATH, JSON.stringify(cache, null, 2));
          console.log(`[${variant.id}] Saved ${enriched.alternateImages.length} images, Color: ${enriched.colorName}`);
        } else {
          // save an empty entry to avoid retrying failed ones constantly
          cache[variant.id] = { colorName: null, alternateImages: [] };
          fs.writeFileSync(CACHE_PATH, JSON.stringify(cache, null, 2));
        }
      } catch (err) {
        console.error(`[${variant.id}] Error: ${err.message}`);
      }

      processedCount++;
      // Sleep to prevent rate limit
      const delay = Math.floor(Math.random() * 3000) + 3000;
      await new Promise(r => setTimeout(r, delay));
    }
    if (processedCount >= limit) break;
  }

  await browser.close();

  // Finally, merge cache into parts-index.json
  console.log('Merging cache into parts-index.json...');
  for (const shape of partsIndex) {
    for (const variant of shape.variants) {
      if (cache[variant.id]) {
        variant.colorName = cache[variant.id].colorName || variant.colorName || null;
        variant.alternateImages = cache[variant.id].alternateImages || [];
      }
    }
  }

  fs.writeFileSync(INDEX_PATH, JSON.stringify(partsIndex, null, 2));
  console.log('Done! Run `npm run dev` to see changes.');
}

run().catch(console.error);
