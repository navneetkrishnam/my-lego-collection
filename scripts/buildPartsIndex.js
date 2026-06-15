import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PARTS_DIR = path.resolve(__dirname, '../public/data/parts');
const INDEX_FILE = path.resolve(__dirname, '../public/data/parts-index.json');

async function buildPartsIndex() {
  console.log('Building grouped global parts index...');
  
  if (!fs.existsSync(PARTS_DIR)) {
    console.error(`Parts directory not found: ${PARTS_DIR}`);
    return;
  }

  const files = fs.readdirSync(PARTS_DIR).filter(f => f.endsWith('.json'));
  console.log(`Found ${files.length} part files.`);

  // Group by exact piece name (shape/mold)
  const nameMap = new Map();

  for (const file of files) {
    const setId = file.replace('.json', '');
    const filePath = path.join(PARTS_DIR, file);
    
    try {
      const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
      
      for (const part of data) {
        if (!nameMap.has(part.name)) {
          nameMap.set(part.name, {
            name: part.name,
            variants: []
          });
        }
        
        const shapeGroup = nameMap.get(part.name);
        
        // Find if this exact color/id variant already exists for this shape
        let variant = shapeGroup.variants.find(v => v.id === part.id);
        if (!variant) {
          variant = {
            id: part.id,
            imageUrl: part.imageUrl,
            sets: []
          };
          shapeGroup.variants.push(variant);
        }
        
        if (!variant.sets.includes(setId)) {
          variant.sets.push(setId);
        }
      }
    } catch (err) {
      console.error(`Failed to process ${file}:`, err);
    }
  }

  // Convert Map to an Array for frontend
  const partsArray = Array.from(nameMap.values());
  
  // Calculate totalSetsCount and totalQuantity of variants for sorting
  for (const group of partsArray) {
    const uniqueSets = new Set();
    for (const variant of group.variants) {
      for (const setId of variant.sets) {
        uniqueSets.add(setId);
      }
    }
    group.totalSetsCount = uniqueSets.size;
  }
  
  // Sort by number of unique sets they appear in (most common shapes first)
  partsArray.sort((a, b) => b.totalSetsCount - a.totalSetsCount);

  fs.writeFileSync(INDEX_FILE, JSON.stringify(partsArray, null, 2));
  console.log(`Successfully built grouped parts index with ${partsArray.length} unique shapes.`);
}

buildPartsIndex();
