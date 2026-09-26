"""Garden/pool focal details and lighting fixtures over the approved hotel study."""
import math,random
import numpy as np
import geometry as g
import atmosphere as a
import layout as l

# Ground-level additions share this schedule with the plan and navigation checker.
SITE_ITEMS=[dict(name='Garden fountain',rect=(7.6,38.1,4.8,4.8),height=5.7),
            dict(name='Pool towel stand',rect=(94.5,67.6,1,3.4),height=2.8),
            dict(name='Pool topiary pot',rect=(93.9,60.4,1.4,1.4),height=5.5)]
OLIVES=[(15.5,17.5,42.45,14,2.3),(93,38,42.45,13,2.0)]
# Warmer, lower-contrast stone reduces the previous checkerboard effect.
g.COLORS.update(paving1='D6C6A7',paving2='D0BFA0',paving3='DCCDAF',paving4='CDBD9F',
    olive='526849',olive_light='7E906F',lavender='8B719C',lavender_tip='B2A2C1',
    silver_leaf='8B9880',pool_gloss='499EAA',water_glint='B2D6CD',
    canvas='EFE2C6',canvas_stripe='BE8463',towel='EDE6D6',brass='B6A171')

def box(name,x,y,z,w,d,h,col='stone'):g.box('garden pool '+name,x,y,z,w,d,h,col)

def ring(x,y,z,r1,r2,h,color='stone',n=32):
    for i in range(n):
        t,u=i*math.tau/n,(i+1)*math.tau/n
        coord=lambda r,zz,aa:(x+r*math.cos(aa),y+r*math.sin(aa),zz)
        for radii,zs,angles in [([r1,r2,r2,r1],[z+h]*4,[t,t,u,u]),([r2,r2,r2,r2],[z,z,z+h,z+h],[t,u,u,t]),([r1,r1,r1,r1],[z+h,z+h,z,z],[t,u,u,t])]:
            a.face([coord(r,zz,aa) for r,zz,aa in zip(radii,zs,angles)],color)

def disk(x,y,z,r,color,n=32):a.face([(x+r*math.cos(t),y+r*math.sin(t),z) for t in np.arange(n)*math.tau/n],color)

def olive(x,y,z,height,spread):
    # Branch tips support each foliage mass. The roots occupy existing planted pots.
    a.tube((x,y,z),(x-.2,y,z+height*.6),.18,'timber')
    for k in range(7):
        angle=k*math.tau/7+.4;rr=spread*(.45+.35*(k%3)/2)
        tip=(x+rr*math.cos(angle),y+rr*math.sin(angle),z+height*(.65+.22*(k%3)/2))
        a.tube((x-.2,y,z+height*.4),tip,.085,'timber')
        a.spindle(tip[0],tip[1],tip[2]-.5,[(0,.12),(.3,.7),(.8,1.05),(1.3,.7),(1.6,.1)],'olive',10)
        for i in range(90):
            theta=a.rng.random()*math.tau;radius=a.rng.random()*.9
            xx=tip[0]+radius*math.cos(theta);yy=tip[1]+radius*math.sin(theta);zz=tip[2]+a.rng.uniform(-.6,.9)
            ang=a.rng.random()*math.tau;dx,dy=.4*math.cos(ang),.4*math.sin(ang)
            a.face([(xx-dx,yy-dy,zz),(xx-dy*.24,yy+dx*.24,zz+.08),(xx+dx,yy+dy,zz+.15),(xx+dy*.24,yy-dx*.24,zz+.08)],'olive_light' if i%3==0 else 'olive')
    g.objects.append(dict(name='garden pool olive tree',root=[x,y,z],height=height,spread=spread))

def lavender(x,y,z):
    for k in range(10):
        angle=k*math.tau/10;rr=.2+.25*a.rng.random();h=1.4+.9*a.rng.random()
        xx,yy=x+rr*math.cos(angle),y+rr*math.sin(angle)
        a.tube((x,y,z),(xx,yy,z+h),.028,'silver_leaf',4)
        for j in range(4):a.spindle(xx,yy,z+h-.45+j*.14,[(0,.075),(.13,.11)],'lavender_tip' if j==3 else 'lavender',5)
    g.objects.append(dict(name='garden pool lavender clump',origin=[x,y,z]))

def fountain():
    x,y,z=10,40.5,40
    a.spindle(x,y,z,[(0,2.4),(.2,2.4),(.35,2.2)],'stone',32)
    ring(x,y,z+.35,1.86,2.2,.55);disk(x,y,z+.58,1.86,'pool_gloss')
    a.spindle(x,y,z+.35,[(0,.55),(.3,.55),(.5,.3),(2.6,.3),(2.8,.7)],'stone',12)
    a.spindle(x,y,z+2.7,[(0,.45),(.35,1.0),(.5,1.12)],'stone',24)
    ring(x,y,z+3.2,.98,1.13,.15);disk(x,y,z+3.27,.98,'pool_gloss')
    a.spindle(x,y,z+3.2,[(0,.3),(1.2,.22),(1.4,.52)],'stone',12)
    ring(x,y,z+4.6,.46,.58,.16);disk(x,y,z+4.68,.46,'pool_gloss')
    a.spindle(x,y,z+4.7,[(0,.15),(.5,.1)],'brass')
    for angle in np.arange(4)*math.tau/4:
        for start,end in [(1.02,1.45),(.5,.8)]:
            high=z+(3.27 if start>1 else 4.68);low=z+(.63 if start>1 else 3.27)
            pts=[(x+(start+(end-start)*t)*math.cos(angle),y+(start+(end-start)*t)*math.sin(angle),high-(high-low)*t*t) for t in np.linspace(0,1,10)]
            for aa,bb in zip(pts,pts[1:]):a.tube(aa,bb,.035,'water_glint',5)
    g.objects.append(dict(name='garden pool tiered fountain',origin=[7.6,38.1,40],size=[4.8,4.8,5.7]))

def pool():
    px,py,pw,pd=l.PROGRAM['pool']
    # Ripple mesh stays within the existing pool void, above the old placeholder surface.
    height=lambda x,y:38.995+.018*math.sin(x*2.1+y*.9)+.012*math.cos(y*2.8-x*.6)
    for x in np.arange(px,px+pw,.5):
        for y in np.arange(py,py+pd,.5):
            a.face([(xx,yy,height(xx,yy)) for xx,yy in [(x,y),(x+.5,y),(x+.5,y+.5),(x,y+.5)]],'pool_gloss')
    # Separate coping slabs and a fine turquoise waterline inside the basin.
    for x in np.arange(px-.5,px+pw+.5,2):
        for y in (py-.5,py+pd):box('coping slab',float(x+.04),y,40.3,min(1.92,px+pw+.5-x-.04),.5,.12)
    for y in np.arange(py,py+pd,2):
        for x in (px-.5,px+pw):box('coping slab',x,float(y+.04),40.3,.5,1.92,.12)
    for x,y,w,d in [(px,py,pw,.06),(px,py+pd-.06,pw,.06),(px,py,.06,pd),(px+pw-.06,py,.06,pd)]:box('waterline tile',x,y,39.12,w,d,.5,'pool_gloss')
    # Ladder feet occupy the coping, not the preserved deck walking strip.
    for x in (78.2,80.2):
        pts=[(x,61.75,40.42),(x,61.75,42.1),(x,62.1,42.35),(x,62.8,42.1),(x,62.95,37.9)]
        for aa,bb in zip(pts,pts[1:]):a.tube(aa,bb,.075,'brass')
    for z in (38.4,39.05,39.7):a.tube((78.2,62.95,z),(80.2,62.95,z),.07,'brass')
    g.objects.append(dict(name='garden pool ripple surface',rect=[px,py,pw,pd],z_range=[38.965,39.025]))


def shade():
    # A wall-mounted retractable awning shades the service-side seating band.
    # Every canopy point stays x89..95.8 and above the 7-stud clearance level.
    x0,x1,y0,y1=89,95.8,62.7,76.3
    for y in (63.2,75.8):
        a.tube((95.8,y,47),(92.8,y,47.6),.085,'iron')
        a.tube((92.8,y,47.6),(89,y,47.1),.085,'iron')
        box('awning wall bracket',95.7,y-.3,46.7,.25,.6,1.2,'iron')
    for i,y in enumerate(np.arange(y0,y1,.8)):
        yy=min(float(y+.8),y1);color='canvas' if i%4 else 'canvas_stripe'
        a.face([(x0,y,47.25),(x1,y,48.5),(x1,yy,48.5),(x0,yy,47.25)],color)
        a.face([(x0,y,47.25),(x0,y,46.85),(x0,yy,46.85),(x0,yy,47.25)],color)
    a.tube((x0,y0,47.1),(x0,y1,47.1),.07,'iron')
    g.objects.append(dict(name='garden pool service-side awning',origin=[89,62.7,46.7],size=[6.95,13.6,1.8],mount='service west wall'))


def towels():
    x,y,z=94.5,67.6,40
    for xx in (x,x+.86):
        for yy in (y,y+3.26):box('towel stand post',xx,yy,z,.14,.14,2.8,'timber')
    for zz in (.35,1.5,2.6):box('towel shelf',x,y,z+zz,1,3.4,.12,'timber')
    for yy in (y+.6,y+1.6,y+2.6):
        for zz in (.8,1.95):a.tube((x+.22,yy,z+zz),(x+.8,yy,z+zz),.3,'towel',10)
    # Drinks and folded towel use the existing side table surface.
    for yy in (68.95,69.6):a.spindle(91.5,yy,41.31,[(0,.16),(.45,.2)],'towel',8)
    box('folded pool towel',92,68.9,41.31,.7,1,.15,'towel')


def author():
    saved=a.rng;a.rng=random.Random(63019)
    try:
        fountain();pool();shade();towels()
        for args in OLIVES:olive(*args)
        for x in np.arange(9.2,16.5,1.15):lavender(float(x),48.8,41)
        for x in np.arange(85.5,91.8,1.05):lavender(float(x),45.4,41)
        for y in (16,18.8):
            for x in (8.8,10.4):lavender(x,y,41)
        # Topiary root stays in its explicitly scheduled pot footprint.
        a.pot(94.6,61.1,40,.7,1.5,.15)
        a.tube((94.6,61.1,41.4),(94.6,61.1,44),.08,'timber')
        for dz in (0,.5,1):a.cluster(94.6,61.1,43.7+dz,.65,.08)
        # Layer cushions onto the existing cottage bench, without enlarging it.
        for x in (85.5,87.5,89.5):box('cottage bench cushion',x,41.15,41.63,1.65,1.15,.22,'canvas')
        for x in (85.5,90.1):box('cottage bench pillow',x,41.08,41.9,1.2,.35,.85,'canvas_stripe')
        # Lanterns attach to pergola corner posts and the existing garden guard.
        for x,y in [(5.5,35.5),(16.5,35.5),(84.5,45.5),(93.5,45.5)]:
            a.tube((x,y,49.3),(x,y+1.1,49.3),.07,'iron');a.lantern(x,y+1.1,47.2)
        for x,y in [(2.25,38),(18,51.75)]:a.lantern(x,y,44.6)
        for y in (64.4,74.8):
            a.tube((96,y,46.6),(95.3,y,46.6),.07,'iron');a.lantern(95.3,y,44.5)
        for item in SITE_ITEMS:
            x,y,w,d=item['rect'];g.objects.append(dict(name='garden pool obstacle '+item['name'],origin=[x,y,40],size=[w,d,item['height']],collision_rect=[x,y,w,d],level=40))
        g.objects.append(dict(name='garden pool scope',seed=63019,lighting='emitting lantern material in renderer',trees='two olive trees in existing pots'))
    finally:a.rng=saved
