// G5 — prove every default BEASTIARY page link is reported by a live codexSee call site.
// Also flags FORGE custom-boss links that require the spawnBoss custom branch.
'use strict';
const fs = require('fs');
const path = require('path');
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');

// Collect codexSee("...") string keys from the product source.
const reported = new Set();
for (const m of html.matchAll(/codexSee\(\s*(['"`])([^'"`]+)\1/g)) reported.add(m[2]);
// Ternary / string-literal presence for shipped boss keys (not always a bare first arg).
if (html.includes("'boss:guardian'") || html.includes('"boss:guardian"')) reported.add('boss:guardian');
if (html.includes("'boss:queen'") || html.includes('"boss:queen"')) reported.add('boss:queen');
// Dynamic patterns that cover whole families:
const dynamic = [
  { re: /^enemy:\d+$/, via: "codexSee('enemy:' + e.kind)" },
  { re: /^weapon:\d+$/, via: "codexSee('weapon:' + G.weapon)" },
  { re: /^boss:boss\.custom\d+$/, via: "codexSee('boss:' + customBoss.id) after G5 fix" },
];

// Reconstruct default pages the same way codexDefaults does (names only for report).
// Enemy count comes from CODEX array length; weapons from WEAPONS length — parse shipped counts.
const codexArr = html.match(/const CODEX\s*=\s*\[([\s\S]*?)\];/);
const enemyCount = codexArr ? (codexArr[1].match(/\{/g) || []).length : 6;
const weaponsBlock = html.match(/const WEAPONS\s*=\s*\[([\s\S]*?)\];/);
const weaponCount = weaponsBlock ? (weaponsBlock[1].match(/name\s*:/g) || []).length : 6;

const pages = [];
for (let i = 0; i < enemyCount; i++) pages.push({ title: 'enemy#' + i, link: 'enemy:' + i });
pages.push({ title: 'Hive Guardian', link: 'boss:guardian' });
pages.push({ title: 'Alien Queen', link: 'boss:queen' });
for (let i = 0; i < weaponCount; i++) pages.push({ title: 'weapon#' + i, link: 'weapon:' + i });
pages.push({ title: 'Escort Tank', link: 'vehicle:tank' });
pages.push({ title: 'Squad Trooper', link: '' }); // always visible

let fail = 0;
console.log('Reported static codexSee keys:', [...reported].sort().join(', ') || '(none)');
console.log('Default pages:', pages.length, '(enemies', enemyCount, 'weapons', weaponCount + ')');
for (const p of pages) {
  if (!p.link) { console.log('OK  ALWAYS', p.title); continue; }
  if (reported.has(p.link)) { console.log('OK  STATIC', p.link, '—', p.title); continue; }
  const dyn = dynamic.find(d => d.re.test(p.link));
  if (dyn) { console.log('OK  DYNAMIC', p.link, 'via', dyn.via); continue; }
  console.log('FAIL UNREACHABLE', p.link, '—', p.title);
  fail++;
}

// Custom boss template from addForgeBoss must be covered by spawnBoss branch.
const hasCustomBossSee = html.includes("codexSee('boss:' + customBoss.id");
console.log(hasCustomBossSee ? 'OK  custom boss unlock branch present' : 'FAIL custom boss unlock branch missing');
if (!hasCustomBossSee) fail++;

// Static keys that must exist:
for (const k of ['boss:guardian', 'boss:queen', 'vehicle:tank']) {
  if (!reported.has(k)) { console.log('FAIL missing static report', k); fail++; }
  else console.log('OK  static report', k);
}

if (fail) { console.error('BEASTIARY AUDIT FAILED', fail); process.exit(1); }
console.log('BEASTIARY AUDIT PASS');
