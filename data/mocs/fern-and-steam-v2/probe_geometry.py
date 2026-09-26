"""Targeted actual-mesh probe. Strict edge/triangle crossings exclude coplanar contact.
This is not a full solid collision solver. Requires numpy and Studio LDraw data.
"""
import sys,json,numpy as np
from pathlib import Path
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H))
from render_model import Library
lib=Library(Path('/Applications/Studio 2.0/ldraw'),H/'ldraw');model=json.load(open(H/'model.json'));spec=json.load(open(H/'inventory-snapshot.json'))['parts']
meshes=[]
for p in model['pieces']:
 t=np.concatenate(list(lib.part(spec[p['element']]['ldraw']).values()))@np.array(p['matrix']).reshape(3,3).T+p['origin'];meshes.append((t,t.min(1),t.max(1),t.min((0,1)),t.max((0,1))))
def hit(a,b):
 # Test each edge of a against the strict interior of b; skip coplanar contact.
 for k in range(3):
  orig=a[:,k];direction=a[:,(k+1)%3]-orig;e1=b[:,1]-b[:,0];e2=b[:,2]-b[:,0];h=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,h);valid=abs(det)>1e-8
  f=np.divide(1,det,out=np.zeros_like(det),where=valid);s=orig-b[:,0];u=f*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);v=f*np.einsum('ij,ij->i',direction,q);t=f*np.einsum('ij,ij->i',e2,q)
  if np.any(valid&(u>1e-6)&(v>1e-6)&(u+v<1-1e-6)&(t>1e-6)&(t<1-1e-6)):return True
 return False
errors=[];checked=0
for p,m in zip(model['pieces'],meshes):
 if p['kind']=='insert':continue
 _,_,_,lo,hi=m
 if abs(hi[1]+p['z']*8)>.01:errors.append([p['key'],'bottom',float(hi[1]),-p['z']*8])
 if p['kind'] in ('box','frame','arch','small_arch','roof','round'):
  actual=[lo[0],hi[0],lo[2],hi[2]];expected=[p['x']*20,(p['x']+p['w'])*20,p['y']*20,(p['y']+p['d'])*20]
  if max(abs(a-b) for a,b in zip(actual,expected))>.01:errors.append([p['key'],'footprint',actual,expected])
 checked+=1
bounds_report={'checked_non_insert_instances':checked,'mesh_bottom_and_regular_footprint_errors':errors,'scope':'Recursively transformed actual LDraw triangle bounds; decorative horizontal bounds excluded.'}
(H/'geometry-verification.json').write_text(json.dumps(bounds_report,indent=2)+'\n')

issues=[];pairs=0
for i,p in enumerate(model['pieces']):
 if p['kind'] not in ('leaf','flower','fern','mug'):continue
 a,al,ah,alo,ahi=meshes[i]
 for j,q in enumerate(model['pieces']):
  if i==j or (q['kind'] in ('leaf','flower','fern','mug') and j<i):continue
  b,bl,bh,blo,bhi=meshes[j]
  if not np.all(np.minimum(ahi,bhi)-np.maximum(alo,blo)>.001):continue
  pairs+=1;found=False
  for start in range(0,len(a),64):
   overlap=np.all(np.minimum(ah[start:start+64,None,:],bh[None,:,:])-np.maximum(al[start:start+64,None,:],bl[None,:,:])>=-1e-7,axis=2)
   aa,bb=np.nonzero(overlap)
   if len(aa) and (hit(a[start+aa],b[bb]) or hit(b[bb],a[start+aa])):found=True;break
  if found:issues.append({'a':p['key'],'b':q['key'],'elements':[p['element'],q['element']],'kinds':[p['kind'],q['kind']]})
report={'candidate_pairs_checked':pairs,'strict_surface_crossings':issues,'scope':'Accessory edge/triangle crossing probe, excludes coplanar contact; not a full solid collision solver.'}
(H/'accessory-geometry-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if errors or issues: raise SystemExit(1)
