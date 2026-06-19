import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export const repoRoot = path.resolve(__dirname, '../../..');
export const dataDir = path.join(repoRoot, 'data');
export const publicDataDir = path.join(repoRoot, 'public', 'data');
export const inventoryDir = path.join(dataDir, 'inventory');
export const pdfCacheDir = path.join(dataDir, 'pdfs');
export const ownedSetsPath = path.join(dataDir, 'owned-sets.csv');
export const inventoryConfigPath = path.join(inventoryDir, 'config.json');
export const appSetsPath = path.join(publicDataDir, 'sets.json');
export const partsCsvPath = path.join(publicDataDir, 'parts.csv');
