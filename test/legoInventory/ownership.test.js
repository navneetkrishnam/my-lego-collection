import assert from 'node:assert/strict';
import test from 'node:test';
import fs from 'fs';
import { ownedSetsPath } from '../../scripts/legoInventory/lib/paths.js';
import { parseOwnedSetsCsv, readOwnedSets, summarizeOwnedSets } from '../../scripts/legoInventory/lib/ownership.js';

test('canonical owned sets file contains all 111 unique sets and 112 physical boxes', () => {
  const sets = readOwnedSets(ownedSetsPath);
  const summary = summarizeOwnedSets(sets);

  assert.equal(summary.uniqueSetCount, 111);
  assert.equal(summary.physicalBoxCount, 112);
  assert.deepEqual(summary.multiQuantitySets, [{ setNumber: '30719', quantityOwned: 2 }]);
});

test('canonical owned sets file keeps set order stable', () => {
  const lines = fs.readFileSync(ownedSetsPath, 'utf8').trim().split(/\r?\n/);

  assert.equal(lines[0], 'set_number,quantity_owned');
  assert.equal(lines[1], '30719,2');
  assert.equal(lines.at(-2), '10369,1');
  assert.equal(lines.at(-1), '10362,1');
});

test('owned sets parser rejects malformed set numbers', () => {
  assert.throws(
    () => parseOwnedSetsCsv('set_number,quantity_owned\nabc,1\n'),
    /invalid set number/
  );
});

test('owned sets parser rejects duplicate set numbers', () => {
  assert.throws(
    () => parseOwnedSetsCsv('set_number,quantity_owned\n31160,1\n31160,1\n'),
    /duplicate set number/
  );
});

test('owned sets parser rejects non-positive quantities', () => {
  assert.throws(
    () => parseOwnedSetsCsv('set_number,quantity_owned\n31160,0\n'),
    /at least 1/
  );
});
