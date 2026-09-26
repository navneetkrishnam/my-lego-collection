"""Actual LDraw bounds and strict mesh crossing probe for special connections.
Coplanar contact and fully contained volumes are outside the triangle probe.
"""
import sys,json,hashlib,numpy as np
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'fern-and-steam-v2'))
from render_model import Library
sys.path.insert(0,str(H))
from audit import ports,world

def intersections(a,b):
 points=[]
 for k in range(3):
  orig=a[:,k];direction=a[:,(k+1)%3]-orig;e1=b[:,1]-b[:,0];e2=b[:,2]-b[:,0]
  h=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,h);valid=abs(det)>1e-8
  f=np.divide(1,det,out=np.zeros_like(det),where=valid);s=orig-b[:,0];u=f*np.einsum('ij,ij->i',s,h)
  q=np.cross(s,e1);v=f*np.einsum('ij,ij->i',direction,q);t=f*np.einsum('ij,ij->i',e2,q)
  keep=valid&(u>1e-6)&(v>1e-6)&(u+v<1-1e-6)&(t>1e-6)&(t<1-1e-6)
  points.extend(orig[keep]+t[keep,None]*direction[keep])
 return points

def intended_fit(points,a,b,spec):
 points=np.array(points);inside=np.zeros(len(points),dtype=bool)
 for top,bottom in [(a,b),(b,a)]:
  normal=np.array(top['matrix']).reshape(3,3)@np.array([0,-1,0])
  for site in ports(top,spec[top['element']],True)&ports(bottom,spec[bottom['element']],False):
   delta=points-np.array(site);axial=delta@normal;radial=np.linalg.norm(delta-axial[:,None]*normal,axis=1)
   inside|=(axial>=-.01)&(axial<=4.01)&(radial<=6.01)
 if inside.all():return 'stud engagement envelope'
 for clip,bar in [(a,b),(b,a)]:
  if clip.get('hinge_parent')!=bar['key']:continue
  pivot=np.array(world(bar,[0,2,-20]));axis=np.array(bar['matrix']).reshape(3,3)@np.array([1,0,0]);delta=points-pivot;along=delta@axis;radial=np.linalg.norm(delta-along[:,None]*axis,axis=1)
  if np.all((abs(along)<=14.01)&(radial<=4.01)):return 'bar within clip grip envelope'
 return None

def run():
 lib=Library(Path('/Applications/Studio 2.0/ldraw'),H.parent/'fern-and-steam-v2/ldraw')
 pieces=json.loads((H/'model.json').read_text())['pieces'];spec=json.loads((H/'inventory-snapshot.json').read_text())['parts'];meshes=[];errors=[]
 for p in pieces:
  t=np.concatenate(list(lib.part(spec[p['element']]['ldraw']).values()))@np.array(p['matrix']).reshape(3,3).T+p['origin']
  lo=t.min((0,1));hi=t.max((0,1));meshes.append((t,t.min(1),t.max(1),lo,hi))
  if p['kind']=='insert' or p.get('pose_type'):continue
  if abs(hi[1]+p['z']*8)>.01:errors.append([p['key'],'bottom',float(hi[1]),-p['z']*8])
  if p['kind'] in ['brick','plate','tile','frame','arch','arch_wide','rock_cap','rock','panel','round','slope']:
   actual=[lo[0],hi[0],lo[2],hi[2]];expected=[p['x']*20,(p['x']+p['w'])*20,p['y']*20,(p['y']+p['d'])*20]
   if max(abs(a-b) for a,b in zip(actual,expected))>.01:errors.append([p['key'],'footprint',list(map(float,actual)),expected])
 lows=np.array([m[3] for m in meshes]);highs=np.array([m[4] for m in meshes]);pairs=set()
 for i,p in enumerate(pieces):
  if not p.get('pose_type') and p['kind'] not in ['leaf','flower','mug','insert','arch','arch_wide','rock_cap','rock','panel','railing','frame','hinge','slope','side_stud_brick']:continue
  for j in np.flatnonzero(np.all(np.minimum(highs[i],highs)-np.maximum(lows[i],lows)>.001,axis=1)):
   if i!=j:pairs.add(tuple(sorted((i,int(j)))))
 print('Mesh bounds errors',len(errors),'candidate pairs',len(pairs),flush=True)
 issues=[];fits=[]
 for count,(i,j) in enumerate(sorted(pairs)):
  a,al,ah,_,_=meshes[i];b,bl,bh,_,_=meshes[j];points=[]
  for start in range(0,len(a),64):
   overlap=np.all(np.minimum(ah[start:start+64,None,:],bh[None,:,:])-np.maximum(al[start:start+64,None,:],bl[None,:,:])>=-1e-7,axis=2)
   aa,bb=np.nonzero(overlap)
   if len(aa):points.extend(intersections(a[start+aa],b[bb]));points.extend(intersections(b[bb],a[start+aa]))
  if points:
   p,q=pieces[i],pieces[j];row=dict(a=p['key'],b=q['key'],elements=[p['element'],q['element']],kinds=[p['kind'],q['kind']],modules=[p['module'],q['module']],intersection_points=len(points));fit=intended_fit(points,p,q,spec)
   if fit:row['classification']=fit;fits.append(row)
   else:row['sample_points']=[list(map(float,pt)) for pt in points[:5]];issues.append(row)
  if count%200==199:print('Checked',count+1,'crossings',len(issues),flush=True)
 report=dict(bounds_errors=errors,candidate_pairs_checked=len(pairs),strict_surface_crossings=issues,expected_engagement_crossings=fits,scope='Actual recursively transformed LDraw meshes. Special parts and all tilted instances against neighboring geometry. Every classified contact point must lie inside a shared 6 LDU stud / 4 LDU bar engagement envelope. Coplanar contact and full containment excluded; not a complete solid collision solver.')
 report['model_sha256']=hashlib.sha256((H/'model.json').read_bytes()).hexdigest()
 (H/'geometry-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 return not errors and not issues
if __name__=='__main__':raise SystemExit(0 if run() else 1)
