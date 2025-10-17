import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { scoreCandidates, pickCodes } from './rules/rubric.js';
import { validateSocMap } from './rules/validate.js';

export interface Bucket { id: string; label: string; notes?: string; }
export interface SocChoice { soc: string; weight: number; reason: string; }
export interface SocMap {
  version: string;
  source: 'O*NET 30.0 Database';
  attribution: {
    text_verbatim: string;
    license: 'CC BY 4.0';
    url: string;
    trademark_notice: string;
  };
  buckets: Array<{ id:string; label:string; soc_codes: SocChoice[]; notes: string; }>;
}

function loadAttribution(): string {
  const fp = path.resolve(path.dirname(fileURLToPath(import.meta.url)), './data/ONET_ATTRIBUTION.md');
  const text = fs.readFileSync(fp, 'utf-8').replace(/\n/g, ' ').trim();
  return text;
}

export function generateMapping(buckets: Bucket[], asOf: string): SocMap {
  const mapped = buckets.map(b => {
    const scored = scoreCandidates(b.label, b.notes);
    const picked = pickCodes(scored);
    return { id: b.id, label: b.label, soc_codes: picked.codes, notes: b.notes || '' };
  });
  const map: SocMap = {
    version: asOf,
    source: 'O*NET 30.0 Database',
    attribution: {
      text_verbatim: loadAttribution(),
      license: 'CC BY 4.0',
      url: 'https://www.onetcenter.org/license_db.html',
      trademark_notice: 'O*NET® is a trademark of USDOL/ETA.'
    },
    buckets: mapped
  };
  return map;
}

export function validateMapping(map: SocMap): {ok: boolean; errors: string[]} {
  return validateSocMap(map);
}
