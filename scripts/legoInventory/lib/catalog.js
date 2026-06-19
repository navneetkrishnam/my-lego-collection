import fs from 'fs';

export function readAppSets(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

export function validateOwnedSetsAgainstCatalog(ownedSets, appSets) {
  const catalogIds = new Set(appSets.map((set) => String(set.id)));
  const missingFromCatalog = ownedSets
    .map((set) => set.setNumber)
    .filter((setNumber) => !catalogIds.has(setNumber));

  return {
    missingFromCatalog
  };
}
