import fs from 'fs';
import path from 'path';
import { Buffer } from 'node:buffer';
import process from 'node:process';
import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';

puppeteer.use(StealthPlugin());

const SETS_JSON_PATH = path.join(process.cwd(), 'public', 'data', 'sets.json');
const OWNED_SETS_PATH = path.join(process.cwd(), 'data', 'owned-sets.csv');
const IMAGES_DIR = path.join(process.cwd(), 'public', 'images');
const PARTS_DIR = path.join(process.cwd(), 'public', 'data', 'parts');

const setIds = process.argv.slice(2);

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function parseNumber(text) {
  const value = Number.parseInt(String(text || '').replace(/\D/g, ''), 10);
  return Number.isFinite(value) ? value : 0;
}

async function wait(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

async function dismissCommonModals(page) {
  try {
    const ageGate = await page.$('[data-test="age-gate-grown-up-cta"]');
    if (ageGate) {
      await ageGate.click();
      await wait(1000);
    }
  } catch {
    // Modal markup changes frequently; failed dismissal is non-fatal.
  }

  try {
    const acceptButton = await page.$('button[data-test="cookie-accept-all"]');
    if (acceptButton) {
      await acceptButton.click();
      await wait(500);
    }
  } catch {
    // Cookie banner may not be present.
  }
}

async function downloadImage(url, destPath) {
  const response = await fetch(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0'
    }
  });

  if (!response.ok) {
    throw new Error(`Image download failed (${response.status}): ${url}`);
  }

  const bytes = Buffer.from(await response.arrayBuffer());
  fs.writeFileSync(destPath, bytes);
}

function normalizeImageUrl(url) {
  try {
    const parsed = new URL(url);
    parsed.search = '?width=800';
    return parsed.toString();
  } catch {
    return url;
  }
}

async function scrapeProduct(page, setId) {
  await page.goto(`https://www.lego.com/en-us/product/-${setId}`, {
    waitUntil: 'domcontentloaded',
    timeout: 60000
  });
  await dismissCommonModals(page);
  await wait(3000);

  return page.evaluate(() => {
    const textOf = (selector) => document.querySelector(selector)?.textContent?.trim() || null;
    const title = textOf('h1 span') || textOf('h1');
    const age = textOf('[data-test="ages-value"]') || textOf('[data-test="age-value"]') || null;
    const piecesText = textOf('[data-test="pieces-value"]');

    let theme = textOf('[data-test="breadcrumb-1"]');
    if (!theme) {
      theme = textOf('[data-test^="product-overview-category-"]');
    }

    let pieces = piecesText ? Number.parseInt(piecesText.replace(/\D/g, ''), 10) : 0;
    if (!pieces) {
      const detailText = Array.from(document.querySelectorAll('li, div, span'))
        .map((el) => el.textContent || '')
        .find((text) => /\d+\s*Pieces/i.test(text));
      const match = detailText?.match(/(\d+)\s*Pieces/i);
      pieces = match ? Number.parseInt(match[1], 10) : 0;
    }

    const images = Array.from(document.querySelectorAll('img'))
      .map((img) => img.src)
      .filter((src) => src && src.includes('lego.com') && src.includes('/assets/'))
      .filter((src, index, list) => list.indexOf(src) === index)
      .slice(0, 5);

    return {
      name: title,
      theme,
      age,
      pieces,
      images
    };
  });
}

async function scrapeParts(page, setId) {
  await page.goto(`https://www.lego.com/en-in/service/replacement-parts/missing/${setId}/pieces`, {
    waitUntil: 'domcontentloaded',
    timeout: 60000
  });
  await dismissCommonModals(page);
  await wait(3000);

  const clicked = await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    const button = buttons.find((item) => item.innerText.includes('See all available pieces'));
    if (!button) {
      return false;
    }
    button.click();
    return true;
  });

  if (!clicked) {
    return [];
  }

  await wait(5000);

  let hasMore = true;
  while (hasMore) {
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
      const button = buttons.find((item) => item.innerText.includes('Continue'));
      if (button && !button.disabled) {
        button.click();
        return true;
      }
      return false;
    });

    if (hasMore) {
      await wait(4000);
    }
  }

  return page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button')).filter((button) =>
      button.innerText.includes('Select this piece')
    );

    return buttons.map((button) => {
      const container = button.closest('li') || button.parentElement?.parentElement?.parentElement;
      const image = container?.querySelector('img');
      const src = image?.src?.split('?')[0] || '';
      const idMatch = src.match(/\/(\d+)\.(jpg|png)/);
      const id = idMatch ? idMatch[1] : null;
      const lines = (container?.innerText || '')
        .split('\n')
        .map((line) => line.trim())
        .filter((line) => line && line !== 'Select this piece');
      const name = lines[0] || 'Unknown Part';

      return {
        id,
        name,
        imageUrl: src,
        rawText: container?.innerText || ''
      };
    });
  });
}

function upsertOwnedSet(setId) {
  const lines = fs.readFileSync(OWNED_SETS_PATH, 'utf8').trimEnd().split(/\r?\n/);
  const exists = lines.slice(1).some((line) => line.split(',')[0] === setId);

  if (!exists) {
    lines.push(`${setId},1`);
    fs.writeFileSync(OWNED_SETS_PATH, `${lines.join('\n')}\n`, 'utf8');
  }
}

function upsertCollectionSet(setId, product, localImages) {
  const sets = JSON.parse(fs.readFileSync(SETS_JSON_PATH, 'utf8'));
  const existingIndex = sets.findIndex((set) => set.id === setId);
  const existing = existingIndex >= 0 ? sets[existingIndex] : {};
  const nextSet = {
    id: setId,
    name: product.name || existing.name || `Set ${setId}`,
    theme: product.theme || existing.theme || 'Unknown',
    age: product.age || existing.age || 'N/A',
    pieces: parseNumber(product.pieces || existing.pieces),
    thumbnail: localImages[0] || existing.thumbnail || '',
    images: localImages.length > 0 ? localImages : existing.images || [],
    status: existing.status || 'Not Started',
    history: existing.history || []
  };

  if (existingIndex >= 0) {
    sets[existingIndex] = nextSet;
  } else {
    sets.push(nextSet);
  }

  fs.writeFileSync(SETS_JSON_PATH, JSON.stringify(sets, null, 2));
}

async function processSet(browser, setId) {
  console.log(`Processing ${setId}...`);
  const productPage = await browser.newPage();
  await productPage.setViewport({ width: 1280, height: 900 });
  await productPage.setExtraHTTPHeaders({ 'Accept-Language': 'en-US,en;q=0.9' });

  const product = await scrapeProduct(productPage, setId);
  await productPage.close();

  if (!product.name || !product.pieces) {
    throw new Error(`Could not verify product details for ${setId}.`);
  }

  const imageDir = path.join(IMAGES_DIR, setId);
  ensureDir(imageDir);

  const localImages = [];
  for (const [index, imageUrl] of product.images.map(normalizeImageUrl).entries()) {
    const localPath = path.join(imageDir, `${index}.png`);
    await downloadImage(imageUrl, localPath);
    localImages.push(`/images/${setId}/${index}.png`);
  }

  const partsPage = await browser.newPage();
  await partsPage.setViewport({ width: 1280, height: 900 });
  await partsPage.setExtraHTTPHeaders({ 'Accept-Language': 'en-IN,en;q=0.9' });
  const parts = await scrapeParts(partsPage, setId);
  await partsPage.close();

  ensureDir(PARTS_DIR);
  fs.writeFileSync(path.join(PARTS_DIR, `${setId}.json`), JSON.stringify(parts, null, 2));

  upsertCollectionSet(setId, product, localImages);
  upsertOwnedSet(setId);

  console.log(
    `Added ${setId}: ${product.name}, ${product.theme}, ${product.age}, ${product.pieces} pieces, ${parts.length} replacement parts.`
  );
}

async function run() {
  if (setIds.length === 0) {
    throw new Error('Usage: node scripts/addSetsToCollection.js <set-id> [set-id...]');
  }

  ensureDir(IMAGES_DIR);
  ensureDir(PARTS_DIR);

  const browser = await puppeteer.launch({ headless: 'new' });
  try {
    for (const setId of setIds) {
      if (!/^\d{5}$/.test(setId)) {
        throw new Error(`Invalid set ID: ${setId}`);
      }
      await processSet(browser, setId);
    }
  } finally {
    await browser.close();
  }
}

run().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
