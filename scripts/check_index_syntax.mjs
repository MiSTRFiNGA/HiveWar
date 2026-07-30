/**
 * CI helper: extract inline <script> blocks (no src=) from index.html and parse with new Function().
 * Usage: node scripts/check_index_syntax.mjs [path/to/index.html]
 */
import fs from 'node:fs';
import path from 'node:path';

const file = path.resolve(process.argv[2] || 'index.html');
const html = fs.readFileSync(file, 'utf8');
const re = /<script\b([^>]*)>([\s\S]*?)<\/script>/gi;
let m;
let n = 0;
let failed = 0;
while ((m = re.exec(html)) !== null) {
  const attrs = m[1] || '';
  if (/\bsrc\s*=/i.test(attrs)) continue;
  const code = (m[2] || '').trim();
  if (!code) continue;
  n += 1;
  try {
    // Parse only — do not execute
    new Function(code);
    console.log(`OK  inline script #${n} (${code.length} chars)`);
  } catch (e) {
    failed += 1;
    console.error(`FAIL inline script #${n}: ${e.message}`);
  }
}
if (n === 0) {
  console.error('No inline <script> blocks found in', file);
  process.exit(2);
}
if (failed) {
  console.error(`${failed}/${n} script block(s) failed syntax check`);
  process.exit(1);
}
console.log(`All ${n} inline script block(s) parse OK`);
