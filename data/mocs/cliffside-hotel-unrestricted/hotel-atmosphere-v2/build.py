#!/usr/bin/env python3
"""Programmed architectural blockout; geometry is still not LEGO part instances."""
import hashlib,json
from pathlib import Path
import numpy as np
import geometry as g
import layout as l
import exterior
import annex_exterior
import atmosphere
HERE=Path(__file__).resolve().parent

def slab(name,rects,holes,z,color='deck',thickness=.5):
    # Union grid yields each floor region exactly once, with real shaft/pool voids.
    xs=sorted({v for x,y,w,d in rects+holes for v in (x,x+w)})
    ys=sorted({v for x,y,w,d in rects+holes for v in (y,y+d)})
    for xa,xb in zip(xs,xs[1:]):
        for ya,yb in zip(ys,ys[1:]):
            x,y=(xa+xb)/2,(ya+yb)/2
            inside=lambda rs:any(a<x<a+w and b<y<b+d for a,b,w,d in rs)
            if inside(rects) and not inside(holes):g.box(name,xa,ya,z-thickness,xb-xa,yb-ya,thickness,color)

def wall3d(f,w):
    z=f['z'];axis=w['axis'];c=w['c'];t=w['thickness']
    opens=w['opens']
    breaks=sorted({w['a'],w['b'],*[v for o in opens for v in (o['a'],o['a']+o['w'])]})
    zs=sorted({0,w['height'],*[v for o in opens for v in (o['sill'],o['sill']+o['height'])]})
    for a,b in zip(breaks,breaks[1:]):
        for za,zb in zip(zs,zs[1:]):
            if any(o['a']<(a+b)/2<o['a']+o['w'] and o['sill']<(za+zb)/2<o['sill']+o['height'] for o in opens):continue
            if axis=='x':g.box(w['name'],a,c-t/2,z+za,b-a,t,zb-za)
            else:g.box(w['name'],c-t/2,a,z+za,t,b-a,zb-za)

def l_roof():
    rects=[(18.5,8.5,79.5,33.5),(18.5,8.5,45.5,53.5)]
    def h(x,y):return 82.75+max(.52*min(x-a,c-x,y-b,d-y) for a,b,c,d in rects if a-1e-8<=x<=c+1e-8 and b-1e-8<=y<=d+1e-8)
    for x in np.arange(18.5,79.5,.5):
        for y in np.arange(8.5,53.5,.5):
            if any(a<x+.25<c and b<y+.25<d for a,b,c,d in rects):
                g.face([(x,h(x,y),y),(x,h(x,y+.5),y+.5),(x+.5,h(x+.5,y+.5),y+.5),(x+.5,h(x+.5,y),y)],'roof')

def stair_core(x,y,z):
    # 35 plate-height risers between 14-stud floor levels, 18 + 17.
    # Bottom/top landing is y+12..14; intermediate landing y..3.
    for i in range(18):
        yy=y+11.5-i*.5;top=z+(i+1)*.4
        g.box('internal up flight',x,yy,z,4,.5,top-z,'deck')
    g.box('internal half landing',x,y,z,10,3,7.2,'deck')
    for i in range(17):
        yy=y+3+i*.5;top=z+7.2+(i+1)*.4
        g.box('internal return flight',x+6,yy,z,4,.5,top-z,'deck')
    g.box('internal top step',x+6,y+11.5,z,4,.5,14,'deck')

def rail(name,x,y,z,w,d,h=2.2):
    # Slender placeholder rail keeps the pool and lower service floors visible.
    for xx,yy in [(x,y),(x+w-1,y),(x,y+d-1),(x+w-1,y+d-1)]:
        g.box(name+' post',xx,yy,z,.5,.5,h,'trim')
    g.box(name+' front',x,y+d-.5,z+h,w,.5,.35,'trim')
    g.box(name+' left',x,y,z+h,.5,d,.35,'trim')
    g.box(name+' right',x+w-.5,y,z+h,.5,d,.35,'trim')

def author(cutaway=None):
    g.triangles.clear();g.objects.clear()
    g.box('base',0,0,-1,*l.BASE,1,'base')
    g.box('water',1,1,0,l.BASE[0]-2,l.BASE[1]-2,.25,'water')
    # Topography stops before the service wing; floors below the court stay exposed.
    for name,x,y,w,d,top in [('main rock core',20,8,58,48,39.5),('side garden core',2,12,18,40,39.5),
        ('cottage approach core',78,8,18,52,39.5),('cottage extension core',96,8,30,32,39.5),('pool terrace core',58,56,38,32,38),
        ('service low plinth',96,40,30,38,11.5)]:
        g.box(name,x,y,.25,w,d,top-.25,'rock2')
    # Support the deck up to its underside while retaining the recessed pool cavity.
    slab('pool deck support',[(58,54,38,34)],[l.PROGRAM['pool']],39.5,'rock2',1.5)
    # Do not fill the pool cavity to its water plane.
    for idx,(x,y,w,d,h) in enumerate([(1,18,4,27,28),(3,52,10,15,32),(10,61,10,15,29),
        (20,56,10,13,34),(26,69,10,17,27),(33,56,10,16,33),(33,80,9,17,15),
        (13,79,12,16,18),(23,98,14,10,7),(4,89,10,12,9),(37,101,6,10,6),
        (61,89,10,12,26),(72,89,10,15,24),(84,89,12,10,20),
        (96,76,12,12,10),(110,76,13,15,9),(101,96,14,10,7),(124,45,3,26,10)]):
        atmosphere.cliff('cliff envelope '+str(idx),x,y,.25,w,d,h,'rock' if idx%2 else 'rock2')
    # Straight ceremonial stair: both flights have precisely the same x extent.
    for i in range(48):
        yy=56+i+(6 if i>=24 else 0);top=40-(i+1)*.8
        g.box('straight exterior tread',44,yy,.25,14,1,top-.25,'deck')
        for xx in (42.8,58):g.box('stair parapet',xx,yy,top,1.2,1,2.1,'trim')
    g.box('straight stair landing',44,80,.25,14,6,20.55,'deck')
    g.box('stair foot',44,110,.25,14,2,1.35,'deck')
    # Floors, walls and openings all come from layout.py.
    for f in l.FLOORS:
        if cutaway is not None and f['z']>cutaway:continue
        slab(f['id']+' floor',f['rects'],f['holes'],f['z'])
        for surf in f.get('surfaces',[]):
            x,y,w,d=surf['rect'];g.box(surf['name'],x,y,f['z'],w,d,.05,surf['color'])
        for w in f['walls']:
            if w['name']=='open arcade front':
                for o in w['opens']:o['height']=12.6
            if cutaway==f['z']:
                low=dict(w,height=1.4,opens=[dict(o,sill=0,height=1.4) for o in w['opens'] if o['kind']=='door'])
                wall3d(f,low)
            else:wall3d(f,w)
        if f['id']=='salon' and cutaway!=26:
            for xx in (99,112):g.arch('salon arcade',xx,77,26,10,12,1)
        for b in f['balconies']:
            slab(b['name'],[b['rect']],[],f['z'])
            x,y,w,d=b['rect']
            for xx in (x+1,x+w/2,x+w-2):
                g.box('balcony support envelope',xx,y-2,f['z']-1,1,d+2,.5,'trim')
            if cutaway!=f['z']:
                (exterior.balcony if f['id'].startswith('main') else annex_exterior.terrace)(b['name'],*b['rect'][:2],f['z'],*b['rect'][2:])
        for item in f['furniture']:
            color='garden' if item['name'].startswith(('Side garden','Cottage garden')) else 'trim' if item['name']=='Pool lounger' else 'shadow'
            g.box(item['name'],item['rect'][0],item['rect'][1],f['z'],item['rect'][2],item['rect'][3],item['height'],color)
            if item['name']=='Pool lounger':
                x,y,w,d=item['rect'];z=f['z']+1
                if item.get('facing')=='west':
                    g.face([(x+w,z+1.5,y),(x+w,z+1.5,y+d),(x+w-2,z,y+d),(x+w-2,z,y)],'trim')
                else:g.face([(x,z+1.5,y),(x+w,z+1.5,y),(x+w,z,y+2),(x,z,y+2)],'trim')
    # Internal stair volumes sit in the declared shafts, with upper floor holes.
    for z in (40,54):
        if cutaway is None or z<cutaway:stair_core(45,11,z)
    if cutaway is None or cutaway>40:stair_core(104,9,40)
    for z in (12,26):
        if cutaway is None or z<cutaway:stair_core(115,41,z)
    # Main floor cornices follow only the L's actual external perimeter.
    if cutaway is None:
        for level in (54,68,82):
            z=level-.65 if level<82 else level
            for a,b in zip(l.MAIN_POLYGON,l.MAIN_POLYGON[1:]+l.MAIN_POLYGON[:1]):
                if a[1]==b[1]:g.box('L cornice',min(a[0],b[0])-.3,a[1]-.3,z,abs(a[0]-b[0])+.6,.6,.65,'trim')
                else:g.box('L cornice',a[0]-.3,min(a[1],b[1])-.3,z,.6,abs(a[1]-b[1])+.6,.65,'trim')
        l_roof()
        exterior.author()
        g.roof('garden cottage hip',80.5,6.5,68.5,47,31,6.5)
        g.roof('service pavilion hip',94.5,38.5,54.5,33,41,6.5)
        annex_exterior.author()
    # Pool: usable deck on all four sides, furniture outside a clear inner loop.
    px,py,pw,pd=l.PROGRAM['pool']
    g.box('pool water',px,py,38.8,pw,pd,.15,'water')
    for x,y,w,d in [(px-.5,py-.5,pw+1,.5),(px-.5,py+pd,pw+1,.5),(px-.5,py,.5,pd),(px+pw,py,.5,pd)]:
        g.box('pool coping',x,y,40,w,d,.3,'trim')
    # Edge guards leave all three public entrances and the stair threshold open.
    for name,x,y,w,d in l.PROGRAM['pergolas']:
        for xx in (x,x+w-1):
            for yy in (y,y+d-1):g.box(name+' post',xx,yy,40,1,1,10,'shadow')
        for yy in (y,y+d-1):g.box(name+' beam',x,yy,50,w,1,1,'shadow')
        for xx in (x,x+w-1):g.box(name+' beam',xx,y,50,1,d,1,'shadow')
    if cutaway is None:atmosphere.author()
    return g.triangles

def export(cutaway=None):
    author(cutaway)
    lines=['0 Cliffside Hotel / room-programmed blockout','0 PROXY GEOMETRY - NOT LEGO PART INSTANCES','0 BFC CERTIFY CCW']
    for color,tri in g.triangles:
        p=np.array(tri)[[0,2,1]]*[20,-20,20]
        assert np.isfinite(p).all() and np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0]))>1e-7
        lines.append('3 0x2'+g.COLORS[color]+' '+' '.join(f'{v:.5f}' for v in p.flat))
    stem='blockout' if cutaway is None else 'cutaway-'+str(cutaway)
    data=('\n'.join(lines)+'\n').encode();(HERE/(stem+'.ldr')).write_bytes(data)
    if cutaway is None:
        report=dict(status='architectural proxy',model_sha256=hashlib.sha256(data).hexdigest(),base_studs=l.BASE,
                    program=l.PROGRAM,floors=l.FLOORS,objects=g.objects)
        (HERE/'layout.json').write_text(json.dumps(report,indent=2)+'\n')
    print(stem,len(g.triangles),'triangles',hashlib.sha256(data).hexdigest())
def export_detail():
    # A deterministic spatial selection of the authored villa, for an unobstructed close view.
    author()
    selected=[]
    for color,tri in g.triangles:
        pts=np.array(tri)
        if np.all((pts[:,0]>=18)&(pts[:,0]<=80)&(pts[:,1]>=39.5)&(pts[:,2]>=8)&(pts[:,2]<=57)):
            selected.append((color,tri))
    lines=['0 Main villa exterior detail / architectural proxy','0 BFC CERTIFY CCW']
    for color,tri in selected:
        p=np.array(tri)[[0,2,1]]*[20,-20,20]
        lines.append('3 0x2'+g.COLORS[color]+' '+' '.join(f'{v:.5f}' for v in p.flat))
    data=('\n'.join(lines)+'\n').encode();(HERE/'villa-detail.ldr').write_bytes(data)
    print('villa-detail',len(selected),'triangles',hashlib.sha256(data).hexdigest())
if __name__=='__main__':
    export()
    export_detail()
