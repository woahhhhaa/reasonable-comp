export function resolveAmbiguous(bucketLabel: string, notes?: string): Array<{soc:string;hint:string}> {
  const label = bucketLabel.toLowerCase();
  const out: Array<{soc:string;hint:string}> = [];
  if (label.includes('product')) {
    out.push({ soc: '11-2021', hint: 'market/strategy positioning' });
    out.push({ soc: '13-1082', hint: 'delivery/coordination' });
  }
  if (label.includes('devops') || label.includes('sre')) {
    out.push({ soc: '15-1252', hint: 'coding emphasis' });
    out.push({ soc: '15-1244', hint: 'ops/infrastructure emphasis' });
  }
  if (label.includes('security') || (notes||'').toLowerCase().includes('grc')) {
    out.push({ soc: '15-1212', hint: 'technical security' });
    out.push({ soc: '13-1041', hint: 'compliance/audit' });
  }
  if (label.includes('success')) {
    out.push({ soc: '41-3091', hint: 'account mgmt/renewals' });
  }
  if (label.includes('support')) {
    out.push({ soc: '43-4051', hint: 'customer support' });
  }
  if (label.includes('operations') || label.includes('ops')) {
    out.push({ soc: '11-1021', hint: 'broad ops mgmt' });
  }
  if (label.includes('admin') || (notes||'').toLowerCase().includes('office mgmt')) {
    out.push({ soc: '11-3012', hint: 'office/admin services' });
  }
  return out;
}
