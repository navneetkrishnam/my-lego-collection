"""Compose the revised building with stepped wings and a supported cliff site."""
from pathlib import Path
import sys, json
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from facade import author as main_building, solid, export
from engine import rect
from roof import roof as pitched_roof

def author():
    m, report=main_building()
    # The site deck replaces the study's temporary stand.
    for q in m.pieces[:]:
        if q['module']=='foundation':
            m.pieces.remove(q);m.remaining[q['element']]+=1
    for q in m.pieces:
        q['origin']=[q['origin'][0]+40,q['origin'][1]-176,q['origin'][2]+40]
        if q['kind']!='insert' and not q.get('pose_type'):
            q['x']+=2;q['y']+=2;q['z']+=22
        q['step']+=10
    pitched_roof(m,'guest-wing-roof',40,10,14,12,70,55)
    pitched_roof(m,'connector-roof',28,4,12,8,47,54)

    def wing(x,y,w,d,floors,name):
        for floor in range(floors):
            z=24+23*floor;front=y+d-1
            m.module=name;m.step=15+floor*10
            wall=rect(x,front,w,1)
            bays=(x+1,x+7) if w==14 else (x+3,)
            holes=set().union(*(rect(b,front,6,1) for b in bays))
            solid(m,wall,z,3,(15,))
            solid(m,wall-holes,z+3,15,(15,))
            for b in bays:
                for xx in (b,b+5):solid(m,rect(xx,front,1,1),z+3,9,(15,))
                m.part('15254',15,b,front,z+12)
            solid(m,wall,z+18,3,(15,))
            # A warm recessed door-height panel behind the arch.
            for b in bays:
                if floor:
                    solid(m,rect(b+1,front-1,4,1),z,3,(15,))
                    frame=m.part('60594',15,b+1,front-1,z+3)
                    if m.remaining[m.element('60603',47)]:m.insert(frame,'60603',[0,8,4])
                    solid(m,rect(b+1,front-1,4,1),z+12,6,(0,))
                else:solid(m,rect(b+1,front-1,4,1),z,18,(70,))
            for sx in (x,x+w-1):
                side=rect(sx,y+1,1,d-2)
                if w==14 and sx==x+w-1:
                    solid(m,side,z,3,(15,))
                    solid(m,side-rect(sx,y+3,1,6),z+3,15,(15,))
                    for yy in (y+3,y+8):solid(m,rect(sx,yy,1,1),z+3,9,(15,))
                    m.part('15254',15,sx,y+3,z+12,turn=True)
                    solid(m,side,z+18,3,(15,))
                    solid(m,rect(sx-1,y+4,1,4),z,3,(15,))
                    m.part('60594',15,sx-1,y+4,z+3,turn=True)
                    solid(m,rect(sx-1,y+4,1,4),z+12,6,(0,))
                else:solid(m,side,z,21,(15,))
            rear=rect(x,y,w,1)
            solid(m,rear,z,3,(15,))
            for xx in ((x+2,x+8) if w==14 else (x+4,)):
                rear-=rect(xx,y,4,1)
                frame=m.part('60596',15,xx,y,z+3)
                m.insert(frame,'60616',[-32,0,5])
            solid(m,rear,z+3,18,(15,))
            m.step+=1;m.module=name+'-floor'
            for dz in (21,22):
                slab=rect(x,y,w,d)
                if w==14 and floor==0:
                    balcony=rect(x+2,front,10,4)
                    # Long transverse plates overlap the wall and terrace edge.
                    for xx in range(x+2,x+12,2):m.part('3020',15,xx,front,z+dz,turn=True)
                    slab-=balcony
                if w==14 and dz==22:
                    for yy in (y+3,y+7):
                        m.part('3020',15,x+4,yy,z+dz)
                        slab-=rect(x+4,yy,4,2)
                m.fill(slab,z+dz,['plate'],[15],32)
            if w==14 and floor==0:
                m.module='guest-balcony'
                for rx in (x+5,x+7):m.part('2432',0,rx,front+3,z+23)
    wing(40,10,14,12,2,'guest-wing')
    wing(28,4,12,8,1,'connector')

    m.module='site-foundation';m.step=1
    m.fill(rect(0,0,56,44),0,['plate'],[0,72,71],128)
    m.fill(rect(0,0,56,44),1,['plate'],[72,0,71],64)
    stairs=rect(22,24,8,20);pool=rect(34,25,12,6)
    deck=rect(2,2,52,30)-stairs-pool
    m.module='terrace-supports';m.step=2
    ring=(rect(2,2,52,30)-rect(3,3,50,28))-stairs
    # Continuous retaining walls and concealed cross-braced piers.
    solid(m,ring,2,18,(71,72,19,15))
    for zz in (20,21,22):m.fill(ring,zz,['plate'],[71,19,15],16)
    for x in range(5,53,8):
        for y in range(5,29,8):
            patch=rect(x,y,2,2)
            if patch&(stairs|pool):continue
            solid(m,patch,2,21,(0,1,4,14,25,2,72,71))
    m.module='terrace-deck';m.step=4
    m.fill(deck,23,['plate'],[19,71,15],64)
    # A second interlocking terrace skin is cut around every building.
    buildings=rect(4,4,24,14)|rect(40,10,14,12)|rect(28,4,12,8)
    # Keep the architecture's exact base elevation. Paving tiles cross deck seams.
    paving=deck-buildings
    # Sills and balcony study paving are already part of the building.
    for q in m.pieces:
        if q.get('pose_type') or q['kind']=='insert':continue
        if q['z']<=24<q['z']+q['h']:paving-=rect(q['x'],q['y'],q['w'],q['d'])
    pool_rim=rect(33,24,14,8)-pool
    m.module='courtyard-paving';m.step=6
    m.fill(paving-pool_rim,24,['tile'],[19,15,71],8,color_first=True)
    m.fill(pool_rim&deck,24,['tile'],[15],8)
    m.module='pool';m.step=5
    for x,y in [(34,25),(44,25),(34,29),(44,29)]:solid(m,rect(x,y,2,2),2,18,(1,0,14,4))
    m.fill(pool,20,['plate'],[1,3,15],32)
    m.fill(pool,21,['tile'],[43,47,212,3,1],4,color_first=True)

    m.module='broad-staircase';m.step=3
    # Eighteen supported one-plate treads end at a four-plate paved approach.
    stair_voxels=set()
    for y in range(24,44):
        top=47-y
        stair_voxels|={(x,y,k) for x in range(22,30) for k in range(2,top)}
        m.fill(rect(22,y,8,1),top,['tile'],[19,15,71],8,color_first=True)
    m.volume(stair_voxels,[71,72,19,15],16)

    m.module='layered-rock';m.step=3
    heights={}
    for x,y,w,d,h in [(2,32,7,4,14),(5,36,8,3,8),(11,32,9,4,11),
                      (15,36,5,4,5),(32,32,8,5,10),(40,32,10,4,16),
                      (45,36,8,3,8),(34,38,10,3,5)]:
        for xy in rect(x,y,w,d):heights[xy]=max(heights.get(xy,0),h)
    m.volume({(x,y,k) for (x,y),h in heights.items() for k in range(2,2+h)},[71,72,28,19],8)
    capped=set()
    for (x,y),h in sorted(heights.items(),key=lambda r:(r[0][1],r[0][0])):
        area=rect(x,y,2,2)
        if area&capped or any(heights.get(xy)!=h for xy in area):continue
        choices=[e for e in m.available(['slope'],[71,72,28],4) if m.parts[e]['w']==2]
        if not choices:break
        m.put(choices[0],x,y,2+h,angle=180);capped|=area
    m.module='waterfront';m.step=6
    water=rect(0,32,56,12)-set(heights)-stairs
    m.fill(water,2,['tile'],[43,47,212,3,1,71],8,color_first=True)

    def uncover(cells):
        leftovers=set()
        for q in m.pieces[:]:
            if q['kind']!='tile' or q.get('pose_type') or q['z']!=24:continue
            area=rect(q['x'],q['y'],q['w'],q['d'])
            if area&cells:
                m.pieces.remove(q);m.remaining[q['element']]+=1;leftovers|=area-cells
        if leftovers:m.fill(leftovers,24,['tile'],[19,15,71],8,color_first=True)

    m.module='courtyard-pergola';m.step=40
    posts=[(7,22),(15,22),(7,28),(15,28)]
    uncover(set().union(*(rect(x,y,2,1) for x,y in posts)))
    # Dark timber built from plate stacks preserves scarce brown wall bricks.
    for x,y in posts:
        solid(m,rect(x,y,2,1),24,15,(308,70))
    for y in (22,28):
        m.fill(rect(7,y,10,1),39,['plate'],[308,70],10)
        m.fill(rect(7,y,10,1),40,['plate'],[308,70],8)
    for x in (7,9,11,13,15):m.part('3460',308,x,22,41,turn=True)

    m.module='terrace-balustrade';m.step=41
    # Pillars are widely spaced and capped by a continuous slim stone rail.
    for x1,x2 in [(3,20),(31,52)]:
        columns=list(range(x1,x2+1,4))
        if columns[-1]!=x2:columns.append(x2)
        uncover({(x,31) for x in columns})
        for x in columns:solid(m,rect(x,31,1,1),24,6,(15,))
        m.fill(rect(x1,31,x2-x1+1,1),30,['plate'],[15],8)
        m.fill(rect(x1,31,x2-x1+1,1),31,['tile'],[15],8)

    m.module='courtyard-furniture';m.step=42
    for x,y in [(11,25),(30,18)]:
        uncover(rect(x,y,2,2));solid(m,rect(x,y,2,2),24,6,(15,))
        m.fill(rect(x,y,2,2),30,['plate'],[70,308],4)
        m.part('3899',15,x,y,31)
    for x,y in [(8,25),(14,25),(30,21)]:
        uncover(rect(x,y,2,2));solid(m,rect(x,y,2,2),24,3,(70,308))
        m.fill(rect(x,y,2,2),27,['tile'],[19,15],4)

    m.module='garden-planters';m.step=43
    for index,(x,y) in enumerate([(3,20),(3,26),(19,20),(31,14),(49,26)]):
        uncover(rect(x,y,2,2));solid(m,rect(x,y,2,2),24,3,(70,308,28))
        for px,py,angle in [(x,y,0),(x+1,y+1,180)]:
            m.part('32607',288,px,py,27,angle=angle)
            m.part('24866',29,px,py,28)
    # Two slim tiered evergreens frame the entrance garden.
    for x,y in [(4,23),(19,27)]:
        uncover(rect(x,y,2,2));solid(m,rect(x,y,2,2),24,3,(70,308,28))
        solid(m,rect(x,y,2,2),27,18,(288,2,10))
        solid(m,rect(x,y,1,1),45,6,(288,2,10))
        m.part('32607',2,x,y,51)
    m.pieces.sort(key=lambda q:(q['step'],q['key']))
    report.update(stage='Full architectural revision for visual review',
                  footprint=[3,3,26,16],base=93,ridge_top=103)
    report['chimney'][0]+=2;report['chimney'][1]+=2;report['chimney'][2]+=22
    for course in report['courses']:
        course['footprint'][0]+=2;course['footprint'][1]+=2;course['base']+=22
    return m,report

if __name__=='__main__':
    m,report=author()
    export(m,report,stem='hotel',title=f'Cliffside Hotel — {len(m.pieces):,}-piece architectural revision')
