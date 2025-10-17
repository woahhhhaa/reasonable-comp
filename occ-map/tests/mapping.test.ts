import { describe, it, expect } from 'vitest';
import { generateMapping } from '../src/index.ts';

const buckets = [
  { id: 'devops', label: 'DevOps/SRE', notes: 'CI/CD, IaC' },
  { id: 'grc', label: 'Security (GRC)', notes: 'SOC2, audit' },
  { id: 'ops', label: 'Operations', notes: 'office mgmt' },
];

describe('mapping heuristics', () => {
  const map = generateMapping(buckets as any, '2025-10-17');
  it('DevOps/SRE includes 15-1252 with >=0.5 weight', () => {
    const b = map.buckets.find(b => b.id === 'devops')!;
    const sd = b.soc_codes.find(s => s.soc === '15-1252');
    expect(sd && sd.weight >= 0.5).toBe(true);
  });
  it('Security (GRC) includes 13-1041 or splits with 15-1212', () => {
    const b = map.buckets.find(b => b.id === 'grc')!;
    const c = b.soc_codes.map(s => s.soc);
    expect(c.includes('13-1041') || (c.includes('13-1041') && c.includes('15-1212'))).toBe(true);
  });
  it('Operations picks 11-3012 over 11-1021 for office mgmt', () => {
    const b = map.buckets.find(b => b.id === 'ops')!;
    const c = b.soc_codes[0].soc;
    expect(c).toBe('11-3012');
  });
});
