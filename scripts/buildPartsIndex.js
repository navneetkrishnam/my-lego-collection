import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PARTS_DIR = path.resolve(__dirname, '../public/data/parts');
const INDEX_FILE = path.resolve(__dirname, '../public/data/parts-index.json');

async function buildPartsIndex() {
  console.log('Building global parts index...');
  
  if (!fs.existsSync(PARTS_DIR)) {
    console.error(`Parts directory not found: ${PARTS_DIR}`);
    return;
  }

  const files = fs.readdirSync(PARTS_DIR).filter(f => f.endsWith('.json'));
  console.log(`Found ${files.length} part files.`);

  const partsMap = new Map();

  for (const file of files) {
    const setId = file.replace('.json', '');
    const filePath = path.join(PARTS_DIR, file);
    
    try {
      const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
      
      for (const part of data) {
        if (!partsMap.has(part.id)) {
          partsMap.set(part.id, {
            id: part.id,
            name: part.name,
            imageUrl: part.imageUrl,
            sets: []
          });
        }
        
        const existingPart = partsMap.get(part.id);
        if (!existingPart.sets.includes(setId)) {
          existingPart.sets.push(setId);
        }
      }
    } catch (err) {
      console.error(`Failed to process ${file}:`, err);
    }
  }

  // Convert Map to an Array for easier frontend consumption
  const partsArray = Array.from(partsMap.values());
  
  // Sort by number of sets they appear in (descending) so most common parts are first
  partsArray.sort((a, b) => b.sets.length - a.sets.length);

  fs.writeFileSync(INDEX_FILE, JSON.stringify(partsArray, null, 2));
  console.log(`Successfully built parts index with ${partsArray.length} unique parts.`);
}

buildPartsIndex();
