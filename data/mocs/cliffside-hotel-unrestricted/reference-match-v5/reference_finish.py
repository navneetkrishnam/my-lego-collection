"""Staircase planting and reference-driven finish, authored in physical stud coordinates."""
import math,random
import numpy as np
import geometry as g
import atmosphere as a
import natural as n

# Each pad is level and supported from the existing stair volume, and occupies only
# an edge strip. Coordinates and elevations are shared with verification and the plan.
STAIR_POTS=[
 ('Upper welcome rose',45.15,59.2,37.6,.88,2.1,'rose',1.15),
 ('Upper flight herb',56.85,66.2,32.0,.83,2.2,'herb',1.1),
 ('Mid flight flowers',45.15,73.2,26.4,.92,2.3,'rose',1.2),
 ('Landing approach',56.85,79.0,22.4,.78,1.8,'rose',1.1),
 ('Landing left citrus',45.15,83.8,20.8,.88,2.2,'citrus',1.25),
 ('Landing right urn',56.85,82.2,20.8,.86,2.15,'herb',1.15),
 ('Lower flight flowers',45.15,90.2,17.6,.92,2.15,'rose',1.2),
 ('Lower flight herb',56.85,96.2,12.8,.8,1.85,'herb',1.1),
 ('Foot approach flowers',45.15,103.2,7.2,.92,2.2,'rose',1.2),
 ('Foot welcome urn',56.85,108.5,3.2,.76,1.9,'rose',1.05)]
PADS=[dict(name=name,rect=(x-1.0,y-1.2,2.,2.4),z=z,plant_rect=(x-R,y-R,2*R,2*R)) for name,x,y,z,r,h,kind,R in STAIR_POTS]
CLEAR_STAIR=(46.5,56,9,56)

def stair_stone():
    # Separate warm limestone tread caps; tiny joints create readable masonry detail.
    for i in range(48):
        y=56+i+(6 if i>=24 else 0);z=40-(i+1)*.8
        for j,x in enumerate(np.arange(44,58,2.8)):
            g.box('reference stair tread cap',float(x+.025),y+.025,z,2.75,.95,.055,'stone')
        # Projecting nosing catches light; the original tread and guard volumes remain.
        g.box('reference stair nosing',44,y+.9,z-.16,14,.11,.16,'trim')
        for x in (42.76,59.2):
            for yy in (y+.05,):
                g.box('reference stair guard facing',x,yy,z+.12,.045,.91,1.86,'stone')
    for p in PADS:
        x,y,w,d=p['rect'];z=p['z']
        # Continuous solid proxy support down to the base, contained inside the stair.
        g.box('reference level stair pot pad',x,y,.25,w,d,z-.25,'stone')
        g.box('reference stair pot pad cap',x-.03,y-.03,z,w+.06,d+.06,.1,'trim')
    for name,x,y,z,r,h,kind,R in STAIR_POTS:
        n.planted_pot(name,x,y,z+.1,r,h,kind,R)


def rose_pocket(label,x,y,z,height,spread,bloom=.65):
    # A compact raised root bed supports a climbing rose; each branch has a woody stem.
    g.box('reference rose bed '+label,x-.9,y-.8,z,1.8,1.6,.6,'pot')
    g.box('reference rose bed soil '+label,x-.8,y-.7,z+.6,1.6,1.4,.04,'soil')
    rr=n.rr_for(label);old=a.rng;a.rng=rr
    try:
        root=np.array([x,y,z+.64]);trunk=np.array([x+.2,y,z+height*.7])
        a.tube(root,trunk,.11,'timber')
        for j in range(12):
            t=(j+1)/12
            tip=np.array([x+rr.uniform(-spread,spread),y+rr.uniform(-.45,.45),z+height*(.32+.68*t)])
            crotch=root+(trunk-root)*min(.85,t)
            a.tube(crotch,tip,.04,'timber',5)
            for k in range(4):
                p=crotch+(tip-crotch)*(k+1)/4
                a.cluster(*p,rr.uniform(.85,1.45),bloom)
        g.objects.append(dict(name='reference rooted rose pocket',label=label,root=root.tolist(),height=height,spread=spread))
    finally:a.rng=old


def planting():
    # Root beds are attached to the outer faces of the existing stair-side ledges.
    # Their foliage remains outside the central nine-stud stair corridor.
    for args in [('upper landing rose',40.3,79.4,20.8,12.5,2.65),
                 ('lower landing rose',62.1,85.8,20.8,9.5,2.6),
                 ('foot climbing rose',40.8,102.8,6.4,11,2.5)]:
        label,x,y,z,h,spread=args
        g.box('reference rose bed support '+label,x-.95,y-.85,.25,1.9,1.7,z-.25,'stone')
        rose_pocket(label,x,y,z,h,spread)
    # Greenery swells around selected existing rock crowns, keeping broad areas bare.
    anchors=[o for o in g.objects if o['name']=='natural rock planting anchor']
    old=a.rng;a.rng=random.Random(25147)
    try:
        for i,o in enumerate(anchors):
            x,y,z=o['origin']
            if i%3 or not(5<x<122 and 58<y<107):continue
            for dx,dy,dz in [(-.5,0,.55),(.4,.3,.9),(0,-.3,1.4)]:a.cluster(x+dx,y+dy,z+dz,1.25,.08)
            # Upright broad-leaved shoots mix with the existing fern-shaped fronds.
            for theta in (0,1.3,3.6):
                tip=(x+math.cos(theta)*.7,y+math.sin(theta)*.7,z+3)
                a.tube((x,y,z),tip,.035,'foliage_dark',4)
                for t in (.3,.6,.9):a.leaf(x+(tip[0]-x)*t,y+(tip[1]-y)*t,z+3*t,1.15)
    finally:a.rng=old


def water():
    # Small blue sea facets lie on the existing water plane, below all rock and stair feet.
    rr=random.Random(71326)
    for x in np.arange(1,127,1.4):
        for y in np.arange(1,113,1.4):
            if not (y>108 or x<2.6 or x>125.5):continue
            w=min(1.32,127-x);d=min(1.32,113-y)
            if min(w,d)<=0:continue
            g.box('reference sea tile',float(x),float(y),.26,float(w),float(d),rr.uniform(.035,.11),rr.choice(['sea1','sea2','sea3','sea4']))
            if rr.random()<.18:
                a.face([(x+.12,y+.12,.39),(x+min(w-.08,.75),y+.17,.39),(x+min(w-.1,.69),y+.25,.39),(x+.1,y+.23,.39)],'sea_glint')


def author():
    g.COLORS.update(glass='655A43',cliff1='90968E',cliff2='B0AC9B',cliff3='C8BBA0',cliff4='979D97',
                    paving1='D5C3A1',paving2='C5B699',paving3='E1CEAB',paving4='CCB998',
                    sea1='398A9B',sea2='4A9DA6',sea3='66ADB4',sea4='337D90',sea_glint='BBD9CE')
    stair_stone();planting();water();window_arches()
    g.objects.append(dict(name='reference finish scope',stair_pots=len(STAIR_POTS),central_clear_studs=9,reference='reference-concept.png'))


def window_arches():
    """Stone spandrels shape selected glazing openings; room/door access stays intact.
    Original rectangular window envelopes bound each arch. None are door openings.
    """
    import exterior as e
    selected=[('main-0','long-arm front',25),('main-0','suite front',64),
              ('main-1','long-arm front',33),('main-2','long-arm front',33)]
    for floor_id,wall_name,u in selected:
        f=next(f for f in n.l.FLOORS if f['id']==floor_id)
        w=next(w for w in f['walls'] if w['name']==wall_name)
        o=next(o for o in w['opens'] if o['a']==u)
        assert o['kind']=='window'
        z=f['z']+o['sill'];r=o['w']/2;top=z+o['height'];spring=top-r;center=u+r
        # Fill only the upper corner regions outside the semicircular glazing profile.
        for k in range(24):
            t=math.pi-k*math.pi/24;tt=math.pi-(k+1)*math.pi/24
            aa=center+r*math.cos(t);bb=center+r*math.cos(tt)
            za=spring+r*math.sin(t);zb=spring+r*math.sin(tt)
            # Triangles use a tiny cap allowance to remain nondegenerate at the crown.
            ps=[(aa,za),(bb,zb),(bb,top+.025),(aa,top+.025)]
            for offset,reverse in [(.08,True),(.28,False)]:
                pts=[e.xyz(w,x,zz,offset) for x,zz in ps]
                g.face(pts[::-1] if reverse else pts,'wall')
            g.face([e.xyz(w,aa,za,.08),e.xyz(w,aa,za,.28),e.xyz(w,bb,zb,.28),e.xyz(w,bb,zb,.08)],'stone')
        # Deep voussoirs make the arch visible from the hero view, with real shadows.
        for k in range(16):
            t=k*math.pi/16+.007;tt=(k+1)*math.pi/16-.007
            ps=[(center+rr*math.cos(a),spring+rr*math.sin(a)) for rr,a in [(r,t),(r,tt),(r+.43,tt),(r+.43,t)]]
            front=[e.xyz(w,x,zz,.55) for x,zz in ps];back=[e.xyz(w,x,zz,.28) for x,zz in ps]
            g.face(front,'stone');g.face(back[::-1],'stone')
            for j in range(4):g.face([front[j],back[j],back[(j+1)%4],front[(j+1)%4]],'stone')
        g.objects.append(dict(name='reference arched window',floor=floor_id,wall=wall_name,opening=u,width=o['w'],spring=spring,top=top))
