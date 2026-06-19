import fs from 'fs';

const OWNED_SETS_HEADER = 'set_number,quantity_owned';
const SET_NUMBER_RE = /^\d{5}$/;

export function parseOwnedSetsCsv(csvText) {
  const lines = csvText
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  if (lines.length === 0) {
    throw new Error('Owned sets CSV is empty.');
  }

  if (lines[0] !== OWNED_SETS_HEADER) {
    throw new Error(`Owned sets CSV must start with "${OWNED_SETS_HEADER}".`);
  }

  const seen = new Set();
  const sets = [];

  for (let index = 1; index < lines.length; index += 1) {
    const lineNumber = index + 1;
    const columns = lines[index].split(',');

    if (columns.length !== 2) {
      throw new Error(`Line ${lineNumber}: expected 2 columns, found ${columns.length}.`);
    }

    const [setNumber, quantityText] = columns.map((value) => value.trim());

    if (!SET_NUMBER_RE.test(setNumber)) {
      throw new Error(`Line ${lineNumber}: invalid set number "${setNumber}".`);
    }

    if (seen.has(setNumber)) {
      throw new Error(`Line ${lineNumber}: duplicate set number "${setNumber}".`);
    }

    if (!/^\d+$/.test(quantityText)) {
      throw new Error(`Line ${lineNumber}: quantity_owned must be a positive integer.`);
    }

    const quantityOwned = Number.parseInt(quantityText, 10);
    if (quantityOwned < 1) {
      throw new Error(`Line ${lineNumber}: quantity_owned must be at least 1.`);
    }

    seen.add(setNumber);
    sets.push({ setNumber, quantityOwned });
  }

  return sets;
}

export function readOwnedSets(filePath) {
  return parseOwnedSetsCsv(fs.readFileSync(filePath, 'utf8'));
}

export function summarizeOwnedSets(sets) {
  return {
    uniqueSetCount: sets.length,
    physicalBoxCount: sets.reduce((total, set) => total + set.quantityOwned, 0),
    multiQuantitySets: sets.filter((set) => set.quantityOwned > 1)
  };
}
