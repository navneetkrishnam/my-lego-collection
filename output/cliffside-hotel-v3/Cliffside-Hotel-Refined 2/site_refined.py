"""Taller coastal terraces, hollow rock shells and a turning staircase."""
from engine import rect
from facade import solid

def wall_volume(m, cells, colors):
    cells=set(cells)
    while cells:
        x,y,z=min(cells,key=lambda p:(p[2],p[1],p[0]));found=False
        choices=m.available(['panel','brick','plate'],colors,16)
        choices.sort(key=lambda e:(-m.parts[e]['h']*m.parts[e]['w']*m.parts[e]['d'],colors.index(m.parts[e]['ldraw_color']),e))
        for e in choices:
            p=m.parts[e]
            for turn in (False,True):
                w,d=(p['d'],p['w']) if turn else (p['w'],p['d'])
                vox={(a,b,c) for a,b in rect(x,y,w,d) for c in range(z,z+p['h'])}
                if vox<=cells:m.put(e,x,y,z,turn);cells-=vox;found=True;break
            if found:break
        if not found:raise ValueError(f'Wall packing shortage at {x,y,z}')

def exposed_shell(full):
    return {p for p in full if any((p[0]+dx,p[1]+dy,p[2]+dz) not in full for dx,dy,dz in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,3)])}

def build(m):
    hidden=sorted({p['ldraw_color'] for p in m.parts.values() if p['kind'] in ['brick','plate'] and p['ldraw_color'] not in [15,19,70,308,28,71,72]})
    upper=rect(22,24,8,9);landing=rect(22,33,8,8);lower=rect(12,33,10,8)
    stairs=upper|landing|lower;pool=rect(34,25,12,6)
    deck=rect(2,2,52,30)-stairs-pool
    m.module='site-foundation';m.step=1
    for z,colors in [(0,[0,72,71]),(1,[72,0,71])]:m.fill(rect(0,0,56,44),z,['plate'],colors,128 if z==0 else 64)
    m.module='turning-staircase';m.step=3
    vox=set()
    for y in range(24,33):
        top=41-2*(y-24);vox|={(x,y,k) for x in range(22,30) for k in range(2,top)}
        m.fill(rect(22,y,8,1),top,['tile'],[19,15,71],8,color_first=True)
    for x in range(12,22):
        top=3+2*(x-12);vox|={(x,y,k) for y in range(33,41) for k in range(2,top)}
        m.fill(rect(x,33,1,8),top,['tile'],[19,15,71],8,color_first=True)
    m.volume(vox,[15,19,71,72,28],32)
    m.module='faceted-cliff';m.step=3
    heights={}
    rock_foot=rect(44,34,8,8)
    planting=[(4,34),(5,38),(7,41),(41,34),(34,38),(52,37)]
    plant_clearance=set().union(*(rect(x-1,y-1,4,3) for x,y in planting))
    for x,y,w,d,h in [(2,31,8,5,32),(3,36,7,4,20),(6,40,5,2,9),(10,31,10,2,25),(30,31,8,5,30),(32,36,8,4,18),(40,31,10,5,35),(43,36,10,3,24),(42,39,10,3,10)]:
        for xy in rect(x,y,w,d):
            if xy not in stairs and xy not in deck and xy not in rect(10,33,2,8) and xy not in rock_foot:heights[xy]=max(heights.get(xy,0),h)
    m.part('23996',72,44,34,2,angle=270)
    full={(x,y,z) for (x,y),height in heights.items() for z in range(2,2+height)}
    m.volume(exposed_shell(full),[71,72,28,19],16)
    capped=set()
    for (x,y),height in sorted(heights.items(),key=lambda r:(r[0][1],r[0][0])):
        if (x+y)%3==0:continue
        for e in m.available(['rock_cap','slope'],[71,72,28],4):
            p=m.parts[e];area=rect(x,y,p['w'],p['d'])
            if area&(capped|plant_clearance) or any(heights.get(xy)!=height for xy in area):continue
            # Rectangular caps keep their catalog footprint under half turns.
            m.put(e,x,y,2+height,angle=180*((x+2*y)%2));capped|=area;break
    m.module='cliff-flowers';m.step=43
    for i,(x,y) in enumerate(planting):
        height=2+heights[x,y]
        m.part('32607',2,x,y,height)
        m.part('24866',29 if i<3 else 15,x,y,height+1)
    m.module='arched-landing';m.step=3
    ring=landing-rect(23,34,6,6)
    vox={(x,y,z) for x,y in ring for z in range(2,22)}
    vox-={(x,40,z) for x in range(23,29) for z in range(2,20)}
    for x in (23,28):solid(m,rect(x,40,1,1),2,12,(15,))
    m.part('15254',15,23,40,14)
    wall_volume(m,vox,[71,19,15,72])
    m.fill(landing,22,['plate'],[19,71,15],32)
    m.fill(landing-{(22,40),(29,40)},23,['tile'],[19,15,71],8,color_first=True)
    for x in (22,29):
        for z in (23,26):m.part('3062',71,x,40,z)
    m.fill(rect(22,40,8,1),29,['plate'],[15,19],8)
    m.fill(rect(22,40,8,1),30,['tile'],[15],8)
    m.module='retaining-masonry';m.step=2
    ring=(rect(2,2,52,30)-rect(3,3,50,28))-stairs
    walls={(x,y,z) for x,y in ring for z in range(2,41)}
    # A glazed lower gallery uses complete owned frames along the rear,
    # reducing masonry demand while giving that elevation an architectural use.
    for x in range(4,52,6):
        walls-={(xx,2,z) for xx in range(x,x+6) for z in range(2,20)}
        frame=m.part('42205',15,x,2,2)
        if ((x-4)//6)%2==0:m.insert(frame,'42509',[0,4.5,5])
    wall_volume(m,{(x,3,z) for x in range(4,52) for z in range(2,20)},[0,72])
    wall_volume(m,walls,[71,72,19,15,28])
    m.module='concealed-piers';m.step=2
    for x in range(5,53,8):
        for y in range(5,29,8):
            area=rect(x,y,2,2)
            if area&(stairs|pool):continue
            solid(m,area,2,39,hidden)
    m.module='terrace-deck';m.step=4
    m.fill(deck,41,['plate'],[19,71,15],64)
    m.module='pool';m.step=4
    for x,y in [(34,25),(44,25),(34,29),(44,29)]:solid(m,rect(x,y,2,2),2,36,hidden)
    m.fill(pool,38,['plate'],[1,3,15],32)
    m.fill(pool,39,['tile'],[43,47,212,3,1],4,color_first=True)
    m.module='waterfront';m.step=5
    water=rect(0,32,56,12)-set(heights)-stairs-rock_foot;quay=rect(10,33,2,8)
    m.fill(quay,2,['tile'],[71,19],8)
    m.fill(water-quay,2,['tile'],[43,47,212,3,1,71],8,color_first=True)
    # Tie separated ceiling patches of the hollow cliff to its foundation.
    # Each added column must remain wholly inside the planned rock volume.
    from audit import inspect
    checked=inspect(m.pieces,m.snapshot);bykey={q['key']:q for q in m.pieces}
    occupied=set()
    for q in m.pieces:
        if q.get('pose_type') or q['kind']=='insert':continue
        occupied|={(x,y,z) for x,y in rect(q['x'],q['y'],q['w'],q['d']) for z in range(q['z'],q['z']+q['h'])}
    supports=[];m.module='cliff-internal-supports';m.step=2
    for component in checked['isolated_components']:
        pieces=[bykey[k] for k in component]
        if not all(q['module'] in ['faceted-cliff','cliff-flowers'] for q in pieces):continue
        attached=False
        for q in sorted(pieces,key=lambda q:(q['z'],q['key'])):
            if q['kind'] not in ['brick','plate']:continue
            for x,y in sorted(rect(q['x'],q['y'],q['w'],q['d'])):
                low=q['z']
                while low>2 and (x,y,low-1) not in occupied:low-=1
                vox={(x,y,z) for z in range(low,q['z'])}
                if vox and vox<=full:
                    m.volume(vox,hidden,1);occupied|=vox
                    supports.append(dict(x=x,y=y,bottom=low,top=q['z'],supports=q['key']))
                    attached=True;break
            if attached:break
        if not attached:raise ValueError('No interior support path for cliff component '+str(component))
    return dict(terrace_height_plates=42,staircase='Two flights with 90-degree landing',hollow_cliff=True,internal_supports=supports)
