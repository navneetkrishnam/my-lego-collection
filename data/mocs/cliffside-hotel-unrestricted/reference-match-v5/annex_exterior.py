"""Cottage/service appearance layers over the unchanged v6 architectural layout."""
from contextlib import contextmanager
from copy import deepcopy
from types import SimpleNamespace
import math
import numpy as np
import geometry as g
import layout as l
import exterior as villa

FACES={'cottage west':-1,'cottage east':1,'cottage rear':-1,'cottage garden front':1,
       'service west':-1,'service east':1,'service rear':-1,'service front':1,'open arcade front':1}

def tag_new(start,prefix):
    for o in g.objects[start:]:
        if o['name'].startswith('villa '):o['name']=prefix+' '+o['name'][6:]

@contextmanager
def facade_context(floors,prefix):
    # Adapt the existing window/door detailing without changing the authored layout.
    saved_layout,saved_faces=villa.l,villa.FACES
    copies=deepcopy(floors)
    for f in copies:
        f['id']='main-adapter'
        f['walls']=[w for w in f['walls'] if w['name'] in FACES and w['name']!='open arcade front']
    start=len(g.objects)
    villa.l=SimpleNamespace(FLOORS=copies);villa.FACES=FACES
    try:yield
    finally:
        villa.l=saved_layout;villa.FACES=saved_faces
        tag_new(start,prefix)

def masonry(floors,prefix):
    with facade_context(floors,prefix):
        for f in floors:
            for w in f['walls']:
                if w['name'] not in FACES:continue
                # Joints stop before openings; the existing arcade void stays open.
                for row,z in enumerate(np.arange(f['z']+1,f['z']+13,2)):
                    intervals=[(w['a']+.12,w['b']-.12)]
                    for o in w['opens']:
                        if f['z']+o['sill']-.7<z<f['z']+o['sill']+o['height']+.8:
                            lo,hi=o['a']-.8,o['a']+o['w']+.8;parts=[]
                            for a,b in intervals:
                                if hi<=a or lo>=b:parts.append((a,b));continue
                                if a<lo:parts.append((a,lo))
                                if b>hi:parts.append((hi,b))
                            intervals=parts
                    for a,b in intervals:
                        if b-a>.1:villa.localbox(w,'stone course',a,float(z),b-a,.035,offset=.004,depth=.018,color='joint')
                    for u in np.arange(w['a']+1+2*(row%2),w['b']-1,4):
                        if any(o['a']-.8<u<o['a']+o['w']+.8 and f['z']+o['sill']-.7<z+1<f['z']+o['sill']+o['height']+1 for o in w['opens']):continue
                        villa.localbox(w,'stone joint',float(u),float(z),.028,1.95,offset=.004,depth=.018,color='joint')
                # Corner stones fit on the solid end piers; none cross an opening.
                for row,z in enumerate(np.arange(f['z']+.4,f['z']+13,2)):
                    length=1.3 if row%2 else 1.9
                    for a in (w['a'],w['b']-length):
                        if any(a<o['a']+o['w']+.55 and a+length>o['a']-.55 for o in w['opens']):continue
                        villa.localbox(w,'corner quoin',a,float(z),length,1.7,depth=.12)
                villa.localbox(w,'floor cornice',w['a']-.12,f['z']+13.35,w['b']-w['a']+.24,.5,depth=.55)
                if f['z']==max(q['z'] for q in floors):
                    for u in np.arange(w['a']+.5,w['b']-.5,1.6):
                        villa.localbox(w,'cornice dentil',float(u),f['z']+12.7,.75,.6,depth=.4)


def tiled_hip(prefix,x,y,z,w,d,rise):
    inset=min(w,d)/2
    h=lambda xx,yy:z+rise*min(xx-x,x+w-xx,yy-y,y+d-yy)/inset
    count=0
    for ix,xx in enumerate(np.arange(x,x+w,1)):
        for iy,yy in enumerate(np.arange(y,y+d,1.8)):
            xa,xb,ya,yb=xx+.04,min(xx+1,x+w)-.04,yy+.04,min(yy+1.8,y+d)-.04
            if xb<=xa or yb<=ya:continue
            cx,cy=(xa+xb)/2,(ya+yb)/2
            dx=h(cx+.01,cy)-h(cx-.01,cy);dy=h(cx,cy+.01)-h(cx,cy-.01)
            color='tile'+str(1+(ix*7+iy*3)%4)
            for j in range(5):
                u,v=j/5,(j+1)/5;zu=.12+.24*math.sin(math.pi*u);zv=.12+.24*math.sin(math.pi*v)
                if abs(dx)>abs(dy):
                    a,b=ya+(yb-ya)*u,ya+(yb-ya)*v
                    p=[(xa,h(xa,a)+zu,a),(xb,h(xb,a)+zu,a),(xb,h(xb,b)+zv,b),(xa,h(xa,b)+zv,b)]
                else:
                    a,b=xa+(xb-xa)*u,xa+(xb-xa)*v
                    p=[(a,h(a,ya)+zu,ya),(b,h(b,ya)+zv,ya),(b,h(b,yb)+zv,yb),(a,h(a,yb)+zu,yb)]
                g.face(p,color)
            count+=1
    g.objects.append(dict(name=prefix+' roof tile field',tile_count=count,roof_rect=(x,y,w,d),roof_base=z))
    axis='x' if w>=d else 'y';c=y+d/2 if axis=='x' else x+w/2
    a=x+inset if axis=='x' else y+inset;b=x+w-inset if axis=='x' else y+d-inset
    for u in np.arange(a,b,1):
        for j in range(6):
            t,tt=j*math.pi/6,(j+1)*math.pi/6
            cross=[c+.32*math.cos(t),c+.32*math.cos(tt)];up=[.4+.28*math.sin(t),.4+.28*math.sin(tt)]
            p=[]
            for along,k in [(u,0),(min(u+.96,b),0),(min(u+.96,b),1),(u,1)]:
                xx,yy=(along,cross[k]) if axis=='x' else (cross[k],along)
                p.append((xx,h(xx,yy)+up[k],yy))
            g.face(p,'tile3')
    g.objects.append(dict(name=prefix+' ridge covers',axis=axis,start=a,end=b))

    # Cover the diagonal junctions where the tile field changes fall direction.
    # A raised curved cap stays above the barrel tiles on both adjoining planes.
    endpoints=[((x,y),(x+inset,y+inset)),
               ((x+w,y),(x+w-inset,y+inset)),
               ((x+w,y+d),(x+w-inset,y+d-inset)),
               ((x,y+d),(x+inset,y+d-inset))]
    for (ax,ay),(bx,by) in endpoints:
        length=math.hypot(bx-ax,by-ay);vx,vy=(bx-ax)/length,(by-ay)/length
        nx,ny=-vy,vx
        for along in np.arange(0,length,1):
            end=min(along+.97,length)
            for j in range(6):
                t,tt=j*math.pi/6,(j+1)*math.pi/6
                cross=[.4*math.cos(t),.4*math.cos(tt)]
                up=[.42+.3*math.sin(t),.42+.3*math.sin(tt)]
                points=[]
                for distance,k in [(along,0),(end,0),(end,1),(along,1)]:
                    xx,yy=ax+vx*distance+nx*cross[k],ay+vy*distance+ny*cross[k]
                    points.append((xx,h(xx,yy)+up[k],yy))
                g.face(points,'tile3')
    g.objects.append(dict(name=prefix+' hip covers',seams=4))


def terrace(name,x,y,z,w,d):
    start=len(g.objects);villa.balcony(name,x,y,z,w,d);tag_new(start,'services')


def author():
    groups=[('cottage',[f for f in l.FLOORS if f['id'].startswith('cottage')]),
            ('services',[f for f in l.FLOORS if f['id'] in ('dining','salon','spa')])]
    for prefix,floors in groups:
        with facade_context(floors,prefix):villa.windows()
        masonry(floors,prefix)
    # Stone rings follow the existing semicircular voids; no glazing closes the arcade.
    salon=next(f for f in l.FLOORS if f['id']=='salon')
    w=next(w for w in salon['walls'] if w['name']=='open arcade front')
    saved=villa.FACES;villa.FACES=FACES;start=len(g.objects)
    try:
        for u in (99,112):
            villa.arc(w,'arcade stone ring',u+5,33,5,.55,offset=.03,depth=.35)
            for a in (u-.55,u+10):villa.localbox(w,'arcade jamb',a,26,.55,7,depth=.35)
            for a in (u-.8,u+10):villa.localbox(w,'arcade impost',a,32.65,.8,.4,depth=.5)
    finally:villa.FACES=saved;tag_new(start,'services')
    # A planted window box emphasizes the cottage bedroom's garden outlook.
    g.box('cottage garden window box',86,36.1,55.3,7,.7,.65,'wood')
    for i in range(12):
        xx=86.2+i*.55
        g.box('cottage garden window foliage',xx,36.12,55.95,.4,.5,.45,'leaf')
        if i%2==0:g.box('cottage garden window flowers',xx+.08,36.18,56.4,.22,.3,.18,'flower')
    tiled_hip('cottage',80.5,6.5,68.5,47,31,6.5)
    tiled_hip('services',94.5,38.5,54.5,33,41,6.5)
