import fs from 'fs';
import path from 'path';

const INDEX_PATH = path.join(process.cwd(), 'public', 'data', 'parts-index.json');
const CSV_PATH = path.join(process.cwd(), 'public', 'data', 'parts.csv');

function exportCsv() {
  if (!fs.existsSync(INDEX_PATH)) {
    console.error('parts-index.json not found.');
    return;
  }

  const partsIndex = JSON.parse(fs.readFileSync(INDEX_PATH, 'utf-8'));
  
  // Create CSV header
  let csvContent = 'part_number,color,part_name\n';
  
  let count = 0;
  for (const shape of partsIndex) {
    // Escape quotes in part name for CSV
    let partName = shape.name || '';
    if (partName.includes('"') || partName.includes(',')) {
      partName = `"${partName.replace(/"/g, '""')}"`;
    }
    
    for (const variant of shape.variants) {
      if (variant.id === null) continue; // Skip corrupted null IDs
      
      const partNumber = variant.id;
      const color = variant.colorName || 'Not Found';
      
      csvContent += `${partNumber},${color},${partName}\n`;
      count++;
    }
  }

  fs.writeFileSync(CSV_PATH, csvContent, 'utf-8');
  console.log(`Successfully exported ${count} parts to public/data/parts.csv`);
}

exportCsv();
