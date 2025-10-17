import { shortlistFor } from './shortlists.js';
import { resolveAmbiguous } from './ambiguous.js';

export function scoreCandidates(bucketLabel: string, bucketNotes?: string, options?: { preferManagerial?: boolean }): Array<{soc:string; score:number; reason:string}> {
  const scores = new Map<string, { score: number; reason: string[] }>();
  const add = (soc: string, inc: number, why: string) => {
    const cur = scores.get(soc) || { score: 0, reason: [] };
    cur.score += inc; cur.reason.push(why); scores.set(soc, cur);
  };

  const shortlist = shortlistFor(bucketLabel) || [];
  shortlist.forEach(c => add(c.soc, 0.6, `shortlist: ${c.title}`));

  const notes = `${bucketLabel} ${bucketNotes||''}`.toLowerCase();
  const managerialTerms = /(head|lead|director|manager|vp|chief)/;
  const technicalTerms = /(code|dev|ci\/cd|iac|terraform|kubernetes|pipeline|build|deploy|tester|qa|automation)/;
  const networkTerms = /(network|infrastructure|systems admin|linux|windows server)/;
  const salesTerms = /(sales|renewal|account|quota|crm)/;
  const policyTerms = /(policy|compliance|audit|soc2|iso|grc)/;
  const officeMgmt = /(office mgmt|office management)/;
  const progProj = /(program|project)/;
  const softwareApp = /(software eng|software|app|application)/;
  const infra = /(infra|infrastructure|platform|systems)/;
  const designUx = /(design|ux|ui)/;
  const dataAnalytics = /(data|analytics|bi)/;
  const recruiting = /(recruit|talent|sourcing)/;
  const finance = /(finance|financial)/;

  if (managerialTerms.test(notes) || options?.preferManagerial) {
    ['11-2021','11-3121','11-3031','11-1021','11-3012'].forEach(s => add(s, 0.2, 'managerial cue'));
  }
  if (technicalTerms.test(notes)) {
    ['15-1252','15-1253'].forEach(s => add(s, 0.2, 'technical/coding cue'));
  }
  if (networkTerms.test(notes)) {
    ['15-1231','15-1244'].forEach(s => add(s, 0.2, 'network/infrastructure cue'));
  }
  if (salesTerms.test(notes)) {
    ['41-3091','41-4011'].forEach(s => add(s, 0.2, 'sales/account cue'));
  }
  if (policyTerms.test(notes)) {
    ['13-1041'].forEach(s => add(s, 0.2, 'policy/compliance cue'));
  }
  if (officeMgmt.test(notes)) { ['11-3012'].forEach(s => add(s, 0.2, 'office mgmt cue')); }

  resolveAmbiguous(bucketLabel, bucketNotes).forEach(h => add(h.soc, 0.15, `ambiguous cue: ${h.hint}`));

  if (progProj.test(notes)) add('13-1082', 0.3, 'program/project');
  if (softwareApp.test(notes)) add('15-1252', 0.3, 'software/app');
  if (infra.test(notes)) add('15-1244', 0.3, 'infrastructure');
  if (designUx.test(notes)) add('15-1255', 0.3, 'design/ux');
  if (dataAnalytics.test(notes)) add('15-2051', 0.3, 'data/analytics');
  if (recruiting.test(notes)) add('13-1071', 0.3, 'recruiting');
  if (finance.test(notes)) add('11-3031', 0.3, 'finance');

  const arr = Array.from(scores.entries()).map(([soc, v]) => ({ soc, score: v.score, reason: v.reason.join('; ') }));
  const max = arr.reduce((m, a) => Math.max(m, a.score), 0);
  return arr
    .map(a => ({ ...a, score: max > 0 ? +(a.score / max).toFixed(3) : 0 }))
    .sort((a,b) => b.score - a.score);
}

export function pickCodes(scored: Array<{soc:string; score:number; reason:string}>): {codes: Array<{soc:string; weight:number; reason:string}>} {
  const top = scored.slice(0, 2);
  if (top.length === 0) return { codes: [] };
  if (top.length === 1 || (top[0].score >= 0.6 && (top[1]?.score ?? 0) < 0.5)) {
    return { codes: [{ soc: top[0].soc, weight: 1.0, reason: top[0].reason }] };
  }
  if (top[0].score >= 0.5 && top[1].score >= 0.5 && Math.abs(top[0].score - top[1].score) <= 0.2) {
    const total = top[0].score + top[1].score;
    let w1 = Math.round((top[0].score / total) * 10) / 10;
    let w2 = +(1 - w1).toFixed(1);
    if (Math.abs(1 - (w1 + w2)) > 1e-9) { w2 = +(1 - w1).toFixed(1); }
    return { codes: [
      { soc: top[0].soc, weight: w1, reason: top[0].reason },
      { soc: top[1].soc, weight: w2, reason: top[1].reason }
    ]};
  }
  return { codes: [{ soc: top[0].soc, weight: 1.0, reason: top[0].reason }] };
}
