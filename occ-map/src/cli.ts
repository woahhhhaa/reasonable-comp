#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { generateMapping, validateMapping, Bucket } from './index.js';
import YAML from 'yaml';

function parseArgs(argv: string[]) {
  const args = argv.slice(2);
  const cmd = args[0];
  const opts: Record<string,string> = {};
  for (let i=1; i<args.length; i+=2) {
    const k = args[i]; const v = args[i+1];
    if (k && v && k.startsWith('--')) opts[k.slice(2)] = v;
  }
  return { cmd, opts };
}

function readBuckets(p: string): Bucket[] {
  const raw = fs.readFileSync(p, 'utf-8');
  if (p.endsWith('.yaml') || p.endsWith('.yml')) return YAML.parse(raw);
  return JSON.parse(raw);
}

const { cmd, opts } = parseArgs(process.argv);

if (cmd === 'generate') {
  const inp = opts['in']; const outp = opts['out']; const date = opts['date'];
  const src = opts['source'];
  if (!inp || !outp || !date || src !== 'O*NET 30.0 Database') {
    console.error('usage: occ-map generate --in <path> --out <path> --source "O*NET 30.0 Database" --date <YYYY-MM-DD>');
    process.exit(2);
  }
  const buckets = readBuckets(inp);
  const map = generateMapping(buckets, date);
  const v = validateMapping(map);
  if (!v.ok) {
    console.error('Validation failed:', v.errors.join('\n'));
    process.exit(1);
  }
  fs.writeFileSync(outp, JSON.stringify(map, null, 2));
  console.log(`Wrote ${outp}`);
  process.exit(0);
}

if (cmd === 'validate') {
  const inp = opts['in'];
  if (!inp) { console.error('usage: occ-map validate --in <soc_map.json>'); process.exit(2); }
  const obj = JSON.parse(fs.readFileSync(inp, 'utf-8'));
  const v = validateMapping(obj);
  if (!v.ok) { console.error('Validation failed:', v.errors.join('\n')); process.exit(1); }
  console.log('OK');
  process.exit(0);
}

console.error('Unknown command. Commands: generate, validate');
process.exit(2);
