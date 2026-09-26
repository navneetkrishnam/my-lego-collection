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
          'water': '70AEB0', 'base': '555756', 'shadow': '706C61', 'garden': '809774'}
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


def joined_l_roof():
    """Continuous envelope over intersecting hip roofs; retains the L recess."""
    rects=[(20.5,8.5,59.5,33.5),(20.5,20,39.5,48.5)]
    def height(x,y):
        values=[.56*min(x-a,c-x,y-b,d-y)
                for a,b,c,d in rects if a-1e-8<=x<=c+1e-8 and b-1e-8<=y<=d+1e-8]
        return 82.75+max(values)
    for x in np.arange(20.5,59.5,.5):
        for y in np.arange(8.5,48.5,.5):
            if not any(a<x+.25<c and b<y+.25<d for a,b,c,d in rects):
                continue
            face([(x,height(x,y),y),(x,height(x,y+.5),y+.5),
                  (x+.5,height(x+.5,y+.5),y+.5),(x+.5,height(x+.5,y),y)],'roof')
    objects.append(dict(name='joined L roof',origin=[20.5,8.5,82.75],size=[39,40,7],color='roof'))


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
    box('display base',0,0,-1,120,88,1,'base')
    box('water envelope',1,1,0,118,86,.3,'water')
    # The high plateau ENDS beside the descending wing, never through it.
    box('main plateau',22,7,.3,60,47,39.7,'rock2')
    box('main courtyard',22,7,39.5,60,47,.5,'deck')
    box('upper wing access terrace support',82,40,.3,8,14,39.7,'rock2')
    box('upper wing access terrace',82,40,39.5,8,14,.5,'deck')
    box('side garden foundation',3,12,.3,19,38,39.7,'rock2')
    box('side garden paving',3,12,40,19,38,.5,'deck')
    box('villa front apron core',22,47,.3,21,14,39.7,'rock2')
    box('villa front apron',22,47,40,21,14,.5,'deck')
    # Garden beds are plain program markers, not detailed foliage.
    for x,y,w,d in [(5,15,14,5),(5,40,14,5),(4.5,22,2,16)]:
        box('side garden planter',x,y,40.5,w,d,1.2,'trim')
        box('side garden planting envelope',x+.3,y+.3,41.7,w-.6,d-.6,.25,'garden')
    for x,y,w,d in [(3,12,1.2,38),(3,12,19,1.2),(3,48.8,19,1.2),(22,59.8,20,1.2)]:
        box('villa terrace parapet',x,y,40.5,w,d,2.6,'trim')
    # Shared garden / pool terrace remains in front of the side of the complex.
    box('pool terrace core',60,54,.3,28,19,37.2,'rock2')
    for x,y,w,d in [(60,50,22,4),(60,54,28,2),(60,56,3,12),
                     (85,56,3,12),(60,68,28,5)]:
        box('pool terrace paving',x,y,38,w,d,.5,'deck')
    box('pool water',63,56,37.8,22,12,.12,'water')
    for x,y,w,d in [(62.4,55.4,23.2,.6),(62.4,68,23.2,.6),
                     (62.4,56,.6,12),(85,56,.6,12)]:
        box('pool coping',x,y,38.5,w,d,.3,'trim')
    box('pool front parapet',60,71.8,38.5,28,1.2,2.6,'trim')
    box('pool side parapet',86.8,58,38.5,1.2,13.8,2.6,'trim')
    box('pool garden bed',61,69.5,38.5,20,1.5,.8,'trim')
    box('pool planting envelope',61.3,69.8,39.3,19.4,.9,.2,'garden')
    # Stair offsets preserved from the accepted arrangement, moved right 8 studs.
    for i in range(18):
        top=39-i; yy=54+i*.78
        box('upper stair tread',44,yy,.3,14,.78,top-.3,'deck')
        for xx in (42.8,58):
            box('upper stair parapet',xx,yy,top,1.2,.78,2.1,'trim')
    box('stair landing',44,68.04,.3,21,6,21.7,'deck')
    for i in range(18):
        top=21-i; yy=74.04+i*.65
        box('lower stair tread',51,yy,.3,14,.65,top-.3,'deck')
        for xx in (49.8,65):
            box('lower stair parapet',xx,yy,top,1.2,.65,2.1,'trim')
    box('stair foot',51,85.74,.3,14,1.1,2.7,'deck')
    # Coarse cliff envelopes follow the new terrace outline. In front of the
    # descending wing they remain BELOW its lowest inhabited floor (z=12).
    rocks=[(1,13,4,20,26),(1,34,5,15,30),(4,50,10,10,32),
           (5,61,9,9,23),(12,52,10,12,35),(14,65,9,10,25),
           (23,61,9,9,32),(24,72,9,9,16),(32,61,10,10,30),
           (34,73,9,8,12),(13,79,12,6,8),(38,81,10,4,6),
           (66,74,8,7,18),(75,74,9,8,25),(83,74,9,7,15),
           (90,65,9,11,10),(99,62,10,10,8),(94,75,11,8,6),
           (108,32,3,20,10),(85,82,10,4,6),(3,72,8,8,12)]
    for idx,(x,y,w,d,h) in enumerate(rocks):
        box('cliff envelope '+str(idx),x,y,.3,w,d,h,'rock' if idx%2 else 'rock2')
    # Genuine L footprint: rear bar plus a forward left return. Garden is on
    # the outer left; the front recess forms the entrance court.
    building('main villa rear bar',22,10,40,36,22,42,3,[(3,6),(13,6),(24,8)])
    building('main villa forward return',22,32,40,16,15,42,3,[(2.5,4.5),(9,4.5)])
    for zz in (54,68):
        box('return balcony envelope',23.5,47,zz,13,2.5,.65,'trim')
        box('recessed villa balcony envelope',45,32,zz,10,2.5,.65,'trim')
    joined_l_roof()
    building('middle building',58,12,40,16,22,32,2,[(4,8)])
    roof('middle hip roof',56.8,10.8,72.75,18.4,24.4,5)
    # Three exposed floors, two below the upper court. Only a low rock plinth
    # exists beneath this footprint; no 40-stud plateau obscures the facade.
    wing_tri_start,wing_object_start=len(triangles),len(objects)
    box('descending wing plinth',82,28,.3,28,26,11.7,'rock2')
    building('descending wing lower floor',82,28,12,28,26,14,1,[(5,6),(17,6)])
    box('arcade rear',82,28,26,28,1.2,14)
    box('arcade right',108.8,29.2,26,1.2,24.8,14)
    box('arcade left',82,29.2,26,1.2,24.8,14)
    box('arcade floor',82,28,26,28,26,.5,'deck')
    for xx,ww in [(82,3),(95,3),(108,2)]:
        box('arcade pier',xx,52.8,26,ww,1.2,14)
    arch('arcade',85,52.8,26,10,12)
    arch('arcade',98,52.8,26,10,12)
    box('arcade lintel',82,52.8,38.6,28,1.2,1.4)
    # Balcony continues beyond the pool's edge, exposing the lower frontage.
    box('arcade balcony envelope',83,54,26,27,3,.8,'trim')
    box('arcade balcony parapet',89,56,26.8,21,1,1.8,'trim')
    building('descending wing upper floor',82,28,40,28,26,14,1,[(5,6),(17,6)])
    box('upper wing balcony envelope',83,54,40,27,3,.8,'trim')
    roof('descending wing hip roof',80.5,26.5,54.75,31,29,6)
    # Bring the wing forward and outside the pool's sightline. Its resulting
    # footprint is x=90..118, y=40..66; the adjacent access terrace stays z=40.
    for i in range(wing_tri_start,len(triangles)):
        color,tri=triangles[i]
        triangles[i]=(color,(np.array(tri)+[8,0,12]).tolist())
    for obj in objects[wing_object_start:]:
        obj['origin'][0]+=8
        obj['origin'][1]+=12
    for x,y,w,d,h in [(111,68,7,10,8),(104,77,10,7,7),(116,46,3,18,9)]:
        box('descending wing low rock',x,y,.3,w,d,h,'rock')
    # The pergola associated with the villa is wholly beside the villa.
    for name,x,y,w,d in [('side garden pergola',7,23,12,13),('middle pergola',59,36,13,11)]:
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
    dims={'status':'architectural proxy, not parts verified','base_studs':[120,88],
          'base_cm':[96,70.4],'maximum_height_studs':90.75,
          'maximum_height_cm':72.6,'main_villa_footprint_studs':[[22,10],[58,10],[58,32],[38,32],[38,47],[22,47]],
          'main_villa_wall_height_studs':42,
          'connector_wall_volume_studs':[16,22,32],
          'right_wing_wall_volume_studs':[28,26,42],
          'right_wing_floor_levels_studs':[12,26,40],
          'right_wing_footprint_bounds_studs':[90,40,118,66],
          'main_courtyard_level_studs':40,
          'villa_garden_bounds_studs':[3,12,22,50],
          'pool_studs':[22,12],'stair_clear_width_studs':14,
          'model_sha256':hashlib.sha256(data).hexdigest(),'triangles':len(triangles),
          'objects':objects}
    (HERE/'dimensions.json').write_text(json.dumps(dims,indent=2)+'\n')
    print(f'Exported {len(triangles)} proxy triangles; {dims["model_sha256"]}')


if __name__=='__main__':
    export()
