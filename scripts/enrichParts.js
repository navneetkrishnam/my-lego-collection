import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import fs from 'fs';
import path from 'path';

puppeteer.use(StealthPlugin());

const INDEX_PATH = path.join(process.cwd(), 'public', 'data', 'parts-index.json');
const CACHE_PATH = path.join(process.cwd(), 'public', 'data', 'parts-enrichment-cache.json');

const USER_AGENTS = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
];

async function scrapeVariant(page, id) {
  // Set random User-Agent
  const randomUA = USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
  await page.setUserAgent(randomUA);

  try {
    await page.goto(`https://www.lego.com/en-us/pick-and-build/pick-a-brick?query=${id}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
  } catch (err) {
    console.log(`[${id}] Timeout on load.`);
    return null; // Might be a block or timeout, let it retry later
  }

  // Wait precisely for the button instead of hard sleep
  let clicked = false;
  try {
    await page.waitForSelector('[data-test="pab-item-button"]', { timeout: 8000 });
    clicked = await page.evaluate(() => {
      const btn = document.querySelector('[data-test="pab-item-button"]');
      if (btn) {
        btn.click();
        return true;
      }
      return false;
    });
  } catch (err) {
    // Button never appeared
  }

  if (!clicked) {
    return null;
  }

  // Wait precisely for the modal instead of hard sleep
  try {
    await page.waitForSelector('[role="dialog"], [data-test="pab-item-color-select"]', { timeout: 8000 });
    // Add a tiny buffer for images to render
    await new Promise(r => setTimeout(r, 500));
  } catch (err) {
    return null;
  }

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
        let src = img.src.split('?')[0];
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
  
  // Parse concurrency from args, default to 3
  const concurrencyArg = args.find(a => a.startsWith('--concurrency='));
  const CONCURRENCY = concurrencyArg ? parseInt(concurrencyArg.split('=')[1]) : 3;

  const browser = await puppeteer.launch({ headless: 'new' });
  
  // Prepare flat list of variants to process
  const pendingVariants = [];
  for (const shape of partsIndex) {
    for (const variant of shape.variants) {
      if (!cache[variant.id]) {
        pendingVariants.push(variant.id);
      }
    }
  }
  
  console.log(`Found ${pendingVariants.length} pending pieces. Starting with ${CONCURRENCY} concurrent workers...`);

  // Spin up pages with resource blocking
  const pages = [];
  for(let i=0; i < Math.min(CONCURRENCY, pendingVariants.length, limit); i++) {
    const p = await browser.newPage();
    await p.setViewport({ width: 1280 + Math.floor(Math.random()*100), height: 800 + Math.floor(Math.random()*100) });
    
    // Intercept and block unnecessary resources to save CPU/RAM
    await p.setRequestInterception(true);
    p.on('request', (req) => {
      const type = req.resourceType();
      if (['stylesheet', 'font', 'media'].includes(type) || req.url().includes('tracking') || req.url().includes('analytics')) {
        req.abort();
      } else {
        req.continue();
      }
    });
    
    pages.push(p);
  }

  let processedCount = 0;
  let index = 0;

  async function worker(page, workerId) {
    while (index < pendingVariants.length && processedCount < limit) {
      const variantId = pendingVariants[index++];
      if (!variantId) break;

      try {
        const enriched = await scrapeVariant(page, variantId);
        if (enriched) {
          cache[variantId] = enriched;
          fs.writeFileSync(CACHE_PATH, JSON.stringify(cache, null, 2));
          console.log(`[Worker ${workerId}] [${variantId}] Saved ${enriched.alternateImages.length} images, Color: ${enriched.colorName}`);
        } else {
          cache[variantId] = { colorName: null, alternateImages: [] };
          fs.writeFileSync(CACHE_PATH, JSON.stringify(cache, null, 2));
          console.log(`[Worker ${workerId}] [${variantId}] Marked as not found.`);
        }
      } catch (err) {
        console.error(`[Worker ${workerId}] [${variantId}] Error: ${err.message}`);
      }

      processedCount++;
      // Micro-delay to avoid slamming immediately, much faster than 3-6s
      const delay = Math.floor(Math.random() * 1000) + 500;
      await new Promise(r => setTimeout(r, delay));
    }
  }

  await Promise.all(pages.map((p, i) => worker(p, i + 1)));

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
