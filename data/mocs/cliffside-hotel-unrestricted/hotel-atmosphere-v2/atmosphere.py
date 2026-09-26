"""Deterministic planted exterior study. Authored meshes, not LEGO part instances."""
import math, random
import numpy as np
import geometry as g
import layout as l

PALETTE=dict(foliage_dark='244836',foliage_mid='426445',foliage_light='698450',
    rose='BE527C',rose_light='E39AAC',cream_flower='F2DFBB',flower_gold='CBA355',
    pot='AF613F',pot_edge='C08055',soil='534B36',timber='795335',
    paving1='D1BE9C',paving2='C6B28F',paving3='DFCFB0',paving4='BBAA91',
    cliff1='9D9D90',cliff2='B8B3A4',cliff3='C7C0AC',cliff4='AAA798',
    masonry1='CEC0A4',masonry2='DCD0B6',masonry3='BDB39B')
g.COLORS.update(PALETTE)
rng=random.Random(9247)
LANDSCAPE_FURNITURE=[
 dict(name='Garden bistro table',rect=(9.5,28.5,3,3),height=2.3),
 dict(name='Garden bistro chair west',rect=(7.3,28.9,1.5,2),height=2.7),
 dict(name='Garden bistro chair east',rect=(13.3,28.9,1.5,2),height=2.7),
 dict(name='Cottage garden bench',rect=(85.2,41,6.5,1.5),height=2.5)]

def point(p):return (p[0],p[2],p[1])
def face(ps,color):g.face([point(p) for p in ps],color)

def tube(a,b,r,color,n=7):
    a,b=np.array(a,float),np.array(b,float);v=b-a;v/=np.linalg.norm(v)
    helper=np.array([0,0,1] if abs(v[2])<.9 else [1,0,0])
    u=np.cross(v,helper);u/=np.linalg.norm(u);w=np.cross(v,u)
    rings=[[p+r*(math.cos(t)*u+math.sin(t)*w) for t in np.arange(n)*2*math.pi/n] for p in (a,b)]
    for i in range(n):face([rings[0][i],rings[0][(i+1)%n],rings[1][(i+1)%n],rings[1][i]],color)
    face(rings[0][::-1],color);face(rings[1],color)

def spindle(x,y,z,profile,color='stone',n=8):
    rings=[[(x+r*math.cos(t),y+r*math.sin(t),z+h) for t in np.arange(n)*2*math.pi/n] for h,r in profile]
    for a,b in zip(rings,rings[1:]):
        for i in range(n):face([a[i],a[(i+1)%n],b[(i+1)%n],b[i]],color)
    face(rings[0][::-1],color);face(rings[-1],color)

def leaf(x,y,z,s=1):
    angle=rng.random()*math.tau;dx,dy=math.cos(angle)*s*.5,math.sin(angle)*s*.5
    p=[(x,y,z+s*.65),(x+dx,y+dy,z),(x,y,z-s*.45),(x-dx,y-dy,z)]
    front=(x-dy*.4,y+dx*.4,z+.04);back=(x+dy*.2,y-dx*.2,z)
    color=rng.choice(['foliage_dark','foliage_mid','foliage_mid','foliage_light'])
    for i in range(4):
        face([p[i],p[(i+1)%4],front],color);face([p[(i+1)%4],p[i],back],color)

def flower(x,y,z,s=.65):
    color=rng.choice(['rose','rose','rose_light','cream_flower'])
    # Small five-petal rosette, tilted toward the principal front viewing direction.
    for k in range(5):
        a=k*math.tau/5;cx=x+math.cos(a)*s*.45;cz=z+math.sin(a)*s*.45
        ps=[(cx+math.cos(t)*s*.32,y+.08*math.sin(t),cz+math.sin(t)*s*.32) for t in np.arange(6)*math.tau/6]
        face(ps,color)
    face([(x+math.cos(t)*s*.16,y-.03,z+math.sin(t)*s*.16) for t in np.arange(6)*math.tau/6],'flower_gold')

def cluster(x,y,z,r=1,bloom=.3):
    for i in range(12):
        a=rng.random()*math.tau;rad=r*math.sqrt(rng.random());xx=x+rad*math.cos(a);yy=y+rad*.7*math.sin(a);zz=z+rng.uniform(-.4,.7)*r
        leaf(xx,yy,zz,rng.uniform(.65,1.05))
        if rng.random()<bloom:flower(xx,yy-.18,zz+.35,rng.uniform(.55,.85))


def obstacle(name,x,y,z,w,d,h):
    g.objects.append(dict(name='atmosphere obstacle '+name,origin=[x,y,z],size=[w,d,h],collision_rect=[x,y,w,d],level=z))


def pot(x,y,z,r=.85,height=1.7,bloom=.6):
    spindle(x,y,z,[(0,r*.6),(.16,r*.68),(height*.8,r),(height*.9,r*1.08),(height,r*1.08)],'pot')
    spindle(x,y,z+height,[(0,r*.91),(.035,r*.91)],'soil')
    for i in range(3):cluster(x+rng.uniform(-.4,.4),y+rng.uniform(-.25,.25),z+height+.55+i*.55,r,bloom)
    g.objects.append(dict(name='atmosphere terracotta planted pot',origin=[x-r,y-r,z],size=[2*r,2*r,height+3]))


def vine(name,points,r=.9,bloom=.45):
    for a,b in zip(points,points[1:]):
        tube(a,b,.065,'timber',5)
        distance=math.dist(a,b);count=max(2,math.ceil(distance/.9))
        for i in range(count):
            t=i/count;v=[a[k]+(b[k]-a[k])*t for k in range(3)]
            cluster(*v,r,bloom)
    g.objects.append(dict(name='atmosphere climber '+name,root=list(points[0]),end=list(points[-1]),flower_density=bloom))


def cypress(x,y,z,height=19):
    tube((x,y,z),(x,y,z+height-2),.25,'timber')
    for dz in np.arange(1.5,height,1.25):
        rad=1.75*math.sin(math.pi*(dz/height))**.55
        spindle(x,y,z+dz,[(0,max(.2,rad*.72)),(.7,max(.2,rad)),(2.5,max(.15,rad*.4))],'foliage_dark',9)
        for k in range(9):
            a=rng.random()*math.tau;leaf(x+rad*math.cos(a),y+rad*math.sin(a),z+dz+rng.random()*1.8,.9)
    g.objects.append(dict(name='atmosphere cypress',origin=[x-2,y-2,z],size=[4,4,height+2]))
    obstacle('cypress',x-2,y-2,z,4,4,height+2)


def cliff(name,x,y,z,w,d,h,color):
    # Replace a block silhouette with staggered, faceted strata INSIDE its envelope.
    seed=int(name.rsplit(' ',1)[1]);rr=random.Random(700+seed)
    cols=max(1,round(w/3));rows=max(1,round(d/4));dz=4.5
    for ix in range(cols):
        for iy in range(rows):
            cw,cd=w/cols,d/rows;xx=x+ix*cw;yy=y+iy*cd
            top=h*(.86+.14*rr.random())
            for zz in np.arange(0,top,dz):
                hh=min(dz,top-zz)
                if hh<.15:continue
                cut=.15+rr.random()*.35
                ring=[(cut,0),(cw-cut,0),(cw,cut),(cw,cd-cut),(cw-cut,cd),(cut,cd),(0,cd-cut),(0,cut)]
                bottom=[(xx+a,yy+b,z+zz) for a,b in ring]
                inset=.08+rr.random()*.24
                upper=[(xx+cw/2+(a-cw/2)*(1-inset),yy+cd/2+(b-cd/2)*(1-inset),z+zz+hh) for a,b in ring]
                col='cliff'+str(1+rr.randrange(4))
                face(upper,col)
                for k in range(8):face([bottom[k],bottom[(k+1)%8],upper[(k+1)%8],upper[k]],col)
            if ix==cols//2 and iy==rows-1:
                g.objects.append(dict(name='atmosphere rock planting anchor',origin=[xx+cw*.5,yy+cd*.5,z+top],front=yy+cd,height=top))
    # Keep the same planning envelope as a record, explicitly mark geometry treatment elsewhere.
    g.objects.append(dict(name=name,origin=[x,y,z],size=[w,d,h],color=color))


def balustrade(name,axis,c,a,b,z):
    # Mounted on existing solid guards; no additional footprint on the walking deck.
    box=lambda u,zz,w,h,depth:g.box('atmosphere '+name,u if axis=='x' else c-depth/2,c-depth/2 if axis=='x' else u,zz,w if axis=='x' else depth,depth if axis=='x' else w,h,'stone')
    box(a,z,b-a,.25,.8);box(a,z+2.05,b-a,.35,.95)
    for u in np.arange(a+.6,b-.3,1.5):
        xx,yy=(u,c) if axis=='x' else (c,u)
        spindle(xx,yy,z+.25,[(0,.25),(.22,.25),(.42,.15),(.8,.29),(1.05,.3),(1.35,.14),(1.8,.24)],'stone')
    for u in np.arange(a,b+.01,6):box(float(u)-.35,z,.7,2.4,.7)


def lantern(x,y,z):
    spindle(x,y,z,[(0,.43),(.3,.43),(.4,.28),(.65,.28)],'iron')
    g.box('atmosphere lantern glass',x-.24,y-.24,z+.65,.48,.48,.85,'lamp')
    for dx in (-.28,.22):
        for dy in (-.28,.22):g.box('atmosphere lantern frame',x+dx,y+dy,z+.6,.06,.06,1,'iron')
    spindle(x,y,z+1.6,[(0,.46),(.15,.46),(.5,.07)],'iron')
    g.objects.append(dict(name='atmosphere lantern',origin=[x-.46,y-.46,z],size=[.92,.92,2.1]))


def paving():
    site=next(f for f in l.FLOORS if f['id']=='site')
    zones=site['rects'];pool=l.PROGRAM['pool']
    blocked=[pool]+[o['rect'] for o in site['furniture']]+[s['rect'] for s in site.get('surfaces',[])]
    # Fully contained pavers stop at every void, wall, garden bed and furniture envelope.
    for ix,x in enumerate(np.arange(2,126,2)):
        for iy,y in enumerate(np.arange(10,88,2)):
            a,b,w,d=float(x+.08),float(y+.08),1.84,1.84
            if not any(a>=xx and b>=yy and a+w<=xx+ww and b+d<=yy+dd for xx,yy,ww,dd in zones):continue
            if any(min(a+w,xx+ww)>max(a,xx) and min(b+d,yy+dd)>max(b,yy) for xx,yy,ww,dd in blocked):continue
            if any((q['axis']=='x' and b<=q['c']+.3 and b+d>=q['c']-.3 and a<q['b'] and a+w>q['a']) or (q['axis']=='y' and a<=q['c']+.3 and a+w>=q['c']-.3 and b<q['b'] and b+d>q['a']) for q in site['walls']):continue
            g.box('atmosphere courtyard paver',a,b,40.015,w,d,.04,'paving'+str(1+(ix*7+iy*3)%4))


def retaining_walls():
    for axis,c,a,b,top in [('x',56,20,44,39.5),('x',88,58,96,39.5),('y',2,12,52,39.5)]:
        for row,z in enumerate(np.arange(2,top-1,2)):
            for u in np.arange(a,b,4):
                aa=float(u)+(.5 if row%2 else 0);ww=min(3.9,b-aa)
                if ww<.2:continue
                if axis=='x':g.box('atmosphere retaining ashlar',aa,c+.015,z,ww,.12,1.9,'masonry'+str(1+(row+int(u))%3))
                else:g.box('atmosphere retaining ashlar',c-.135,aa,z,.12,ww,1.9,'masonry'+str(1+(row+int(u))%3))


def author():
    global rng;rng=random.Random(9247)
    paving();retaining_walls()
    # Full-length overflowing rail planters on each guest balcony and the service loggia.
    for f in l.FLOORS:
        for b in f['balconies']:
            x,y,w,d=b['rect'];z=f['z']
            g.box('atmosphere rail flower trough',x+.7,y+d-.2,z+1.25,w-1.4,.65,.55,'pot')
            for xx in np.arange(x+1,x+w-1,.85):cluster(float(xx),y+d+.05,z+2.3,.9,.7)
            for xx in np.arange(x+1.5,x+w-1,3):vine('balcony cascade',[(xx,y+d+.25,z+1.8),(xx+.5,y+d+.4,z-.6),(xx-.25,y+d+.4,z-2.1)],.6,.4)
    # Timber rafters and flowering canopies grow from the existing pergola posts.
    for name,x,y,w,d in l.PROGRAM['pergolas']:
        for xx in np.arange(x-.3,x+w+.3,1.5):g.box('atmosphere pergola rafter',float(xx),y-.6,51,.45,d+1.2,.65,'timber')
        for yy in np.arange(y,y+d,1.8):g.box('atmosphere pergola lattice',x-.6,float(yy),51.65,w+1.2,.22,.22,'timber')
        for xx in np.arange(x+.2,x+w-.1,1.3):
            for yy in np.arange(y+.2,y+d-.1,1.3):
                if rng.random()<.68:cluster(float(xx),float(yy),52.1,.85,.32)
        for xx,yy in [(x+.35,y+.35),(x+w-.65,y+d-.65)]:
            vine(name+' post',[(xx,yy,41),(xx+.15,yy,45),(xx-.1,yy,49),(xx+.3,yy,52)],.5,.35)
        for xx in (x+.5,x+w-.5):lantern(xx,y+.5,48)
    # Trees and planting stay in the existing raised beds, away from the arrival routes.
    for x,y,h in [(6.3,17.5,24),(12.5,17.5,19),(6.5,47.5,14)]:cypress(x,y,41,h)
    site=next(f for f in l.FLOORS if f['id']=='site')
    for bed in [o for o in site['furniture'] if 'garden' in o['name'].lower()]:
        x,y,w,d=bed['rect']
        for xx in np.arange(x+.5,x+w-.3,1):
            for yy in np.arange(y+.3,y+d-.15,1):cluster(float(xx),float(yy),41.65,.65,.55)
    for x,y in [(15.5,17.5),(15.5,47.5),(93,38)]:pot(x,y,41,.7,1.45,.7)
    # Climbers occupy solid facade piers. Wall openings are screened below.
    facade_vine('main west',30,40,80,'villa garden climber',1.9)
    facade_vine('long-arm front',41,40,80,'villa outer climber',1.05)
    facade_vine('suite front',59,40,79,'courtyard climbing rose',1.0)
    facade_vine('suite front',76.7,40,78,'suite corner climber',.65)
    facade_vine('cottage garden front',96.3,40,67,'cottage garden rose',1.25)
    facade_vine('cottage garden front',123.7,40,67,'cottage outer rose',.7)
    facade_vine('service front',110.3,12,52,'service front rose',.85)
    facade_vine('service front',124,12,52,'service corner rose',1.05)
    # Cascades root in narrow parapet planters on the OUTSIDE of the pool/garden guards.
    for x in (62,70,78,87,93):
        g.box('atmosphere parapet trough',x-.7,88.05,42.25,1.4,1.4,.65,'pot')
        drop=rng.uniform(17,28);bend=rng.uniform(-1.8,1.8)
        vine('pool retaining cascade',[(x,89.1,43.3),(x-.5,89.2,37),(x+bend,89.2,30),(x+bend*.5,89.2,drop)],1.15,.48)
        vine('pool cascade branch',[(x-.5,89.2,37),(x-1.8,89.2,34),(x-2.3,89.2,29)],.8,.4)
    for y in (19,31,43):
        vine('garden retaining cascade',[(1.75,y,42),(1.3,y+1.2,34),(1.2,y-.9,26),(1.3,y+.6,rng.uniform(13,22))],.72,.4)
    for w in site['walls']:
        if 'guard' in w['name'].lower():balustrade(w['name'],w['axis'],w['c'],w['a'],w['b'],42.2)
    # Stair-edge lamp piers and planters sit entirely outside the 14-stud tread width.
    for i in (0,12,24,36,47):
        y=56+i+(6 if i>=24 else 0);z=40-(i+1)*.8
        for x in (43.4,58.6):
            g.box('atmosphere stair pier',x-.55,y,z,1.1,1,2.6,'stone')
            lantern(x,y+.5,z+2.6)
    # Rock planting is rooted at the actual authored top of a faceted stratum.
    for o in list(g.objects):
        if o['name']!='atmosphere rock planting anchor':continue
        x,y,z=o['origin'];front=o['front']
        for dx,dy,dz in [(0,0,.4),(.65,0,1.0),(-.65,.1,.8)]:cluster(x+dx,y+dy,z+dz,1.15,.14)
        if o['height']>12:
            vine('rock crevice spill',[(x,y,z+.4),(x,front+.25,z),(x+.7,front+.35,z-3),(x-.6,front+.35,z-6)],.85,.18)
    garden_furniture()
    g.objects.append(dict(name='atmosphere scope',seed=9247,layout='unchanged v6',cliff_geometry='faceted within baseline envelopes'))


def facade_vine(wallname,u,z0,z1,name,r):
    import exterior,annex_exterior
    faces={**exterior.FACES,**annex_exterior.FACES}
    walls=[(f,w) for f in l.FLOORS for w in f['walls'] if w['name']==wallname or (wallname=='service front' and w['name']=='open arcade front')]
    w=walls[0][1];sgn=faces[w['name']];c=w['c']+sgn*(w['thickness']/2+.5)
    position=lambda uu,z:(uu,c,z) if w['axis']=='x' else (c,uu,z)
    pts=[]
    for z in np.arange(z0+1,z1,1.8):
        uu=u+min(1.2,r*.6)*math.sin(z*.35)
        # Allow full leaf/flower radius plus surrounds, preserving every window/door.
        blocked=any(f['z']+o['sill']-r-.9<z<f['z']+o['sill']+o['height']+r+.9 and o['a']-r-.6<uu<o['a']+o['w']+r+.6 for f,ww in walls for o in ww['opens'])
        if blocked:
            if len(pts)>1:vine(name,pts,r,.58)
            pts=[];continue
        pts.append(position(uu,float(z)))
    if len(pts)>1:vine(name,pts,r,.58)
    # Visible planter anchors at wall base, mounted against a solid pier.
    x,y,_=position(u,z0)
    g.box('atmosphere wall planter bracket',x-.45,y-.45,z0+.4,.9,.9,.35,'iron')
    pot(x,y,z0+.75,.6,1.2,.55)


def garden_furniture():
    for item in LANDSCAPE_FURNITURE:
        x,y,w,d=item['rect'];z=40
        if 'table' in item['name']:
            spindle(x+w/2,y+d/2,z,[(0,.6),(.2,.6),(.4,.18),(2,.18)],'iron')
            spindle(x+w/2,y+d/2,z+2,[(0,1.5),(.25,1.5)],'timber',12)
            pot(x+w/2,y+d/2,z+2.25,.22,.4,.6)
        else:
            for xx in (x+.15,x+w-.3):
                for yy in (y+.15,y+d-.3):g.box('atmosphere garden furniture leg',xx,yy,z,.15,.15,1.2,'iron')
            g.box('atmosphere garden seat',x,y,z+1.2,w,d,.22,'timber')
            g.box('atmosphere garden seat cushion',x+.08,y+.08,z+1.42,w-.16,d-.16,.2,'trim')
            g.box('atmosphere garden back',x,y,z+1.45,w,.18,1.05,'timber')
        obstacle(item['name'],x,y,z,w,d,item['height'])
    # Dress the existing loungers without expanding their floor footprints.
    for y in (63,72):
        g.box('atmosphere lounger cushion',89.3,y+.2,41.03,3.5,3.6,.18,'trim')
        for yy in (y+.4,y+1.4,y+2.4,y+3.4):g.box('atmosphere lounger cushion piping',89.3,yy,41.22,3.5,.08,.035,'pot_edge')
