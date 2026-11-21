'use strict';
/*
 * Combined Build, Part A stream 4: reproducible-builder proof.
 * The canonical layout is the four module sources BESIDE the
 * builder (identity.js, ledger.js, capture.js, migration.js,
 * build-stage1-bundle.js in one directory). This check copies
 * exactly those five files into a clean directory, rebuilds
 * there, and requires the produced stage1core.js to be
 * byte-identical (SHA-256) to the tree's shipped bundle.
 * Run: node tests-stage1/rebuild-verify.js ; exit 0 = pass.
 */

const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const { createHash } = require('node:crypto');

const tree = path.join(__dirname, '..');
const FILES = ['identity.js', 'ledger.js', 'capture.js', 'migration.js', 'build-stage1-bundle.js'];
const sha = (p) => createHash('sha256').update(fs.readFileSync(p)).digest('hex');

let failures = 0;
for (const f of FILES) {
  if (!fs.existsSync(path.join(tree, f))) { console.log('FAIL  canonical layout: ' + f + ' missing beside the builder'); failures += 1; }
}
if (!failures) console.log('PASS  canonical layout: all four sources beside the builder');

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'pb-rebuild-'));
try {
  for (const f of FILES) fs.copyFileSync(path.join(tree, f), path.join(tmp, f));
  execFileSync(process.execPath, [path.join(tmp, 'build-stage1-bundle.js')], { stdio: 'pipe' });
  const rebuilt = sha(path.join(tmp, 'stage1core.js'));
  const shipped = sha(path.join(tree, 'stage1core.js'));
  if (rebuilt === shipped) {
    console.log('PASS  clean-room rebuild is byte-identical to the shipped bundle (sha256 ' + shipped.slice(0, 16) + '…)');
  } else {
    console.log('FAIL  clean-room rebuild differs: rebuilt ' + rebuilt + ' vs shipped ' + shipped);
    failures += 1;
  }
} finally {
  fs.rmSync(tmp, { recursive: true, force: true });
}
console.log('\nrebuild-verify: ' + (failures ? 'FAILED' : 'PASSED'));
process.exit(failures ? 1 : 0);
