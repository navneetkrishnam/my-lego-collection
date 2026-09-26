"""Inventory-limited exact-part placements, with deterministic rectangle packing."""
from collections import Counter
import math

def rotation(a):
 c=round(math.cos(math.radians(a)),10);s=round(math.sin(math.radians(a)),10)
 return [c,0,s,0,1,0,-s,0,c]
def transform(m,v):return [sum(m[3*i+j]*v[j] for j in range(3)) for i in range(3)]
def rect(x,y,w,d):return {(a,b) for a in range(x,x+w) for b in range(y,y+d)}

class Model:
 def __init__(self,snapshot):
  self.snapshot=snapshot;self.parts=snapshot['parts'];self.remaining={e:p['minimum'] for e,p in self.parts.items()};self.pieces=[];self.module='base';self.step=1;self.serial=0
 def element(self,code,color):
  e=self.snapshot['preferred'].get(str(code)+':'+str(color))
  if not e:raise ValueError(f'No exact element for shape{code}/color{color}')
  return e
 def put(self,e,x,y,z,turn=False,angle=None):
  if self.remaining.get(e,0)<=0:raise ValueError('Inventory shortage '+e+' in '+self.module)
  p=self.parts[e];w,d=(p['d'],p['w']) if turn else (p['w'],p['d']);mat=rotation((90 if turn else 0) if angle is None else angle)
  delta=transform(mat,p.get('origin_offset',[0,0,0]))
  self.serial+=1
  q=dict(key=f'H{self.serial:05}',element=e,x=x,y=y,z=z,w=w,d=d,h=p['h'],kind=p['kind'],studded=p['studded'],matrix=mat,origin=[20*(x+w/2)+delta[0],-8*(z+p['h'])+delta[1],20*(y+d/2)+delta[2]],step=self.step,module=self.module)
  self.pieces.append(q);self.remaining[e]-=1;return q
 def part(self,code,color,x,y,z,turn=False,angle=None):return self.put(self.element(code,color),x,y,z,turn,angle)
 def insert(self,parent,code,offset):
  e=self.element(code,47);q=self.put(e,0,0,0);q.update(parent=parent['key'],offset=offset,matrix=parent['matrix']);delta=transform(parent['matrix'],offset);q['origin']=[a+b for a,b in zip(parent['origin'],delta)];return q
 def available(self,kinds,colors,max_area=9999):
  rank={c:i for i,c in enumerate(colors)}
  es=[e for e in self.snapshot['preferred'].values() if self.remaining[e]>0 and self.parts[e]['kind'] in kinds and self.parts[e]['ldraw_color'] in colors and self.parts[e]['w']*self.parts[e]['d']<=max_area]
  return sorted(es,key=lambda e:(-self.parts[e]['w']*self.parts[e]['d'],rank[self.parts[e]['ldraw_color']],-self.remaining[e],e))
 def fill(self,cells,z,kinds,colors,max_area=9999,color_first=False):
  cells=set(cells);added=[]
  while cells:
   x,y=min(cells,key=lambda p:(p[1],p[0]));found=False
   choices=self.available(kinds,colors,max_area)
   if color_first:choices.sort(key=lambda e:colors.index(self.parts[e]['ldraw_color']))
   for e in choices:
    p=self.parts[e]
    if p['kind']=='brick' and p['h']!=3:continue
    for turn in (False,True):
     w,d=(p['d'],p['w']) if turn else (p['w'],p['d']);foot=rect(x,y,w,d)
     if foot<=cells:
      added.append(self.put(e,x,y,z,turn));cells-=foot;found=True;break
    if found:break
   if not found:raise ValueError(f'Unfilled surface {self.module}: {len(cells)} cells, first{x,y,z}; kinds{kinds} colors{colors}')
  return added
 def volume(self,cells,colors,max_area=32):
  cells=set(cells)
  while cells:
   x,y,z=min(cells,key=lambda p:(p[2],p[1],p[0]));found=False
   es=self.available(['brick','plate'],colors,max_area)
   es.sort(key=lambda e:(-self.parts[e]['w']*self.parts[e]['d']*self.parts[e]['h'],colors.index(self.parts[e]['ldraw_color']),e))
   for e in es:
    p=self.parts[e]
    for turn in (False,True):
     w,d=(p['d'],p['w']) if turn else (p['w'],p['d'])
     vox={(a,b,c) for a,b in rect(x,y,w,d) for c in range(z,z+p['h'])}
     if vox<=cells:self.put(e,x,y,z,turn);cells-=vox;found=True;break
    if found:break
   if not found:raise ValueError(f'Unfilled volume {self.module}: {len(cells)} cells, first{x,y,z}')
 def wall(self,x,y,length,z,height,holes=(),turn=False,panels=True):
  # Local u across facade; v in brick courses. Holes use those units.
  cells=rect(0,0,length,height//3)
  for u,v,w,h in holes:cells-=rect(u,v,w,h)
  while cells:
   u,v=min(cells,key=lambda p:(p[1],p[0]));found=False
   colors=[19,15] if v==0 else [15,19]
   es=self.available(['brick','panel'] if panels else ['brick'],colors)
   es=[e for e in es if self.parts[e]['d']==1]
   # Panels save scarce bricks on side/rear walls; stratify the bottom course.
   def score(e):
    p=self.parts[e];w=p['w'];h=p['h']//3
    # A four-wide panel in a five-wide pier strands a column of scarce singles.
    single_gap=any((u+w,v+k) in cells and (u+w+1,v+k) not in cells for k in range(h))
    return (single_gap,-p['h']*w,colors.index(p['ldraw_color']),e)
   es.sort(key=score)
   for e in es:
    p=self.parts[e];w=p['w'];h=p['h']//3;area=rect(u,v,w,h)
    if area<=cells:
     px,py=(x,y+u) if turn else (x+u,y);self.put(e,px,py,z+3*v,turn);cells-=area;found=True;break
   if not found:
    # Three stacked plates are still ordinary studded masonry, not an invented part.
    width=next((w for w in (8,6,4,3,2,1) if rect(u,v,w,1)<=cells),1)
    px,py=(x,y+u) if turn else (x+u,y)
    for k in range(3):self.fill(rect(px,py,1,width) if turn else rect(px,py,width,1),z+3*v+k,['plate'],[15,19],8)
    cells-=rect(u,v,width,1)
