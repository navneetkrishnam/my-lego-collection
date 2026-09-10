import fs from 'fs';
import path from 'path';
import { execFileSync } from 'child_process';
import process from 'node:process';

const SETS_JSON_PATH = path.join(process.cwd(), 'public', 'data', 'sets.json');
const IMAGES_DIR = path.join(process.cwd(), 'public', 'images');

export function convertToWebpThumbnail(inputPngPath, outputWebpPath, width = 400, quality = 80) {
  execFileSync('cwebp', [
    '-q', String(quality),
    '-resize', String(width), '0',
    inputPngPath,
    '-o', outputWebpPath
  ], { stdio: 'pipe' });
}

function run() {
  if (!fs.existsSync(SETS_JSON_PATH)) {
    throw new Error(`Sets file not found at ${SETS_JSON_PATH}`);
  }

  const sets = JSON.parse(fs.readFileSync(SETS_JSON_PATH, 'utf8'));
  console.log(`Starting thumbnail generation for ${sets.length} sets...`);

  let totalOriginalBytes = 0;
  let totalWebpBytes = 0;
  let convertedCount = 0;
  let skippedCount = 0;

  for (const set of sets) {
    const setId = String(set.id);
    const setDir = path.join(IMAGES_DIR, setId);
    const inputPng = path.join(setDir, '0.png');
    const outputWebp = path.join(setDir, 'thumb.webp');

    if (!fs.existsSync(inputPng)) {
      console.warn(`[WARN] 0.png not found for set ${setId}. Skipping.`);
      skippedCount += 1;
      continue;
    }

    const originalStats = fs.statSync(inputPng);
    totalOriginalBytes += originalStats.size;

    try {
      convertToWebpThumbnail(inputPng, outputWebp, 400, 80);
      const webpStats = fs.statSync(outputWebp);
      totalWebpBytes += webpStats.size;
      convertedCount += 1;

      // Update catalog entry
      set.thumbnail = `/images/${setId}/thumb.webp`;
    } catch (err) {
      console.error(`[ERROR] Failed converting set ${setId}: ${err.message}`);
    }
  }

  // Write updated sets.json
  fs.writeFileSync(SETS_JSON_PATH, JSON.stringify(sets, null, 2), 'utf8');

  const origMB = (totalOriginalBytes / (1024 * 1024)).toFixed(2);
  const newMB = (totalWebpBytes / (1024 * 1024)).toFixed(2);
  const savedPercent = (((totalOriginalBytes - totalWebpBytes) / totalOriginalBytes) * 100).toFixed(1);

  console.log('\n--- Thumbnail Generation Complete ---');
  console.log(`Successfully converted : ${convertedCount} sets`);
  if (skippedCount > 0) {
    console.log(`Skipped sets           : ${skippedCount}`);
  }
  console.log(`Original total size    : ${origMB} MB`);
  console.log(`Optimized WebP size    : ${newMB} MB`);
  console.log(`Total data saved       : ${(origMB - newMB).toFixed(2)} MB (${savedPercent}% reduction)`);
}

// Allow running directly as CLI script
if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname)) {
  run();
}
