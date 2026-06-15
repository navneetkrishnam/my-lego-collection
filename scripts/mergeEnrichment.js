import fs from 'fs';
import path from 'path';

const INDEX_PATH = path.join(process.cwd(), 'public', 'data', 'parts-index.json');
const CACHE_PATH = path.join(process.cwd(), 'public', 'data', 'parts-enrichment-cache.json');

function merge() {
  if (!fs.existsSync(INDEX_PATH)) {
    console.error('parts-index.json not found.');
    return;
  }

  if (!fs.existsSync(CACHE_PATH)) {
    console.error('parts-enrichment-cache.json not found. Nothing to merge.');
    return;
  }

  const partsIndex = JSON.parse(fs.readFileSync(INDEX_PATH, 'utf-8'));
  const cache = JSON.parse(fs.readFileSync(CACHE_PATH, 'utf-8'));

  let updatedCount = 0;
  for (const shape of partsIndex) {
    for (const variant of shape.variants) {
      if (cache[variant.id]) {
        variant.colorName = cache[variant.id].colorName || variant.colorName || null;
        variant.alternateImages = cache[variant.id].alternateImages || [];
        updatedCount++;
      }
    }
  }

  fs.writeFileSync(INDEX_PATH, JSON.stringify(partsIndex, null, 2));
  console.log(`Successfully merged ${updatedCount} cached entries into parts-index.json!`);
}

merge();
