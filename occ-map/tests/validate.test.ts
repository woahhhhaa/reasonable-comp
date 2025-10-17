import { describe, it, expect } from 'vitest';
import { validateMapping } from '../src/index.ts';

const base = {
  version: '2025-10-17',
  source: 'O*NET 30.0 Database' as const,
  attribution: {
    text_verbatim: 'This product includes information from the O*NET 30.0 Database by the U.S. Department of Labor, Employment and Training Administration (USDOL/ETA). Used under the CC BY 4.0 license. O*NET® is a trademark of USDOL/ETA.',
    license: 'CC BY 4.0' as const,
    url: 'https://www.onetcenter.org/license_db.html',
    trademark_notice: 'O*NET® is a trademark of USDOL/ETA.'
  },
};

describe('validation', () => {
  it('fails on invalid weights and codes', () => {
    const obj: any = {
      ...base,
      buckets: [
        {
          id: 'x', label: 'Sales',
          soc_codes: [ { soc: '41-3091', weight: 0.7, reason: 'ok' }, { soc: '41-4011', weight: 0.4, reason: 'bad sum' } ],
          notes: ''
        }
      ]
    };
    const v = validateMapping(obj as any);
    expect(v.ok).toBe(false);
    expect(v.errors.some(e => e.includes('weights must sum'))).toBe(true);
  });
});
