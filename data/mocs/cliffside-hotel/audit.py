"""Inventory, ordinary bodies and geometric connector positions; no strength claim."""
from collections import Counter,defaultdict
from pathlib import Path
import json,math,hashlib
from engine import transform
H=Path(__file__).resolve().parent

def world(q,v):return tuple(round(a+b,5) for a,b in zip(transform(q['matrix'],v),q['origin']))
def ports(q,p,top):
 if p['kind']=='insert' or top and not p['studded']:return set()
 out=set();w,d=p['w'],p['d']
 for i in range(w):
  for j in range(d):
   yy=0 if top else 8*p['h']
   if p['kind']=='arch':
    if top and i in (0,w-1):yy=24
    if not top and i not in (0,w-1):continue
   if p['kind']=='slope' and top and j!=d-1:continue
   off=p.get('origin_offset',[0,0,0])
   out.add(world(q,[20*(i+.5-w/2)-off[0],yy-off[1],20*(j+.5-d/2)-off[2]]))
 return out

def inspect(pieces,snapshot):
 spec=snapshot['parts'];used=Counter(q['element'] for q in pieces)
 errors={k:[] for k in ['shortages','duplicates','ordinary_body_overlaps','invalid_inserts','invalid_hinges','invalid_transforms']}
 for e,n in used.items():
  if n>spec[e]['minimum']:errors['shortages'].append([e,n,spec[e]['minimum']])
 bykey={q['key']:q for q in pieces};graph={q['key']:set() for q in pieces};tops=defaultdict(set);bottoms=defaultdict(set);seen={};voxels={}
 def link(a,b):graph[a].add(b);graph[b].add(a)
 for q in pieces:
  p=spec[q['element']];key=q['key'];pose=(q['element'],tuple(q['origin']),tuple(q['matrix']))
  r=q['matrix']
  if len(r)!=9 or any(not math.isfinite(v) for v in r+q['origin']) or any(abs(sum(r[3*k+i]*r[3*k+j] for k in range(3))-(1 if i==j else 0))>1e-6 for i in range(3) for j in range(3)):errors['invalid_transforms'].append(key)
  if pose in seen:errors['duplicates'].append([seen[pose],key])
  seen[pose]=key
  if p['kind']=='insert':
   parent=bykey.get(q.get('parent'));expected={'60616':('60596',[-32,0,5]),'60603':('60594',[0,8,4]),'42509':('42205',[0,4.5,5])}.get(p['bl_part'])
   if not parent or not expected or spec[parent['element']]['bl_part']!=expected[0] or q.get('offset')!=expected[1] or world(parent,expected[1])!=tuple(round(v,5) for v in q['origin']) or q['matrix']!=parent['matrix']:errors['invalid_inserts'].append(key)
   else:link(key,parent['key'])
   continue
  for pt in ports(q,p,True):tops[pt].add(key)
  for pt in ports(q,p,False):bottoms[pt].add(key)
  if 'hinge_parent' in q:
   parent=bykey[q['hinge_parent']]
   if max(abs(a-b) for a,b in zip(world(q,[0,2,-20]),world(parent,[0,2,-20])))>1e-4:errors['invalid_hinges'].append(key)
   else:link(key,parent['key'])
  if 'mount_parent' in q:
   parent=bykey[q['mount_parent']]
   a=world(parent,[0,10,-10]);b=world(q,[10,8,0])
   if max(abs(x-y) for x,y in zip(a,b))>1e-4:errors['invalid_inserts'].append(key)
   else:link(key,parent['key'])
  # Pitched panels are checked in their own assembly coordinate system.
  if p['kind'] in ['brick','plate','tile','side_stud_brick'] and q.get('pose_type')!='facade_inlay':
   space=q.get('panel','world');x,y,z=q['x'],q['y'],q['z']
   for a in range(x,x+q['w']):
    for b in range(y,y+q['d']):
     for c in range(z,z+q['h']):
      loc=space,a,b,c
      if loc in voxels:errors['ordinary_body_overlaps'].append([voxels[loc],key])
      voxels[loc]=key
 for pt in tops.keys() & bottoms.keys():
  for a in tops[pt]:
   for b in bottoms[pt]:
    if a!=b:link(a,b)
 errors['ordinary_body_overlaps']=sorted(set(tuple(v) for v in errors['ordinary_body_overlaps']))
 remaining=set(graph);components=[]
 while remaining:
  todo=[min(remaining)];component=[]
  while todo:
   key=todo.pop()
   if key not in remaining:continue
   remaining.remove(key);component.append(key);todo.extend(graph[key]&remaining)
  components.append(sorted(component))
 result=dict(piece_count=len(pieces),exact_elements=len(used),**errors,connected_components=len(components),isolated_components=sorted(components,key=len)[:-1],inventory_pass=not errors['shortages'],digital_checks_pass=not any(errors.values()) and len(components)==1,limitations=['Ordinary body occupancy covers axis-aligned parts and each roof plane separately; pitched-to-building crossings need mesh checks.','Stud/bar/clip positions establish connectivity, not clutch strength, rigidity or construction access.','Physical build not tested.'])
 return result

if __name__=='__main__':
 r=inspect(json.loads((H/'model.json').read_text())['pieces'],json.loads((H/'inventory-snapshot.json').read_text()));r['model_sha256']=hashlib.sha256((H/'model.json').read_bytes()).hexdigest();(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps({k:v for k,v in r.items() if k!='isolated_components'},indent=2));print('Isolated sizes',[len(c) for c in r['isolated_components']])
 raise SystemExit(0 if r['digital_checks_pass'] else 1)
