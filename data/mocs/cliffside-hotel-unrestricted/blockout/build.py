#!/usr/bin/env python3
"""Architectural proxy geometry in stud units; NOT LEGO part placements."""
import hashlib
import json
import math
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
COLORS = {'wall': 'E4D7BD', 'trim': 'F1E6D0', 'roof': 'B47152',
          'rock': 'A8A69B', 'rock2': 'BBB5A6', 'deck': 'CEC2A9',
          'water': '70AEB0', 'base': '555756', 'shadow': '706C61'}
triangles = []
objects = []


def face(points, color):
    for i in range(1, len(points)-1):
        triangles.append((color, [points[0], points[i], points[i+1]]))


def box(name, x, y, z, w, d, h, color='wall'):
    assert min(w, d, h) > 0
    p = [(x,z,y),(x+w,z,y),(x+w,z,y+d),(x,z,y+d),
         (x,z+h,y),(x+w,z+h,y),(x+w,z+h,y+d),(x,z+h,y+d)]
    for ids in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7),(0,3,7,4),(1,5,6,2)]:
        face([p[i] for i in ids], color)
    objects.append(dict(name=name, origin=[x,y,z], size=[w,d,h], color=color))


def roof(name, x, y, z, w, d, rise):
    # Hipped envelope: continuous planes intentionally have no tile detail.
    a,b,c,e=(x,z,y),(x+w,z,y),(x+w,z,y+d),(x,z,y+d)
    inset=min(w,d)/2
    if abs(w-d)<1e-8:
        peak=(x+w/2,z+rise,y+d/2)
        polys=[(a,b,peak),(b,c,peak),(c,e,peak),(e,a,peak)]
    elif w > d:
        r,s=(x+inset,z+rise,y+d/2),(x+w-inset,z+rise,y+d/2)
        polys=[(a,b,s,r),(b,c,s),(c,e,r,s),(e,a,r)]
    else:
        r,s=(x+w/2,z+rise,y+inset),(x+w/2,z+rise,y+d-inset)
        polys=[(a,b,r),(b,c,s,r),(c,e,s),(e,a,r,s)]
    for p in polys:
        face(p,'roof')
    objects.append(dict(name=name, origin=[x,y,z],size=[w,d,rise],color='roof'))


def front_wall(name, x, y, z, w, h, holes, thickness=1.2):
    """Build planar wall around rectangular major openings, no fake decals."""
    xs=sorted({x,x+w,*[v for a,b,c,d in holes for v in (a,a+c)]})
    zs=sorted({z,z+h,*[v for a,b,c,d in holes for v in (b,b+d)]})
    for xa,xb in zip(xs,xs[1:]):
        for za,zb in zip(zs,zs[1:]):
            cx,cz=(xa+xb)/2,(za+zb)/2
            if not any(a < cx < a+c and b < cz < b+d for a,b,c,d in holes):
                box(name,xa,y,za,xb-xa,thickness,zb-za)


def arch(name,x,y,z,w,h,t=1.2):
    """Spandrel above a real semicircular void; piers authored separately."""
    r=w/2
    spring=z+h-r
    for i in range(16):
        a=math.pi-i*math.pi/16
        b=math.pi-(i+1)*math.pi/16
        xa,za=x+r+r*math.cos(a),spring+r*math.sin(a)
        xb,zb=x+r+r*math.cos(b),spring+r*math.sin(b)
        # Tiny extra headroom prevents degenerate peak facets.
        top=z+h+.6
        face([(xa,za,y),(xb,zb,y),(xb,top,y),(xa,top,y)],'wall')
        face([(xa,top,y+t),(xb,top,y+t),(xb,zb,y+t),(xa,za,y+t)],'wall')
        face([(xa,za,y),(xa,za,y+t),(xb,zb,y+t),(xb,zb,y)],'wall')


def building(name,x,y,z,w,d,h,storeys,bays):
    box(name+' back',x,y,z,w,1.2,h)
    # Side openings are spatial voids too, so side proportions can be judged.
    side_holes=[(y+off,z+floor*h/storeys+2.4,5.5,h/storeys-4.5)
                for floor in range(storeys) for off in (4,d-10)]
    ys=sorted({y+1.2,y+d,*[v for a,b,c,e in side_holes for v in (a,a+c)]})
    zs=sorted({z,z+h,*[v for a,b,c,e in side_holes for v in (b,b+e)]})
    for ya,yb in zip(ys,ys[1:]):
        for za,zb in zip(zs,zs[1:]):
            if not any(a<(ya+yb)/2<a+c and b<(za+zb)/2<b+e for a,b,c,e in side_holes):
                box(name+' left',x,ya,za,1.2,yb-ya,zb-za)
    box(name+' right',x+w-1.2,y+1.2,z,1.2,d-1.2,h)
    floor_h=h/storeys
    holes=[]
    for floor in range(storeys):
        for bx,bw in bays:
            entrance=name=='main villa' and floor==0 and bx==16
            holes.append((x+bx,z+.5 if entrance else z+floor*floor_h+2.4,
                          bw,11.5 if entrance else floor_h-4.5))
        box(name+' floor',x,y,z+floor*floor_h,w,d,.5,'deck')
        if floor:
            box(name+' floor line',x-.25,y-.25,z+floor*floor_h,w+.5,d+.5,.45,'trim')
    front_wall(name+' facade',x,y+d-1.2,z,w,h,holes)
    box(name+' cornice',x-.7,y-.7,z+h,w+1.4,d+1.4,.75,'trim')


def author():
    triangles.clear(); objects.clear()
    box('display base',0,0,-1,96,88,1,'base')
    box('water envelope',1,1,0,94,86,.3,'water')
    # Main load-bearing plateau envelope; front terminates behind the stair.
    box('upper plateau',8,7,.3,58,47,39.7,'rock2')
    box('right plateau back',66,7,.3,26,17,39.7,'rock2')
    box('right wing foundation',66,24,.3,28,30,37.7,'rock2')
    box('main courtyard',7,7,39.5,59,47,.5,'deck')
    box('right rear terrace',66,7,39.5,27,17,.5,'deck')
    box('left terrace core',5,38,.3,30,24,39.7,'rock2')
    box('left terrace paving',5,38,40,30,24,.5,'deck')
    # Pool terrace forms a broad projecting platform right of the stair.
    box('pool terrace core',54,54,.3,38,18,37.2,'rock2')
    # Pool opening: four paving rectangles leave an actual recess.
    for x,y,w,d in [(54,49,38,5),(54,54,5,12),(81,54,11,12),(54,66,38,6)]:
        box('pool terrace paving',x,y,38,w,d,.5,'deck')
    box('pool water',59,54,37.8,22,12,.12,'water')
    for x,y,w,d in [(58.4,53.4,23.2,.6),(58.4,66,23.2,.6),
                     (58.4,54,.6,12),(81,54,.6,12)]:
        box('pool coping',x,y,38.5,w,d,.3,'trim')
    # Retreating rock envelopes, deliberately broad and untextured.
    for idx,(x,y,w,d,h) in enumerate([
        (2,9,6,26,27),(1,35,6,17,21),(3,52,6,16,24),
        (7,62,9,9,32),(5,70,10,7,19),(12,69,10,10,24),
        (19,62,9,9,33),(21,71,9,10,16),(28,60,7,12,29),
        (28,73,9,8,10),(11,80,13,5,7),(33,79,8,6,6),
        (57,73,8,9,18),(65,73,9,8,27),(73,72,9,8,22),
        (83,71,10,8,29),(89,58,5,14,27),(83,80,10,5,10),
        (67,81,12,4,8)]):
        box('cliff envelope '+str(idx),x,y,.3,w,d,h,'rock' if idx%2 else 'rock2')
    # Continuous 14-stud-wide staircase: 36 risers with broad central landing.
    for i in range(18):
        top=40-(i+1)
        yy=54+i*.78
        box('upper stair tread',36,yy,.3,14,.78,top-.3,'deck')
        for xx in (34.8,50):
            box('upper stair parapet',xx,yy,top,1.2,.78,2.1,'trim')
    box('stair landing',36,68.04,.3,21,6,21.7,'deck')
    for i in range(18):
        top=22-(i+1)
        yy=74.04+i*.65
        box('lower stair tread',43,yy,.3,14,.65,top-.3,'deck')
        for xx in (41.8,57):
            box('lower stair parapet',xx,yy,top,1.2,.65,2.1,'trim')
    box('stair foot',43,85.74,.3,14,1.1,2.7,'deck')
    # Retaining walls emphasize the terrace edge; balusters come later.
    for x,y,w,d,z in [(5,60.8,29,1.2,40.5),(5,38,1.2,22.8,40.5),
                       (58.5,70.8,33.5,1.2,38.5),(90.8,50,1.2,20.8,38.5)]:
        box('terrace parapet',x,y,z,w,d,2.6,'trim')
    # Three visibly staggered architectural volumes.
    building('main villa',10,10,40,40,28,42,3,[(4,8),(16,8),(28,8)])
    for zz in (54,68):
        for xx in (13,25):
            box('main balcony envelope',xx,38,zz,10,2.5,.65,'trim')
    roof('main hip roof',8.5,8.5,82.75,43,31,7)
    building('middle building',50,12,40,16,22,32,2,[(4,8)])
    roof('middle hip roof',48.8,10.8,72.75,18.4,24.4,5)
    # Right wing open arcade below an upper room volume.
    box('right wing rear',66,24,38,28,1.2,14)
    box('right wing left',66,25.2,38,1.2,24.8,14)
    box('right wing right',92.8,25.2,38,1.2,24.8,14)
    box('arcade floor',66,24,38,28,26,.5,'deck')
    for xx,ww in [(66,3),(79,3),(92,2)]:
        box('arcade pier',xx,48.8,38,ww,1.2,14)
    arch('arcade',69,48.8,38,10,12)
    arch('arcade',82,48.8,38,10,12)
    box('arcade lintel',66,48.8,50.6,28,1.2,1.4)
    building('right wing upper',66,24,52,28,26,14,1,[(5,6),(17,6)])
    box('wing balcony envelope',67,50,52,26,3,.8,'trim')
    roof('right hip roof',64.5,22.5,66.75,31,29,6)
    # Sheltered terrace envelopes: slender posts and roofless beam frames.
    for name,x,y,w,d in [('left dining pergola',6,41,15,12),('middle pergola',51,36,13,11)]:
        for xx in (x,x+w-1):
            for yy in (y,y+d-1):
                box(name+' post',xx,yy,40.5,1,1,10,'shadow')
        for yy in (y,y+d-1):
            box(name+' beam',x,yy,50.5,w,1,1,'shadow')
        for xx in (x,x+w-1):
            box(name+' beam',xx,y,50.5,1,d,1,'shadow')
    return triangles


def export():
    author()
    lines=['0 Cliffside Hotel / unrestricted composition study',
           '0 PROXY TRIANGLE GEOMETRY - NOT A LEGO PARTS MODEL',
           '0 Units: 20 LDU per stud in all axes; provisional scale',
           '0 BFC CERTIFY CCW']
    for color,tri in triangles:
        # World x/up/depth -> LDraw x/down/depth reverses handedness.
        p=np.array(tri)[[0,2,1]]*np.array([20,-20,20])
        assert np.isfinite(p).all()
        assert np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0])) > 1e-6
        lines.append('3 0x2'+COLORS[color]+' '+' '.join(f'{v:.5f}' for v in p.flat))
    data=('\n'.join(lines)+'\n').encode()
    (HERE/'blockout.ldr').write_bytes(data)
    dims={'status':'architectural proxy, not parts verified','base_studs':[96,88],
          'base_cm':[76.8,70.4],'maximum_height_studs':90.75,
          'maximum_height_cm':72.6,'main_villa_wall_volume_studs':[40,28,42],
          'connector_wall_volume_studs':[16,22,32],
          'right_wing_wall_volume_studs':[28,26,28],
          'pool_studs':[22,12],'stair_clear_width_studs':14,
          'model_sha256':hashlib.sha256(data).hexdigest(),'triangles':len(triangles),
          'objects':objects}
    (HERE/'dimensions.json').write_text(json.dumps(dims,indent=2)+'\n')
    print(f'Exported {len(triangles)} proxy triangles; {dims["model_sha256"]}')


if __name__=='__main__':
    export()
