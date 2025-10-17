import fs from 'node:fs';
import { generateMapping } from '../src/index.js';
import YAML from 'yaml';

function main() {
  const args = process.argv.slice(2);
  const inIdx = args.indexOf('--in');
  const outIdx = args.indexOf('--out');
  const dateIdx = args.indexOf('--date');
  const sourceIdx = args.indexOf('--source');
  if (inIdx<0 || outIdx<0 || dateIdx<0 || sourceIdx<0) throw new Error('usage');
  const inp = args[inIdx+1];
  const outp = args[outIdx+1];
  const date = args[dateIdx+1];
  const buckets = (inp.endsWith('.yaml')||inp.endsWith('.yml')) ? YAML.parse(fs.readFileSync(inp,'utf-8')) : JSON.parse(fs.readFileSync(inp,'utf-8'));
  const map = generateMapping(buckets, date);
  fs.writeFileSync(outp, JSON.stringify(map, null, 2));
  console.log(`Wrote ${outp}`);
}

main();
