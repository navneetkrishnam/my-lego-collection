"""Main-villa appearance study over the approved v5 room geometry; stud units."""
import math
import numpy as np
import geometry as g
import layout as l

g.COLORS.update(stone='EBDDC1',joint='C5B89E',shutter='38594A',shutter_light='4F6B55',
                iron='343D37',wood='88603C',glass='4C6561',lamp='E7B96C',
                tile1='B86743',tile2='C6794D',tile3='A85C3C',tile4='BC704C',leaf='577348',flower='D68E9C')
FACES={'main west':-1,'main rear':-1,'main east':1,'suite front':1,'L inner return':1,'long-arm front':1}

def localbox(w,name,u,z,width,height,offset=0,depth=.25,color='stone'):
    # u follows the wall; positive offset is outward from its external face.
    sign=FACES[w['name']];at=w['c']+sign*(w['thickness']/2+offset)
    low=min(at,at+sign*depth)
    if w['axis']=='x':g.box('villa '+name,u,low,z,width,depth,height,color)
    else:g.box('villa '+name,low,u,z,depth,width,height,color)

def xyz(w,u,z,v):
    at=w['c']+FACES[w['name']]*(w['thickness']/2+v)
    return (u,z,at) if w['axis']=='x' else (at,z,u)

def arc(w,name,center,spring,r,thick,offset=.08,depth=.4):
    for i in range(12):
        a=i*math.pi/12+.008;b=(i+1)*math.pi/12-.008
        p=[(center+rr*math.cos(t),spring+rr*math.sin(t)) for rr,t in [(r,a),(r,b),(r+thick,b),(r+thick,a)]]
        front=[xyz(w,u,z,offset+depth) for u,z in p];back=[xyz(w,u,z,offset) for u,z in p]
        g.face(front,'stone');g.face(list(reversed(back)),'stone')
        for j in range(4):g.face([front[j],back[j],back[(j+1)%4],front[(j+1)%4]],'stone')
    g.objects.append(dict(name='villa '+name,wall=w['name'],radius=r,center=center,spring=spring))

def windows():
    for f in l.FLOORS:
        if not f['id'].startswith('main'):continue
        for w in f['walls']:
            if w['name'] not in FACES:continue
            for o in w['opens']:
                u=o['a'];width=o['w'];z=f['z']+o['sill'];h=o['height'];door=o['kind']=='door'
                localbox(w,'opening jamb',u-.5,z-.1,.5,h+.2)
                localbox(w,'opening jamb',u+width,z-.1,.5,h+.2)
                localbox(w,'opening head',u-.65,z+h,width+1.3,.6,depth=.5)
                if not door:
                    localbox(w,'window sill',u-.65,z-.5,width+1.3,.45,depth=.7)
                    localbox(w,'recessed glazing',u+.12,z+.12,width-.24,h-.24,offset=-.68,depth=.05,color='glass')
                    for uu in (u+.12,u+width-.3,u+width/2-.09):
                        localbox(w,'window frame',uu,z+.12,.18,h-.24,offset=-.55,depth=.18,color='wood')
                    for zz in (z+.12,z+h-.3,z+h*.58):
                        localbox(w,'window transom',u+.12,zz,width-.24,.18,offset=-.55,depth=.18,color='wood')
                    # Shutters only where clear wall space exists; narrow corridor bays keep stone surrounds.
                    others=[p for p in w['opens'] if p is not o]
                    shutter_width=min(1.5,width*.3)
                    for a in (u-.65-shutter_width,u+width+.65):
                        if a<w['a']+1 or a+shutter_width>w['b']-1:continue
                        if any(a<p['a']+p['w']+.55 and a+shutter_width>p['a']-.55 for p in others):continue
                        localbox(w,'shutter panel',a,z,shutter_width,h,offset=.12,depth=.2,color='shutter')
                        for zz in np.arange(z+.4,z+h-.2,.55):
                            localbox(w,'shutter louvre',a+.1,float(zz),shutter_width-.2,.15,offset=.32,depth=.09,color='shutter_light')
                else:
                    # Operable double doors are shown closed for the appearance study.
                    # Their clear structural opening and planning access are unchanged.
                    for a in (u+.08,u+width/2+.04):
                        leaf=width/2-.12
                        localbox(w,'operable door leaf',a,z+.08,leaf,h-.16,offset=-.68,depth=.1,color='wood')
                        localbox(w,'door glazed panel',a+.18,z+3.2,leaf-.36,h-3.5,offset=-.55,depth=.05,color='glass')
                        localbox(w,'door lower panel',a+.18,z+.45,leaf-.36,2.3,offset=-.55,depth=.05,color='tile3')
                        localbox(w,'door handle',a+leaf-.2,z+3,.12,.65,offset=-.45,depth=.14,color='iron')
                    # Relieving arch is above the lintel, not across the clear opening.
                    arc(w,'door relieving arch',u+width/2,z+h,width/2,.55)
                    if f['z']==40:
                        for a in (u-1.65,u+width+1.05):
                            localbox(w,'entrance lantern back',a,z+5.7,.6,1.7,offset=.05,depth=.35,color='iron')
                            localbox(w,'entrance lantern light',a+.08,z+5.9,.44,1.1,offset=.4,depth=.3,color='lamp')
                            localbox(w,'entrance lantern cap',a-.1,z+7,.8,.22,offset=.35,depth=.5,color='iron')


def masonry():
    for f in l.FLOORS:
        if not f['id'].startswith('main'):continue
        for w in f['walls']:
            if w['name'] not in FACES:continue
            for row,z in enumerate(np.arange(f['z']+1,f['z']+13,2)):
                intervals=[(w['a']+.12,w['b']-.12)]
                for o in w['opens']:
                    if f['z']+o['sill']-.7<z<f['z']+o['sill']+o['height']+.8:
                        cut=(o['a']-.8,o['a']+o['w']+.8);new=[]
                        for a,b in intervals:
                            if cut[1]<=a or cut[0]>=b:new.append((a,b));continue
                            if a<cut[0]:new.append((a,cut[0]))
                            if b>cut[1]:new.append((cut[1],b))
                        intervals=new
                for a,b in intervals:
                    if b-a>.1:localbox(w,'stone course',a,float(z),b-a,.035,offset=.004,depth=.018,color='joint')
                for u in np.arange(w['a']+1+(row%2)*2,w['b']-1,4):
                    if any(o['a']-.8<u<o['a']+o['w']+.8 and f['z']+o['sill']-.7<z+1<f['z']+o['sill']+o['height']+1 for o in w['opens']):continue
                    localbox(w,'stone vertical joint',float(u),float(z),.028,1.95,offset=.004,depth=.018,color='joint')
    # Quoin stones on exposed convex corners, never the L's re-entrant corner.
    for x,y in [(20,10),(78,10),(78,32),(44,52),(20,52)]:
        for row,z in enumerate(np.arange(40.4,81,2)):
            # Quoins sit on both adjacent outward-facing wall strips.
            for f in l.FLOORS:
                if f['z']<=z<f['z']+14 and f['id'].startswith('main'):
                    for w in f['walls']:
                        if w['name'] not in FACES:continue
                        u=x if w['axis']=='x' else y;cross=y if w['axis']=='x' else x
                        outer=w['c']+FACES[w['name']]*.5
                        if abs(outer-cross)>.01 or u not in (w['a'],w['b']):continue
                        length=1.3 if row%2 else 1.9
                        localbox(w,'corner quoin',u if u==w['a'] else u-length,float(z),length,1.7,depth=.12)
    for w in [w for f in l.FLOORS if f['id']=='main-2' for w in f['walls'] if w['name'] in FACES]:
        localbox(w,'upper cornice',w['a']-.15,81.5,w['b']-w['a']+.3,.5,depth=.65)
        for u in np.arange(w['a']+.5,w['b']-.5,1.6):
            localbox(w,'cornice dentil',float(u),80.7,.75,.7,depth=.45)

def balcony(name,x,y,z,w,d):
    # Replace main-only rail placeholders; all work stays within the approved deck.
    for xx,yy,ww,dd in [(x,y+d-.35,w,.22),(x,y,.22,d),(x+w-.35,y,.22,d)]:
        g.box('villa balcony top rail',xx,yy,z+2.65,ww,dd,.22,'iron')
        g.box('villa balcony bottom rail',xx,yy,z+.4,ww,dd,.16,'iron')
    for xx in np.arange(x+.2,x+w-.1,.85):g.box('villa balcony spindle',float(xx),y+d-.35,z+.45,.13,.16,2.2,'iron')
    for xx in (x,x+w-.35):
        for yy in np.arange(y+.2,y+d-.1,.85):g.box('villa balcony spindle',xx,float(yy),z+.45,.16,.13,2.2,'iron')
    g.box('villa balcony fascia',x,y+d-.15,z-.55,w,.3,.55,'stone')
    # Compact planter at the outer corner; leaves remain within the deck footprint.
    g.box('villa balcony planter',x+.7,y+d-1,z+.4,2.1,.6,.6,'wood')
    for i in range(5):
        xx=x+.8+i*.37
        g.box('villa balcony foliage',xx,y+d-.92,z+1,.3,.42,.55 if i%2 else .75,'leaf')
        g.box('villa balcony flowers',xx+.02,y+d-.87,z+1.55,.22,.25,.2,'flower')

RECTS=[(18.5,8.5,79.5,33.5),(18.5,8.5,45.5,53.5)]
def inside(x,y):return any(a<=x<=c and b<=y<=d for a,b,c,d in RECTS)
def roofheight(x,y):
    return 82.75+max(.52*min(x-a,c-x,y-b,d-y) for a,b,c,d in RECTS if a-1e-6<=x<=c+1e-6 and b-1e-6<=y<=d+1e-6)

def roof_tiles():
    # Individual low barrel profiles on a regular grid conform to the existing hip envelope.
    # Roof bounds and slopes are unchanged; each tile follows the local fall direction.
    count=0
    for ix,x in enumerate(np.arange(18.5,79.5,1)):
        for iy,y in enumerate(np.arange(8.5,53.5,1.8)):
            end=min(y+1.8,53.5 if x<45.5 else 33.5)
            if end-y<.12:continue
            xa,xb,ya,yb=x+.04,x+.96,y+.04,end-.04
            if not all(inside(xx,yy) for xx in (xa,xb) for yy in (ya,yb)):continue
            cx,cy=(xa+xb)/2,(ya+yb)/2
            dx=roofheight(cx+.01,cy)-roofheight(cx-.01,cy)
            dy=roofheight(cx,cy+.01)-roofheight(cx,cy-.01)
            color='tile'+str(1+(ix*7+iy*3)%4)
            # The barrel axis follows the local roof fall, including the side hips.
            for j in range(5):
                u=j/5;v=(j+1)/5
                zu=.12+.24*math.sin(math.pi*u);zv=.12+.24*math.sin(math.pi*v)
                if abs(dx)>abs(dy):
                    a=ya+(yb-ya)*u;b=ya+(yb-ya)*v
                    pts=[(xa,roofheight(xa,a)+zu,a),(xb,roofheight(xb,a)+zu,a),
                         (xb,roofheight(xb,b)+zv,b),(xa,roofheight(xa,b)+zv,b)]
                else:
                    a=xa+(xb-xa)*u;b=xa+(xb-xa)*v
                    pts=[(a,roofheight(a,ya)+zu,ya),(b,roofheight(b,ya)+zv,ya),
                         (b,roofheight(b,yb)+zv,yb),(a,roofheight(a,yb)+zu,yb)]
                g.face(pts,color)
            count+=1
    g.objects.append(dict(name='villa roof tile field',tile_count=count))
    # Low ridge covers visually join the two tile fields of the L roof.
    for axis,c,a,b in [('x',21,32,67),('y',32,21,40)]:
        for u in np.arange(a,b,1):
            for j in range(6):
                t=j*math.pi/6;tt=(j+1)*math.pi/6
                cross=[c+.32*math.cos(t),c+.32*math.cos(tt)]
                up=[.4+.28*math.sin(t),.4+.28*math.sin(tt)]
                pts=[]
                for along,k in [(u,0),(min(u+.96,b),0),(min(u+.96,b),1),(u,1)]:
                    xx,yy=(along,cross[k]) if axis=='x' else (cross[k],along)
                    pts.append((xx,roofheight(xx,yy)+up[k],yy))
                g.face(pts,'tile3')
    g.objects.append(dict(name='villa roof ridge covers',segments=54))
    # Two architectural chimney envelopes, located over the building rather than the eaves.
    for x,y in [(27,17),(67,18)]:
        z=roofheight(x+1.5,y+1.5)-.3
        g.box('villa chimney shaft',x,y,z,3,3,6,'stone')
        g.box('villa chimney collar',x-.25,y-.25,z+4.2,3.5,3.5,.4,'trim')
        g.box('villa chimney cap',x-.35,y-.35,z+6,3.7,3.7,.6,'tile3')
        g.box('villa chimney flue',x+1,y+1,z+6.6,1,1,.2,'iron')

def author():
    windows();masonry();roof_tiles()
