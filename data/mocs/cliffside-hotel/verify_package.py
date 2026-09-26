"""Cross-check exported placements, exact donors, render inputs and determinism."""
from pathlib import Path
from collections import Counter
import contextlib,hashlib,io,json
from model import author,export
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 files=['model.json','bom.json','allocation.json','cliffside-hotel.ldr'];before={f:sha(H/f) for f in files};snapshot=json.loads((H/'inventory-snapshot.json').read_text())
 with contextlib.redirect_stdout(io.StringIO()):export(author(snapshot))
 after={f:sha(H/f) for f in files};assert before==after,'Non-deterministic export'
 m=json.loads((H/'model.json').read_text());bom=json.loads((H/'bom.json').read_text());alloc=json.loads((H/'allocation.json').read_text())
 counts=Counter(q['element'] for q in m['pieces']);assert counts=={r['element']:r['required'] for r in bom};assert len({q['key'] for q in m['pieces']})==len(m['pieces'])
 allocated=Counter();donors=Counter()
 for r in alloc:allocated[r['element']]+=r['quantity'];donors[r['element'],r['set'],r['copy']]+=r['quantity']
 assert allocated==counts
 for (e,s,c),n in donors.items():
  assert c<=snapshot['owned_sets'][s]
  allowed=next(r['quantity'] for r in snapshot['parts'][e]['sources'] if r['set']==s and r['copy']==c)
  assert n<=allowed
 text=(H/'cliffside-hotel.ldr').read_text();assert sum(line.startswith('1 ') for line in text.splitlines())==len(m['pieces'])
 assert text.count('0 STEP')+1==len(m['steps'])
 for name in ['preview.render.json','preview-rear.render.json']:
  r=json.loads((H/name).read_text());assert r['input_sha256']==sha(H/'cliffside-hotel.ldr'),name+' is stale'
 v=json.loads((H/'verification.json').read_text());g=json.loads((H/'geometry-verification.json').read_text())
 assert v['digital_checks_pass'] and not g['bounds_errors'] and not g['strict_surface_crossings']
 assert v['model_sha256']==g['model_sha256']==sha(H/'model.json'),'Stale verification report'
 r=dict(deterministic_exports=True,export_sha256=after,source_sha256={p.name:sha(p) for p in sorted(H.glob('*.py'))},piece_count=len(m['pieces']),exact_elements=len(counts),donor_sets=len({r['set'] for r in alloc}),donor_allocation_rows=len(alloc),stage_count=len(m['steps']),bom_matches_placements=True,allocations_match_bom=True,no_donor_overallocation=True,render_inputs_match=True)
 (H/'reproducibility.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in r.items() if 'sha256' not in k},indent=2))
if __name__=='__main__':verify()
