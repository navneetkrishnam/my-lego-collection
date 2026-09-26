"""Flood-fill the authored floor plates through actual door gaps (0.5-stud grid)."""
from collections import deque
import json
from pathlib import Path
import numpy as np
import layout as l
HERE=Path(__file__).resolve().parent
STEP=.5
xs=np.arange(STEP/2,l.BASE[0],STEP)
ys=np.arange(STEP/2,l.BASE[1],STEP)
X,Y=np.meshgrid(xs,ys,indexing='ij')

def rect(r):
 x,y,w,d=r;return (X>x)&(X<x+w)&(Y>y)&(Y<y+d)

def run():
 masks={}
 for z in sorted({f['z'] for f in l.FLOORS}):
  selected=[f for f in l.FLOORS if f['z']==z]
  m=np.zeros_like(X,dtype=bool)
  for f in selected:
   area=np.zeros_like(m)
   for r in f['rects']+[b['rect'] for b in f['balconies']]:area|=rect(r)
   for h in f['holes']:area&=~rect(h)
   m|=area
  for f in selected:
   for w in f['walls']:
    along=X if w['axis']=='x' else Y;cross=Y if w['axis']=='x' else X
    blocked=(along>=w['a'])&(along<=w['b'])&(np.abs(cross-w['c'])<=w['thickness']/2)
    for o in w['opens']:
     if o['kind']=='door':
      assert o['w']>=3
      blocked&=~((along>o['a'])&(along<o['a']+o['w']))
    m&=~blocked
   for item in f['furniture']:m&=~rect(item['rect'])
  # Pergola posts are structural footprint obstacles at courtyard level.
  if z==40:
   for x,y,w,d in [(5,24,12,12),(84,36,10,8)]:
    for xx in (x,x+w-1):
     for yy in (y,y+d-1):m&=~rect((xx,yy,1,1))
  masks[z]=m
 def cell(x,y,z):return (z,int(x/STEP),int(y/STEP))
 vertical={}
 for x,y,levels in [(51,24,[40,54,68]),(120,54,[12,26,40])]:
  for a,b in zip(levels,levels[1:]):
   aa,bb=cell(x,y,a),cell(x,y,b)
   vertical.setdefault(aa,[]).append(bb);vertical.setdefault(bb,[]).append(aa)
 start=cell(51,55,40)
 assert masks[40][start[1],start[2]],'Arrival threshold blocked'
 def traverse(allowed):
  seen={start};q=deque([start])
  while q:
   z,x,y=q.popleft()
   for a,b,c in [(z,x+1,y),(z,x-1,y),(z,x,y+1),(z,x,y-1)]+vertical.get((z,x,y),[]):
    v=(a,b,c)
    if 0<=b<len(xs) and 0<=c<len(ys) and allowed[a][b,c] and v not in seen:
     seen.add(v);q.append(v)
  return seen
 seen=traverse(masks)
 public={z:m.copy() for z,m in masks.items()}
 for f in l.FLOORS:
  for s in f['spaces']:
   if s['kind'] in ('guest','bath','service') or s['name'].startswith('Treatment') or s['name']=='Cottage garden':
    public[f['z']]&=~rect(s['rect'])
 public_seen=traverse(public)
 public_core_targets=[cell(51,24,z) for z in (40,54,68)]+[cell(120,54,z) for z in (12,26,40)]
 assert all(v in public_seen for v in public_core_targets),'Public access depends on private/service rooms'
 # Clear strips run outside the coping and stop before the lounger band.
 for r in [(58.5,63.5,7,13),(88.5,63.5,7,13),(65.5,54,23,9.5),(65.5,76.5,23,4.5)]:
  assert np.all(masks[40][rect(r)]),'Pool circulation strip obstructed'

 results=[]
 for f in l.FLOORS:
  for s in f['spaces']+[dict(name=b['name'],node=b['node']) for b in f['balconies']]:
   c=cell(*s['node'],f['z'])
   results.append(dict(floor=f['id'],space=s['name'],reachable=c in seen,node=s['node']))
 missing=[r for r in results if not r['reachable']]
 out=dict(scope='floor topology and actual door gaps; not structural or code certification',grid_studs=STEP,
          connected_targets=len(results)-len(missing),total_targets=len(results),unreachable=missing,
          public_core_access_without_private_rooms=True,pool_clear_loop=True,targets=results)
 (HERE/'circulation-check.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k!='targets'},indent=2))
 assert not missing,'Disconnected destinations; inspect floor plans before proceeding'
 return out
if __name__=='__main__':run()
