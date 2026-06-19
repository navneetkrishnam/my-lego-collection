#!/usr/bin/env node
import fs from 'fs';
import process from 'node:process';
import {
  appSetsPath,
  inventoryConfigPath,
  ownedSetsPath
} from './lib/paths.js';
import { readAppSets, validateOwnedSetsAgainstCatalog } from './lib/catalog.js';
import { readOwnedSets, summarizeOwnedSets } from './lib/ownership.js';

function parseArgs(argv) {
  const [command = 'help', ...rest] = argv;
  const options = {};

  for (let index = 0; index < rest.length; index += 1) {
    const arg = rest[index];
    if (!arg.startsWith('--')) {
      throw new Error(`Unexpected argument "${arg}".`);
    }

    const name = arg.slice(2);
    if (name === 'force') {
      options.force = true;
      continue;
    }

    const value = rest[index + 1];
    if (!value || value.startsWith('--')) {
      throw new Error(`Missing value for --${name}.`);
    }

    options[name] = value;
    index += 1;
  }

  return { command, options };
}

function loadValidatedInputs(options = {}) {
  const setsPath = options.sets || ownedSetsPath;
  const ownedSets = readOwnedSets(setsPath);
  const appSets = readAppSets(appSetsPath);
  const catalogValidation = validateOwnedSetsAgainstCatalog(ownedSets, appSets);

  if (catalogValidation.missingFromCatalog.length > 0) {
    throw new Error(
      `Owned sets missing from app catalog: ${catalogValidation.missingFromCatalog.join(', ')}`
    );
  }

  if (!fs.existsSync(inventoryConfigPath)) {
    throw new Error(`Inventory config not found: ${inventoryConfigPath}`);
  }

  return {
    setsPath,
    ownedSets,
    summary: summarizeOwnedSets(ownedSets),
    config: JSON.parse(fs.readFileSync(inventoryConfigPath, 'utf8'))
  };
}

function selectRunSets(ownedSets, options) {
  if (!options.set) {
    return ownedSets;
  }

  const selected = ownedSets.filter((set) => set.setNumber === options.set);
  if (selected.length === 0) {
    throw new Error(`Set ${options.set} is not present in the canonical owned-set list.`);
  }

  return selected;
}

function printSummary(label, inputs, selectedSets = inputs.ownedSets) {
  console.log(label);
  console.log(`Canonical sets file: ${inputs.setsPath}`);
  console.log(`Config version: ${inputs.config.configVersion}`);
  console.log(`Parser version: ${inputs.config.parserVersion}`);
  console.log(`Unique owned sets: ${inputs.summary.uniqueSetCount}`);
  console.log(`Physical boxes owned: ${inputs.summary.physicalBoxCount}`);
  console.log(`Selected sets: ${selectedSets.map((set) => set.setNumber).join(', ')}`);

  if (inputs.summary.multiQuantitySets.length > 0) {
    const values = inputs.summary.multiQuantitySets
      .map((set) => `${set.setNumber} x${set.quantityOwned}`)
      .join(', ');
    console.log(`Multi-quantity sets: ${values}`);
  }
}

function printHelp() {
  console.log(`Usage:
  npm run inventory -- run --sets data/owned-sets.csv
  npm run inventory -- run --set 31160
  npm run inventory -- validate
  npm run inventory -- review
  npm run inventory -- combine

Phase 1 validates canonical ownership/configuration only. PDF resolution and extraction come next.`);
}

function runCommand(command, options) {
  if (command === 'help' || command === '--help' || command === '-h') {
    printHelp();
    return;
  }

  if (command === 'run') {
    const inputs = loadValidatedInputs(options);
    const selectedSets = selectRunSets(inputs.ownedSets, options);
    printSummary('Inventory run input validation passed.', inputs, selectedSets);
    console.log('PDF resolution/extraction is not implemented in Phase 1.');
    return;
  }

  if (command === 'validate') {
    const inputs = loadValidatedInputs(options);
    printSummary('Inventory input validation passed.', inputs);
    return;
  }

  if (command === 'review' || command === 'combine') {
    loadValidatedInputs(options);
    console.log(`${command} is not implemented in Phase 1.`);
    return;
  }

  throw new Error(`Unknown command "${command}".`);
}

try {
  const { command, options } = parseArgs(process.argv.slice(2));
  runCommand(command, options);
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
