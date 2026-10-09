const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const ts = require("typescript");

function load(relativePath) {
  const source = fs.readFileSync(path.join(__dirname, "..", relativePath), "utf8");
  const code = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
  }).outputText;
  const context = { exports: {}, process: { env: {} } };
  vm.runInNewContext(code, context);
  return context.exports;
}

const { simulateMaterial } = load("src/lib/simulation.ts");
const { MODE_A_MATERIALS } = load("src/lib/api.ts");
const resin = MODE_A_MATERIALS[0];
const onTime = simulateMaterial(resin, 0);
const delayed = simulateMaterial(resin, 4);

assert.equal(onTime.firstReceipt, 8);
assert.equal(onTime.gap, 0);
assert.equal(delayed.arrival, 12);
assert.equal(delayed.gap, 4);
assert.equal(delayed.stockout, 9);
assert.equal(delayed.stress.find(p => p.day === 9).balance, -100);
assert.equal(delayed.stress.find(p => p.day === 12).balance, 600);
assert.equal(onTime.base.find(p => p.day === 8).balance, 1000);
assert.equal(delayed.base.find(p => p.day === 8).balance, 1000);
assert.notEqual(delayed.stress.find(p => p.day === 8).balance, onTime.stress.find(p => p.day === 8).balance);

// A clamped zero balance must not manufacture daily replenishment.
const film = simulateMaterial(MODE_A_MATERIALS[1], 4);
assert.equal(film.firstReceipt, 10);
assert.equal(film.arrival, 14);
assert.equal(film.stockout, 11);
assert.equal(film.stress.find(p => p.day === 30).balance, -50);

// At the maximum delay, the scheduled receipt moves to day 22.
const worst = simulateMaterial(resin, 14);
assert.equal(worst.arrival, 22);
assert.equal(worst.gap, 14);
assert.equal(worst.stockout, 9);

// With no supplied receipt, there is no invented arrival or supply-gap value.
const noReceipt = simulateMaterial({ ...resin, trajectory_base: [] }, 4);
assert.equal(noReceipt.arrival, null);
assert.equal(noReceipt.gap, null);
assert.equal(noReceipt.stockout, 9);
console.log("Inventory scenarios passed: arrival shifts, stockout, recovery, clamped balances, and missing receipts.");
