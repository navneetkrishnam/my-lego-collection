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


