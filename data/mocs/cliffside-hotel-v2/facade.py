"""Deterministic actual-part architectural study, preceding the full cliff site."""
from pathlib import Path
import sys, json
from collections import Counter
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from engine import Model, rect
sys.path.insert(0, str(HERE))
from roof_study import roof

def solid(m, cells, z, h, colors=(19,)):
    m.volume({(x,y,k) for x,y in cells for k in range(z,z+h)}, list(colors))

def author():
    m = Model(json.loads((HERE/'inventory-snapshot.json').read_text()))
    roof_report = roof(m,base=71)
    m.module='foundation'; m.step=1
    for z in range(2):
        m.fill(rect(1,1,26,18),z,['plate'],[71,72,19],32)
    m.part('87079',71,15,17,2)
    for floor, z in enumerate((2,25,48)):
        m.step=2+floor*3; m.module=f'storey-{floor+1}'
        # Front masonry, with six-stud arch units enclosing four-stud openings.
        front=rect(2,15,24,1)
        sill_base=front.copy()
        for x in (4,11,18): sill_base-=rect(x+1,15,4,1)
        solid(m,sill_base,z,3)
        piers=front.copy()
        for x in (4,11,18): piers-=rect(x,15,6,1)
        pier_voxels={(x,y,k) for x,y in piers for k in range(z+3,z+18)}
        if floor:
            for sx in (3,10,17,24):
                pier_voxels-={(sx,15,k) for k in range(z+9,z+12)}
                color=19 if m.remaining[m.element('87087',19)] else 15
                mount=m.part('87087',color,sx,15,z+9,angle=180)
                shutter=m.part('3710',2,0,0,0)
                shutter.update(pose_type='facade_inlay',mount_parent=mount['key'],
                    matrix=[0,0,1,-1,0,0,0,-1,0],
                    origin=[mount['origin'][0],mount['origin'][1]+20,mount['origin'][2]+18])
        m.volume(pier_voxels,[19])
        solid(m,front,z+18,3)
        for bay,x in enumerate((4,11,18)):
            for leg in (x,x+5): solid(m,rect(leg,15,1,1),z+3,9,(15,))
            m.part('15254',15,x,15,z+12)
            if floor==0 and bay==1:
                solid(m,rect(x+1,14,4,1),z,18,(70,))
                m.fill(rect(x+1,15,4,2),z,['tile'],[19],8)
                continue
            # Recessed windows retain real glazing inserts and a dark fanlight.
            solid(m,rect(x+1,14,4,1),z,3,(15,))
            m.part('3001',15,x+1,15,z)
            frame=m.part('60594',0,x+1,14,z+3)
            m.insert(frame,'60603',[0,8,4])
            solid(m,rect(x+1,14,4,1),z+12,6,(0,))
            m.fill(rect(x+1,16,4,1),z+3,['tile'],[19],4)
        # Full side/rear walls make this a useful building volume, not a flat prop.
        for sx in (2,25):
            side=rect(sx,2,1,13)
            solid(m,side,z,3)
            solid(m,rect(sx,2,1,1)|rect(sx,13,1,2),z+3,15,(15,))
            m.part('60581',19,sx,3,z+3,turn=True)
            solid(m,rect(sx,3,1,4),z+12,6)
            for yy in (7,12): solid(m,rect(sx,yy,1,1),z+3,9,(15,))
            m.part('15254',15,sx,7,z+12,turn=True)
            solid(m,side,z+18,3)
            ix=3 if sx==2 else 24
            solid(m,rect(ix,8,1,4),z,3,(15,))
            frame=m.part('60594',15,ix,8,z+3,turn=True)
            if floor: m.insert(frame,'60603',[0,8,4])
            solid(m,rect(ix,8,1,4),z+12,6,(0,))
        rear=rect(3,2,22,1)
        solid(m,rear,z,3,(15,))
        for xx in (6,16):
            rear-=rect(xx,2,4,1)
            frame=m.part('60596',15,xx,2,z+3)
            m.insert(frame,'60616',[-32,0,5])
        solid(m,rear,z+3,18,(15,))
        m.step+=1; m.module=f'floor-and-cornice-{floor+1}'
        # One plate cornice, plus projecting balcony slabs where occupied.
        slab=rect(2,2,24,14)
        if floor<2:
            for x in ((4,11) if floor==0 else (4,)):
                slab|=rect(x,15,6,4)
        else: slab=rect(1,1,26,16)
        m.fill(slab,z+21,['plate'],[15],32)
        top=slab.copy()
        if floor<2:
            for x in ((4,11) if floor==0 else (4,)):
                m.part('3032',15,x,15,z+22)
                top-=rect(x,15,6,4)
            if floor==1:
                for xx in (12,14): m.part('3021',15,xx,15,z+22,turn=True)
                top-=rect(12,15,4,3)
        m.fill(top,z+22,['plate'],[15],32)
        if floor<2:
            m.step+=1; m.module=f'balconies-{floor+1}'
            for x in ((4,11) if floor==0 else (4,)):
                for rx in (x+1,x+3): m.part('2432',0,rx,18,z+23)
                for rx in (x,x+5):
                    m.part('3062',0,rx,18,z+23)
                    m.fill(rect(rx,18,1,1),z+26,['tile'],[0])
                # Pot plants are connected through the slab's exposed studs.
                for px in (x,x+5):
                    m.part('3062',70,px,17,z+23)
                    m.part('3062',31,px,17,z+26)
                    m.part('32607',2,px,17,z+29,angle=0 if px==x else 180)
                    m.part('24866',14,px,17,z+30)
        if floor==1:
            for rx in (12,14): m.part('2432',0,rx,17,z+23)
    m.pieces.sort(key=lambda q:(q['step'],q['key']))
    return m,roof_report

def export(m, roof_report, output_dir=HERE, stem='facade', title='Cliffside Hotel — revised main building study'):
    output_dir.mkdir(parents=True,exist_ok=True)
    used=Counter(q['element'] for q in m.pieces)
    bom=[]; allocations=[]
    for e,n in sorted(used.items()):
        p=m.parts[e]
        assert n<=p['minimum'],e
        bom.append(dict(element=e,required=n,available=p['minimum'],name=p['name'],color=p['color']))
        left=n
        for src in sorted(p['sources'],key=lambda s:(-s['quantity'],s['set'],s['copy'])):
            take=min(left,src['quantity'])
            if take: allocations.append(dict(src,element=e,quantity=take))
            left-=take
        assert left==0,e
    data=dict(title=title,status='Visual review draft; consult current verification reports; physical assembly untested',pieces=m.pieces,roof=roof_report)
    for name,value in [('model',data),('bom',bom),('allocation',allocations)]:
        (output_dir/f'{name}.json').write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    lines=['0 '+title,'0 Physical assembly untested.']
    last=None
    for q in m.pieces:
        if last is not None and last!=q['step']: lines.append('0 STEP')
        last=q['step']; p=m.parts[q['element']]
        lines.append(f"0 {q['key']} ELEMENT {q['element']} MODULE {q['module']}")
        lines.append(f"1 {p['ldraw_color']} "+' '.join(f'{v:.8g}' for v in q['origin']+q['matrix'])+' '+p['ldraw'])
    (output_dir/f'{stem}.ldr').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(pieces=len(m.pieces),elements=len(used),modules=dict(Counter(q['module'] for q in m.pieces))),indent=2))

if __name__=='__main__': export(*author(),output_dir=HERE/'study')
