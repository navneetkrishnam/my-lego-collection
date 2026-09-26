"""Cliffside Hotel - deterministic actual-element architectural draft."""
from collections import Counter
import json,csv,hashlib
from pathlib import Path
from engine import Model,rect
from roof import roof
from catalog import dump
HERE=Path(__file__).resolve().parent

STEPS={1:'Interlocked foundation',2:'Cliff supports and retaining walls',3:'Staircase, pool structure and outcrops',4:'Raised terrace deck',5:'Terrace paving, pool water and furniture',10:'Ground floor architecture',11:'Ground floor interiors',12:'First floor decks and cornices',20:'First floor architecture and balconies',21:'First floor interiors',22:'Second floor decks and cornices',30:'Second floor architecture and balconies',31:'Second floor interiors',32:'Main building roof deck',40:'Pavilion roof assembly',41:'Guest wing roof assembly',42:'Main roof assembly',50:'Flowering planters'}

def author(snapshot):
 m=Model(snapshot)
 # Reserve scarce roof parts before the rest of the model consumes them.
 roof(m,'main-roof',4,4,16,12,86,60)
 roof(m,'guest-roof',32,8,12,12,64,61)
 roof(m,'pavilion-roof',20,4,12,8,42,62)
 print('Roof reservation',len(m.pieces),flush=True)

 def win(x,y,z,kind='door',turn=False):
  if kind=='small':
   q=m.part('60594',15,x,y,z,turn);m.insert(q,'60603',[0,8,4])
  elif kind=='wide':
   q=m.part('42205',15,x,y,z,turn);m.insert(q,'42509',[0,4.5,5])
  else:
   q=m.part('60596',15,x,y,z,turn);m.insert(q,'60616',[-32,0,5])
 def slab(x,y,w,d,z,balconies=False):
  cells=rect(x,y,w,d)
  if balconies:
   for bx in (x+2,x+10):
    patch=rect(bx,y+d-1,6,4);m.fill(patch,z,['plate'],[15,19],24);cells-=patch
  m.fill(cells,z,['plate'],[15,19,71],48)
 def house(name,x,y,w,d,floors,firststep,main=False):
  for floor in range(floors):
   m.module=name;z=20+22*floor;m.step=firststep+2*floor
   front=y+d-1
   # Local hole definitions use brick-course units and exclude side-wall corners.
   if main and floor==0:
    front_holes=[(1,0,6,7),(9,0,6,7)]
    for xx in (x+1,x+9):m.part('40066',15,xx,front,z)
    # Outer studs of large arches are one brick lower than their central tops.
    for xx in (x+1,x+6,x+9,x+14):m.part('3005',15,xx,front,z+18)
   else:
    positions=[2,10] if main else [4]
    front_holes=[(a,1,4,6) for a in positions]
    for a in positions:win(x+a,front,z+3)
   m.wall(x,front,w,z,21,front_holes,panels=False)
   # Rear elevation: one broad glazed opening per floor.
   rear_kind='wide' if name!='pavilion' else 'door';rw=6 if rear_kind=='wide' else 4;u=(w-rw)//2
   win(x+u,y,z+3,rear_kind);m.wall(x,y,w,z,21,[(u,1,rw,6)],panels=True)
   # Main left elevation uses paired small windows; wing right uses door-height panes.
   for side in (0,1):
    xx=x if side==0 else x+w-1;holes=[]
    if main and side==0:
     yy=y+4;win(xx,yy,z+3,'small',True);win(xx,yy,z+12,'small',True);holes=[(3,1,4,6)]
    elif main and side==1 and floor==2:
     yy=y+4;win(xx,yy,z+3,'small',True);win(xx,yy,z+12,'small',True);holes=[(3,1,4,6)]
    elif not main and name!='pavilion' and side==1:
     yy=y+4;win(xx,yy,z+3,'door',True);holes=[(3,1,4,6)]
    m.wall(xx,y+1,d-2,z,21,holes,True,True)
   # Floor paving leaves the wall footprint studded.
   m.module=name+'-interior';m.step=40
   m.fill(rect(x+1,y+1,w-2,d-2),z,['tile'],[19,15,71],8)
   m.module=name;m.step=firststep+2*floor+1
   slab(x,y,w,d,z+21,balconies=main and floor<2)
  return m
 house('main-building',4,4,16,12,3,10,True)
 house('guest-wing',32,8,12,12,2,20)
 # Low connecting pavilion: glazed door in front, solid rear and side walls.
 m.module='pavilion';m.step=30
 win(24,11,23);win(24,4,23)
 m.wall(20,11,12,20,21,[(4,1,4,6)],panels=False);m.wall(20,4,12,20,21,[(4,1,4,6)])
 for xx in (20,31):m.wall(xx,5,6,20,21,turn=True)
 m.step=40;m.fill(rect(21,5,10,6),20,['tile'],[19,15,71],8)
 m.step=31;slab(20,4,12,8,41)
 print('Buildings',len(m.pieces),flush=True)

 # Balcony balustrades, integrated with cantilevered floor plates.
 m.module='balconies';m.step=45
 balcony_reserved=set()
 for level in (42,64):
  for bx in (6,14):
   for xx in (bx,bx+5):
    for zz in (0,3):m.part('3062',71 if zz==0 else 15,xx,18,level+zz)
   m.part('15332',15,bx+1,18,level)
   m.part('6636',15,bx,18,level+6)
   m.fill(rect(bx,16,6,2),level,['tile'],[19,15,71],6)

 # Furnished rooms: reception counter, guest beds, cabinets, small tables.
 m.module='furnishings';m.step=40
 # Put furniture on untiled studs by removing exactly its floor tiles later.
 def reserve_furniture(x,y,w,d,z):
  target=rect(x,y,w,d)
  removed=[]
  for q in m.pieces[:]:
   if q.get('pose_type') or q['kind']!='tile' or q['z']!=z:continue
   footprint=rect(q['x'],q['y'],q['w'],q['d'])
   if footprint & target:
    m.pieces.remove(q);m.remaining[q['element']]+=1;removed.extend(footprint-target)
  if removed:m.fill(set(removed),z,['tile'],[19,15,71],4)
 def block(x,y,w,d,z,height,colors):
  for zz in range(z,z+height,3):m.fill(rect(x,y,w,d),zz,['brick'],colors,8)
 for x,y,z in [(7,7,42),(14,7,42),(7,7,64),(14,7,64),(35,11,42)]:
  reserve_furniture(x,y,3,5,z);block(x,y,3,5,z,3,[70,0,19]);m.fill(rect(x,y,3,5),z+3,['plate'],[15,19],8)
  m.fill(rect(x,y,3,1),z+4,['tile'],[15],4);m.fill(rect(x,y+1,3,4),z+4,['tile'],[1,2,288,19,15],4)
 reserve_furniture(7,7,8,2,20);block(7,7,8,2,20,6,[19,15]);m.fill(rect(7,7,8,2),26,['plate'],[70,308],8);m.fill(rect(7,7,8,2),27,['tile'],[70,0,19],8)
 for x,y,z in [(36,14,20),(26,7,20),(9,12,64)]:
  reserve_furniture(x,y,2,2,z);m.part('3003',15,x,y,z);m.part('3022',70,x,y,z+3)
  m.part('3899',15,x+1,y+1,z+4,angle=0)
 print('Furnishings',len(m.pieces),flush=True)

 # Raised deck: courtyards at20 plates, pool water lower at18.
 m.module='terrace';m.step=4
 deck=rect(2,2,44,28)-rect(19,20,6,10)-rect(28,22,10,6)
 m.fill(deck,19,['plate'],[19,71,72,15],128)
 # Pool slab supported lower than surrounding terrace.
 m.module='pool';m.step=3;m.fill(rect(28,22,10,6),16,['plate'],[1,3,15],64)
 m.step=5;m.fill(rect(28,22,10,6),17,['tile'],[43,47,40,212,3,1],4)
 m.fill(rect(27,21,12,8)-rect(28,22,10,6),20,['tile'],[15,19],6)

 # Columns underneath the deck; concealed colors preserve neutral exterior stock.
 m.module='cliff-support';m.step=2
 for xx in (3,11,27,35,43):
  for yy in (3,11,19,27):
   if rect(xx,yy,2,2)&rect(19,20,6,10) or rect(xx,yy,2,2)&rect(28,22,10,6):continue
   for zz in range(2,17,3):m.fill(rect(xx,yy,2,2),zz,['brick'],[0,1,4,14,25,2,71,19,15],4)
   for zz in (17,18):m.fill(rect(xx,yy,2,2),zz,['plate'],[0,1,4,14,25,2,71,19],4)
 # Pool support columns to the lower slab.
 for xx in (28,36):
  for yy in (22,26):
   for zz in range(2,14,3):m.fill(rect(xx,yy,2,2),zz,['brick'],[0,1,4,14,25,2,71],4)
   for zz in (14,15):m.fill(rect(xx,yy,2,2),zz,['plate'],[0,1,4,14,25,2,71],4)

 # Pale stone perimeter and stepped stair retaining walls.
 m.module='cliff-face';m.step=2
 def stonewall(x,y,length,z,h,turn=False):
  for level in range(h//3):
   cells=rect(x,y,1,length) if turn else rect(x,y,length,1)
   m.fill(cells,z+3*level,['brick'],[19,71,72,15],8)
 for x,y,l,t in [(2,2,44,False),(2,29,17,False),(25,29,21,False),(2,3,26,True),(45,3,26,True)]:stonewall(x,y,l,2,15,t)
 # Last two plate courses support the deck edge.
 for zz in (17,18):
  ring=rect(2,2,44,28)-rect(3,3,42,26)-rect(19,20,6,10)
  m.fill(ring,zz,['plate'],[19,71,72,15],8)

 # Broad straight flight with a generous approach; every tread is supported.
 m.module='staircase';m.step=3
 for y in range(20,38):
  h=38-y # firsttreadz20, lowestz3
  m.fill(rect(19,y,6,1),1+h,['tile'],[15,19,71],6)
 m.volume({(x,y,z) for x in range(19,25) for y in range(20,38) for z in range(2,39-y)},[19,71,72,15,0],12)
 # Exterior paved space excludes building footprints, pool and stairwell.
 m.module='courtyard';m.step=5
 furniture=[(5,20,2,2),(11,20,2,2),(39,23,2,4),(39,27,2,2),(3,24,2,4),(42,23,2,4),(25,17,2,2)]
 occupied=rect(4,4,16,12)|rect(20,4,12,8)|rect(32,8,12,12)|rect(27,21,12,8)
 for b in furniture:occupied|=rect(*b)
 m.fill(deck-occupied,20,['tile'],[19,15,71,72],8,color_first=True)

 m.module='courtyard-details';m.step=45
 for x,y,w,d in furniture:
  if w==d==2:
   m.fill(rect(x,y,2,2),20,['brick'],[15,19,71],4);m.part('3022',70,x,y,23)
  else:
   m.fill(rect(x,y,w,d),20,['brick'],[70,19,72],8);m.fill(rect(x,y,w,d),23,['plate'],[70,2],8)
 # Plant clusters on a two-stud grid, with alternating foliage orientations.
 m.module='planting';m.step=50
 for x,y in [(3,24),(3,26),(42,23),(42,25),(39,23),(39,25)]:
  m.part('32607',2 if (x+y)%2 else 10,x,y,24,angle=0)
  m.part('24866',29 if (x+y)%2 else 15,x,y,25)
  # One broad leaf per two-stud planter bay keeps adjacent foliage clear.

 # Foundation slabs, crossed seams. All visible outer faces stay charcoal.
 m.module='foundation';m.step=1
 m.fill(rect(0,0,48,40),0,['plate'],[0,72],128)
 rim=rect(0,0,48,40)-rect(1,1,46,38)
 m.fill(rim,1,['plate'],[0,72],8)
 m.fill(rect(1,1,46,38),1,['plate'],[0,72,71,19,15],48)
 # Low sea edge / rocky approach around the elevated platform.
 m.module='waterfront';m.step=5
 low=rect(0,0,48,40)-rect(2,2,44,28)-rect(19,30,6,8)
 m.fill(low,2,['tile'],[71,72,19,15,0],8)
 # Projecting stone cornices articulate the storeys and tie the facade edges.
 m.module='architectural-trim';m.step=45
 for x,y,w,d,levels in [(4,4,16,12,[41,63,85]),(32,8,12,12,[41,63]),(20,4,12,8,[41])]:
  for zz in levels:
   edge=rect(x-1,y-1,w+2,d+2)-rect(x,y,w,d)
   # Preserve adjoining buildings and already authored balcony plates.
   for q in m.pieces:
    if q.get('pose_type') or q['kind']=='insert':continue
    if q['z']<=zz<q['z']+q['h']:edge-=rect(q['x'],q['y'],q['w'],q['d'])
   inner_ring=rect(x,y,w,d)-rect(x+1,y+1,w-2,d-2)
   for q in m.pieces[:]:
    if q.get('pose_type') or q['kind']!='plate' or q['z']!=zz:continue
    foot=rect(q['x'],q['y'],q['w'],q['d'])
    if foot&inner_ring:
     m.pieces.remove(q);m.remaining[q['element']]+=1;edge|=foot
   m.fill(edge,zz,['plate'],[15,19,71],24)
   # Keep exposed studs for the decorative piers and removable roof assemblies.
 # Slender outer piers emphasize the recessed windows and entrance bays.
 for xx,yy,levels in [(4,16,[20,42,64]),(12,16,[20,42,64]),(19,16,[20,42,64]),(32,20,[20,42]),(43,20,[20,42]),(20,12,[20]),(31,12,[20])]:
  for zz in levels:
   reserve_furniture(xx,yy,1,1,zz)
   for start in (zz,zz+12):m.volume({(xx,yy,h) for h in range(start,start+9)},[15,19],1)
   mount_color=next(c for c in [15,19,71] if m.remaining.get(m.element('87087',c),0)>0)
   mount=m.part('87087',mount_color,xx,yy,zz+9,angle=180)
   panel=m.part('2431',0,0,0,0)
   panel.update(pose_type='facade_inlay',mount_parent=mount['key'],matrix=[0,0,1,-1,0,0,0,-1,0],origin=[mount['origin'][0],mount['origin'][1]+20,mount['origin'][2]+18])
 # Irregular rock outcrops around the terrace replace the flat lower paving.
 m.module='rock-outcrops';m.step=3
 rocks=[]
 for xx in list(range(2,18,2))+list(range(26,46,2)):
  rocks.append((xx,30,12+3*((xx//2)%2),180))
 for xx in [2,6,10,14,26,30,34,38,42]:rocks.append((xx,34,6+3*((xx//2)%2),180))
 for xx in (0,46):
  for yy in (6,14,22):rocks.append((xx,yy,9,90 if xx==46 else 270))
 for i,(xx,yy,height,angle) in enumerate(rocks):
  reserve_furniture(xx,yy,2,2,2)
  m.volume({(a,b,c) for a,b in rect(xx,yy,2,2) for c in range(2,2+height)},[19,71,72,28],4)
  candidates=[m.element('3039',c) for c in [19,71,72,28] if '3039:'+str(c) in m.snapshot['preferred']]
  e=next((e for e in candidates if m.remaining[e]>0),None)
  if e:m.put(e,xx,yy,2+height,angle=angle)
  else:m.fill(rect(xx,yy,2,2),2+height,['plate'],[19,71,72,28],4)
 m.module='architectural-trim';m.step=45
 m.fill(rect(6,16,6,2),40,['plate'],[15,19,71],12)
 m.fill(rect(38,10,2,4),62,['plate'],[15,19,71],8)
 # Repeated flowering planters soften the entrance terrace.
 m.module='planting';m.step=50
 for xx,yy in [(5,20),(11,20),(25,17),(39,27)]:
  m.part('32607',2,xx,yy,24)
  m.part('24866',29,xx,yy,25)
  m.part('32607',288,xx+1,yy+1,24,angle=180)
 # A cornice is optional ornament: omit unsupported thin fringe strips.
 # Floors, balconies, roof panels and structural parts may never be dropped here.
 from audit import inspect
 report=inspect(m.pieces,snapshot);bykey={q['key']:q for q in m.pieces}
 for comp in report['isolated_components']:
  qs=[bykey[k] for k in comp]
  if all(q['module']=='architectural-trim' and q['kind']=='plate' and min(q['w'],q['d'])==1 for q in qs):
   for q in qs:m.pieces.remove(q);m.remaining[q['element']]+=1
 # Publish a floor-by-floor sequence so furniture precedes the ceiling above it.
 bykey={q['key']:q for q in m.pieces}
 for q in m.pieces:
  if q['module'] in ['main-roof','guest-roof','pavilion-roof']:
   q['step']={'main-roof':42,'guest-roof':41,'pavilion-roof':40}[q['module']];continue
  if q['module']=='planting':q['step']=50;continue
  if q['module']=='courtyard-details':q['step']=5;continue
  if q['step']<=5:continue
  anchor=bykey.get(q.get('parent',q.get('mount_parent')),q);zz=anchor['z']
  floor=0 if zz<42 else 1 if zz<64 else 2
  if q['module'].endswith('-interior') or q['module']=='furnishings':q['step']=[11,21,31][floor]
  elif q['kind']=='plate' and zz in [40,41,62,63,85]:q['step']=12 if zz<=41 else 22 if zz<=63 else 32
  else:q['step']=[10,20,30][floor]
 # Keys become stable only after furniture flooring has been cut and rebuilt.
 old={q['key']:f'H{i+1:05}' for i,q in enumerate(m.pieces)}
 for i,q in enumerate(m.pieces):
  q['key']=f'H{i+1:05}'
  for k in ('parent','hinge_parent','mount_parent'):
   if k in q:q[k]=old[q[k]]
 m.pieces.sort(key=lambda p:(p['step'],p.get('panel',''),p['z'],p['y'],p['x'],p['key']))
 return m

def export(m):
 used=Counter(q['element'] for q in m.pieces);bom=[];allocation=[]
 for e,n in sorted(used.items()):
  p=m.parts[e];bom.append(dict(element=e,required=n,available=p['minimum'],margin=p['minimum']-n,name=p['name'],color=p['color'],ldraw=p['ldraw']))
  remaining=n
  for src in sorted(p['sources'],key=lambda s:(-s['quantity'],s['set'],s['copy'])):
   count=min(remaining,src['quantity'])
   if count:allocation.append(dict(src,element=e,quantity=count,donor_allowance=src['quantity']));remaining-=count
  if remaining:raise ValueError('Unallocated '+e)
 dump(HERE/'model.json',dict(title='Cliffside Hotel',status='coordinate build draft; consult verification reports; physical build not tested',footprint=[48,40],steps=[dict(number=n,title=t) for n,t in sorted(STEPS.items())],pieces=m.pieces))
 dump(HERE/'bom.json',bom);dump(HERE/'allocation.json',allocation)
 lines=['0 Cliffside Hotel - actual-element architectural draft','0 Name: cliffside-hotel.ldr','0 Physical build not tested.']
 last=None
 for q in m.pieces:
  if q['step']!=last:
   if last is not None:lines.append('0 STEP')
   lines.append(f"0 Stage {q['step']}: {STEPS[q['step']]}");last=q['step']
  p=m.parts[q['element']];lines += [f"0 {q['key']} ELEMENT {q['element']} MODULE {q['module']}",f"1 {p['ldraw_color']} "+' '.join(f'{v:.8g}' for v in q['origin']+q['matrix'])+' '+p['ldraw']]
 (HERE/'cliffside-hotel.ldr').write_text('\n'.join(lines)+'\n')
 print(json.dumps({'pieces':len(m.pieces),'elements':len(used),'modules':dict(Counter(q['module'] for q in m.pieces))},indent=2))
if __name__=='__main__':export(author(json.loads((HERE/'inventory-snapshot.json').read_text())))
