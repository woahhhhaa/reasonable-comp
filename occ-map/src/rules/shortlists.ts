import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export interface ShortlistEntry { bucket: string; candidates: { soc: string; title: string }[] }

export function loadShortlists(): ShortlistEntry[] {
  const fp = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../data/SHORTLISTS.json');
  const raw = fs.readFileSync(fp, 'utf-8');
  const js = JSON.parse(raw);
  return js.shortlists as ShortlistEntry[];
}

export function shortlistFor(bucketLabel: string): { soc: string; title: string }[] | null {
  const list = loadShortlists();
  const found = list.find(s => s.bucket.toLowerCase() === bucketLabel.toLowerCase());
  return found ? found.candidates : null;
}
