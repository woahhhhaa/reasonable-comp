import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import AjvImport from 'ajv';
import addFormatsImport from 'ajv-formats';
const addFormats: any = (addFormatsImport as any).default || addFormatsImport;
const AjvCtor: any = (AjvImport as any).default || AjvImport;
const ajv: any = new AjvCtor({ allErrors: true });
addFormats(ajv);

export function loadSchema() {
  const fp = path.resolve(process.cwd(), 'schema/soc_map.schema.json');
  const schema = JSON.parse(fs.readFileSync(fp, 'utf-8'));
  return schema;
}

export function loadValidCodes(): { pattern: RegExp; codes: Set<string>; retired: Set<string> } {
  const fp = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../data/SOC_VALID_CODES.json');
  const js = JSON.parse(fs.readFileSync(fp, 'utf-8'));
  return { pattern: new RegExp(js.code_pattern), codes: new Set(js.valid_codes), retired: new Set(js.retired_or_unsupported_codes) };
}

export function validateSocMap(obj: any): { ok: boolean; errors: string[] } {
  const schema = loadSchema();
  const v = ajv.compile(schema);
  const errors: string[] = [];
  const ok = v(obj) as boolean;
  if (!ok && v.errors) {
    errors.push(...v.errors.map((e: any) => `${e.instancePath} ${e.message}`));
  }
  const { pattern, codes, retired } = loadValidCodes();
  if (!Array.isArray(obj.buckets)) {
    errors.push('buckets must be an array');
  } else {
    if (obj.buckets.length < 15 || obj.buckets.length > 25) {
      errors.push('buckets length must be between 15 and 25');
    }
    for (const b of obj.buckets) {
      let sum = 0;
      for (const s of b.soc_codes) {
        if (!pattern.test(s.soc)) errors.push(`invalid SOC format: ${s.soc}`);
        if (!codes.has(s.soc)) errors.push(`SOC not in valid_codes: ${s.soc}`);
        if (retired.has(s.soc)) errors.push(`SOC retired/unsupported: ${s.soc}`);
        sum += s.weight;
      }
      if (Math.abs(1 - sum) > 1e-9) errors.push(`weights must sum to 1.0 for bucket ${b.id}`);
    }
  }
  return { ok: errors.length === 0, errors };
}
