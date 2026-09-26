"""Reference-led landscape: repeatable irregular rock, rooted growth and distributed pots.
All dimensions are proxy stud units; these meshes are not LEGO part instances.
"""
import hashlib,math,random
import numpy as np
import geometry as g
import layout as l
import atmosphere as a

SEED=94126
# Conservative foliage footprints, not just the narrower terracotta bases.
POTS=[
 ('Garden entrance citrus',17.8,22,40,.82,2.0,'citrus',1.35),
 ('Garden fountain companion',4.3,38.9,40,.65,1.4,'rose',1.1),
 ('Villa front corner',21.7,54.1,40,.65,1.5,'herb',1.0),
 ('Lobby entrance large',46.6,48.6,40,1.05,2.3,'citrus',1.6),
 ('Lobby entrance low',49.1,49.5,40,.46,1.0,'rose',.7),
 ('Suite court urn',59.2,38.8,40,1.0,2.4,'rose',1.45),
 ('Library terrace olive',75.2,35.0,40,.8,2.0,'herb',1.3),
 ('Court flower group tall',70.2,49.6,40,.95,2.1,'rose',1.4),
 ('Court flower group low',72.6,50.1,40,.45,.9,'herb',.68),
 ('Cottage garden approach',83.0,38.2,40,.48,1.2,'rose',.75),
 ('Cottage foyer urn',111.0,38.0,40,.62,1.8,'herb',.9),
 ('Cottage east corner',123.4,38.0,40,.74,1.9,'rose',1.05),
 ('Promenade citrus',94.2,48.5,40,.75,1.9,'citrus',1.2),
 ('Pool seating south urn',93.8,77.1,40,.58,1.5,'rose',.9),
 # Balcony pots tuck into rail corners, outside their door thresholds.
 ('Corner balcony herb',23.4,54.5,54,.45,1.0,'herb',.65),
 ('Upper suite balcony rose',61.5,34.4,68,.48,1.1,'rose',.68),
 ('Salon terrace citrus',99.5,80.2,26,.55,1.3,'herb',.8),
 ('Salon terrace flower urn',122.3,80.2,26,.55,1.3,'rose',.8),
]
POT_ITEMS=[dict(name=name,rect=(x-R,y-R,2*R,2*R),height=h+(4.3 if kind=='citrus' else 2.8),level=z) for name,x,y,z,r,h,kind,R in POTS]
# Unevenly spaced roots and different lengths, with deliberate exposed wall.
CASCADE_ROOTS=[(63.1,43.3,18.8),(73.9,43.3,26.7),(91.4,43.3,15.6)]

def rr_for(label):return random.Random(SEED+int(hashlib.sha256(label.encode()).hexdigest()[:8],16))

def cliff(name,x,y,z,w,d,h,color):
    """Three unequal interlocking fractured masses, entirely inside a reserved rock envelope.
    Rings vary in height, offset and outline; there is no row/column rock grid.
    Horizontal shelves support the recorded planting anchors.
    """
    rr=rr_for(name)
    def mass(label,cx,cy,ww,dd,hh,base_z,plant=False):
        n=8;phase=rr.uniform(-.12,.12)
        ang=[math.tau*i/n+phase+rr.uniform(-.11,.11) for i in range(n)]
        # Broad toe, fissured shoulder, narrow uneven crown, all closed back to base.
        scales=[1,.89,.98,.85,.8]
        heights=[0,hh*.19,hh*.48,hh*.82,hh]
        rings=[]
        for j,(scale,zz) in enumerate(zip(scales,heights)):
            ox=rr.uniform(-.045,.045)*ww if j else 0
            oy=rr.uniform(-.05,.05)*dd if j else 0
            ring=[]
            for i,t in enumerate(ang):
                rad=scale*rr.uniform(.84,1)
                xx=cx+ox+math.cos(t)*ww*.47*rad
                yy=cy+oy+math.sin(t)*dd*.47*rad
                dz=rr.uniform(-.06,.06)*hh if 0<j<4 else 0
                ring.append((max(x+.025,min(x+w-.025,xx)),max(y+.025,min(y+d-.025,yy)),base_z+zz+dz))
            rings.append(ring)
        stone=rr.choice(['cliff1','cliff2','cliff3','cliff4'])
        for j,(lo,hi) in enumerate(zip(rings,rings[1:])):
            for i in range(n):
                col=stone if rr.random()<.76 else rr.choice(['cliff1','cliff2','cliff3','cliff4'])
                # Each quad is two angular fracture planes, without repeated square seams.
                a.face([lo[i],lo[(i+1)%n],hi[(i+1)%n],hi[i]],col)
        a.face(rings[-1],stone);a.face(rings[0][::-1],stone)
        g.objects.append(dict(name='natural fractured rock',envelope=name,label=label,origin=[cx-ww/2,cy-dd/2,base_z],size=[ww,dd,hh]))
        if plant:
            px=sum(p[0] for p in rings[-1])/n;py=sum(p[1] for p in rings[-1])/n
            # Anchor sits on the real planar crown, with the rim as spill support.
            rim=max(rings[-1],key=lambda p:p[1])
            g.objects.append(dict(name='natural rock planting anchor',origin=[px,py,base_z+hh],rim=list(rim),envelope=name))
    mass('broad fractured base',x+w*.48,y+d*.47,w*.99,d*.98,h*.48,z,rr.random()<.3)
    mass('offset middle ledge',x+w*.53,y+d*.42,w*.9,d*.85,h*.43,z+h*.32,rr.random()<.65)
    mass('broken crown',x+w*rr.uniform(.39,.57),y+d*.36,w*.74,d*.67,h*.36,z+h*.64,rr.random()<.4)
    mass('offset shoulder',x+w*.65,y+d*.7,w*.68,d*.57,h*rr.uniform(.25,.48),z,rr.random()<.6)
    # A few talus fragments, strongly varied in size, lie at the foot of the mass.
    for k in range(rr.randint(2,4)):
        ww=w*rr.uniform(.16,.28);dd=d*rr.uniform(.12,.21)
        cx=x+rr.uniform(.18,.8)*w;cy=y+rr.uniform(.65,.87)*d
        mass('talus '+str(k),cx,cy,ww,dd,min(h*.18,rr.uniform(1,3.2)),z)
    g.objects.append(dict(name=name,origin=[x,y,z],size=[w,d,h],color=color))


def vine(name,points,r=.9,bloom=.45,allow=None,branches=True):
    """Root-connected woody paths with tapered, patchy leaves and asymmetric offshoots."""
    rr=rr_for(name+repr(points));old=a.rng;a.rng=rr
    try:
        pts=[np.array(p,float) for p in points]
        lengths=[np.linalg.norm(q-p) for p,q in zip(pts,pts[1:])];total=sum(lengths)
        if total<.01:return
        done=0;centers=[]
        for seg,(p,q,dist) in enumerate(zip(pts,pts[1:],lengths)):
            if dist<.01:continue
            a.tube(p,q,.045+.025*(1-done/total),'timber',5)
            count=max(2,math.ceil(dist/.65))
            for k in range(count):
                t=(k+.2)/count;progress=(done+dist*t)/total
                center=p+(q-p)*t
                # Cluster widths swell in localized pockets and taper at growing tips.
                radius=r*(.42+.5*max(0,math.sin(progress*9.7+1.3)))*(1-.35*progress)
                if rr.random()<.18:continue
                center+=np.array([rr.uniform(-.18,.18),rr.uniform(-.12,.12),rr.uniform(-.15,.15)])
                if allow and not allow(center,radius+.7):continue
                flowers=bloom*(.22+.95*max(0,math.sin(progress*13+seg)))
                a.cluster(*center,radius,flowers)
                centers.append(center.tolist())
                if branches and k%4==1 and rr.random()<.48:
                    offset=np.array([rr.choice([-1,1])*rr.uniform(.7,2.2)*r,rr.uniform(-.3,.3),rr.uniform(-1.8,.5)])
                    end=center+offset
                    if allow and not allow(end,.9):continue
                    middle=center+offset*.55+np.array([0,0,.2])
                    a.tube(center,middle,.035,'timber',4);a.tube(middle,end,.02,'timber',4)
                    a.cluster(*middle,r*.5,flowers*.65);a.cluster(*end,r*.32,flowers*.45)
            done+=dist
        g.objects.append(dict(name='natural rooted creeper',label=name,root=list(points[0]),path=[list(p) for p in points],end=list(points[-1]),foliage_centers=centers,flower_density=bloom))
    finally:a.rng=old


def facade_vine(wallname,u,z0,z1,name,r):
    import exterior,annex_exterior
    walls=[(f,w) for f in l.FLOORS for w in f['walls'] if w['name']==wallname or (wallname=='service front' and w['name']=='open arcade front')]
    w=walls[0][1];sign={**exterior.FACES,**annex_exterior.FACES}[w['name']]
    c=w['c']+sign*(w['thickness']/2+.5)
    pos=lambda uu,zz:np.array((uu,c,zz) if w['axis']=='x' else (c,uu,zz))
    holes=[(o['a']-.45,f['z']+o['sill']-.45,o['a']+o['w']+.45,f['z']+o['sill']+o['height']+.45) for f,ww in walls for o in ww['opens']]
    def allow(p,pad):
        uu=p[0] if w['axis']=='x' else p[1];zz=p[2]
        return w['a']-.15<=uu<=w['b']+.15 and not any(aa-pad<uu<bb+pad and za-pad<zz<zb+pad for aa,za,bb,zb in holes)
    rr=rr_for(name);points=[pos(u,z0+1.95)];last=u
    # A continuous stem follows solid wall piers; branch foliage is independently screened.
    for zz in np.arange(z0+3,z1,1.3):
        preferred=u+math.sin((zz-z0)*.18+rr.random()*.4)*r*.8
        candidates=sorted(np.arange(u-2.2,u+2.21,.2),key=lambda v:abs(v-preferred)+.45*abs(v-last))
        options=[v for v in candidates if allow(pos(v,zz),.12)]
        if not options:break
        nxt=options[0]
        # Verify the segment as well as its end, so no stem bridges a window.
        if not all(allow(pos(last+(nxt-last)*t,points[-1][2]+(zz-points[-1][2])*t),.09) for t in np.linspace(0,1,9)):break
        points.append(pos(nxt,float(zz)));last=nxt
    if len(points)>1:vine(name,[p.tolist() for p in points],r,.48,allow)
    # Long lateral growth follows the solid spandrel below a selected floor, never a cut-off floating strip.
    for zz,length,direction in [(z0+11.1,rr.uniform(3,6),-1),(z0+25.0,rr.uniform(2.5,5.5),1)]:
        if zz>=points[-1][2]:continue
        root=min(points,key=lambda p:abs(p[2]-zz));branch=[root.tolist()]
        for t in np.linspace(.1,1,12):
            p=root+pos(direction*length*t,rr.uniform(-.12,.12))-pos(0,0)
            if not allow(p,.65):break
            branch.append(p.tolist())
        if len(branch)>2:vine(name+' lateral',branch,.6,.35,allow,False)
    x,y,_=pos(u,z0)
    g.box('atmosphere wall planter bracket',x-.45,y-.45,z0+.4,.9,.9,.35,'iron')
    a.pot(x,y,z0+.75,.6,1.2,.55)


def cascades():
    # Main pool retaining wall: three different established plants, not five vertical repeats.
    for i,(x,z,end) in enumerate(CASCADE_ROOTS):
        g.box('natural parapet root trough',x-.7,88.05,42.25,1.4,1.4,.65,'pot')
        bend=[-1.3,3.5,-2.8][i]
        pts=[(x,89.1,z),(x+.4,89.25,40.8),(x+bend*.5,89.35,36.2),(x+bend,89.3,31.8),(x+bend-.7,89.4,end+3),(x+bend+.3,89.35,end)]
        vine('pool wall cascade '+str(i),pts,2.15 if i!=1 else 1.65,.27 if i!=1 else .08)
        root=pts[2]
        vine('pool wall spreading branch '+str(i),[root,(root[0]+2.2,89.35,34.8),(root[0]+3.8,89.35,32.5),(root[0]+4.6,89.35,29.1)],.8,.18)
    for i,(y,end) in enumerate([(18.2,26),(33.8,14.2),(47.6,29)]):
        # Roots sit in the existing outer guard, below its balustrade cap.
        g.box('natural garden guard root pocket',1.35,y-.5,41.8,.8,1,.7,'pot')
        vine('garden wall trailing ivy '+str(i),[(1.6,y,42.5),(1.3,y+.7,38),(1.2,y+2,34),(1.25,y+.8,end)],.85,.12)


def rock_planting():
    for i,o in enumerate([q for q in g.objects if q['name']=='natural rock planting anchor']):
        rr=rr_for('rock planting '+str(i));old=a.rng;a.rng=rr
        try:
            x,y,z=o['origin'];rim=o['rim']
            a.cluster(x,y,z+.5,rr.uniform(.65,1.3),.025)
            # Fern-shaped fronds and dry tufts root at crevices, with most rock left bare.
            for j in range(rr.randint(3,6)):
                theta=rr.random()*math.tau;length=rr.uniform(1.2,2.8)
                tip=(x+math.cos(theta)*length,y+math.sin(theta)*length,z+.6)
                mid=(x+math.cos(theta)*length*.5,y+math.sin(theta)*length*.5,z+1.5)
                a.tube((x,y,z),mid,.035,'foliage_dark',4);a.tube(mid,tip,.025,'foliage_dark',4)
                for t in np.linspace(.2,1,4):
                    px=x+(tip[0]-x)*t;py=y+(tip[1]-y)*t;pz=z+.4+math.sin(t*math.pi)*1.1
                    a.leaf(px,py,pz,.7)
            if i%3==1 and z>9:
                vine('crevice ivy '+str(i),[(x,y,z+.3),(rim[0],rim[1],z+.2),(rim[0]+.25,rim[1]+.15,z-2.2),(rim[0]-.6,rim[1]+.12,z-4)],.6,.035)
        finally:a.rng=old


def planted_pot(name,x,y,z,r,h,kind,R):
    rr=rr_for(name);old=a.rng;a.rng=rr
    try:
        col=rr.choice(['pot','pot','pot_faded'])
        a.spindle(x,y,z,[(0,r*.58),(.14,r*.7),(h*.78,r*.9),(h*.88,r),(h,r)],col,12)
        a.spindle(x,y,z+h,[(0,r*.86),(.04,r*.86)],'soil',12)
        # The full plant mesh is clamped to its declared conservative horizontal envelope.
        start=len(g.triangles)
        if kind=='citrus':
            a.tube((x,y,z+h),(x+.1,y,z+h+2.6),.085,'timber')
            for k in range(5):
                ang=rr.random()*math.tau;tip=(x+math.cos(ang)*.65,y+math.sin(ang)*.65,z+h+rr.uniform(2.1,3.2))
                a.tube((x,y,z+h+1.5),tip,.04,'timber',5);a.cluster(*tip,.65,.015)
                a.spindle(tip[0],tip[1]-.3,tip[2],[(0,.1),(.14,.17),(.28,.08)],'citrus_fruit',8)
        else:
            for k in range(5 if kind=='rose' else 4):
                dx,dy=rr.uniform(-r*.5,r*.5),rr.uniform(-r*.5,r*.5);zz=z+h+rr.uniform(.5,1.5)
                a.tube((x,y,z+h),(x+dx,y+dy,zz),.03,'foliage_dark',4)
                a.cluster(x+dx,y+dy,zz,r*.65,.5 if kind=='rose' else .03)
        foliage=np.array([v for _,tri in g.triangles[start:] for v in tri])
        sx=min(1,R/max(abs(foliage[:,0]-x)));sy=min(1,R/max(abs(foliage[:,2]-y)))
        for j in range(start,len(g.triangles)):
            color,tri=g.triangles[j]
            g.triangles[j]=(color,[(x+(xx-x)*sx,zz,y+(yy-y)*sy) for xx,zz,yy in tri])
        g.objects.append(dict(name='natural planted pot',label=name,origin=[x-R,y-R,z],size=[2*R,2*R,h+(4.3 if kind=='citrus' else 2.8)],collision_rect=[x-R,y-R,2*R,2*R],level=z,plant=kind))
    finally:a.rng=old


def author():
    terrain_aprons()
    g.COLORS.update(pot_faded='C88C68',citrus_fruit='D5AE48',cliff1='93978E',cliff2='B1B0A2',cliff3='C2BDAA',cliff4='A5A596')
    for p in POTS:planted_pot(*p)
    # Potted accents stand on widened masonry landings OUTSIDE the clear stair width.
    for i,(x,y,z,r,h,kind) in enumerate([(40.8,80.9,20.8,.75,1.8,'rose'),(61.5,85.8,20.8,.6,1.5,'herb'),(40.8,104.2,6.4,.65,1.7,'rose')]):
        g.box('natural stair planter ledge',x-1.15,y-1.15,.25,2.3,2.3,z-.25,'stone')
        planted_pot('Stair ledge '+str(i),x,y,z,r,h,kind,1.05)
    rock_planting()
    g.objects.append(dict(name='natural landscape scope',seed=SEED,reference='reference-concept.png',rock='irregular interlocking buttresses and talus within preserved envelopes',creepers='continuous rooted stems with tapered asymmetric branches'))


def terrain_aprons():
    """Closed rock aprons join outcrops into continuous slopes outside circulation.
    A jittered triangulation avoids a square-grid silhouette. Every vertex is bounded
    by these external zones and below the nearest terrace floor.
    """
    for label,x0,y0,w,d,top in [('west cliff toe',2.8,53,39.5,56,30),('pool cliff toe',59.7,88.3,35.5,20.5,19),('service cliff toe',96,82.5,30.3,26.3,7.8)]:
        rr=rr_for(label);nx=max(4,round(w/4));ny=max(4,round(d/4));vertices=[]
        for j in range(ny+1):
            row=[]
            for i in range(nx+1):
                xx=x0+w*i/nx+(rr.uniform(-.9,.9) if 0<i<nx else 0)
                yy=y0+d*j/ny+(rr.uniform(-.9,.9) if 0<j<ny else 0)
                progress=(yy-y0)/d
                h=.6+top*(1-progress)**.9
                h+=rr.uniform(-2.3,2.3)*(1-progress)
                # The seaward boundary resolves into low irregular shelves, not a vertical block.
                if i in (0,nx):h*=rr.uniform(.28,.5)
                if j==ny:h=rr.uniform(.35,1.3)
                row.append((xx,yy,max(.3,min(top,h))))
            vertices.append(row)
        for j in range(ny):
            for i in range(nx):
                aa,bb,cc,dd=vertices[j][i],vertices[j][i+1],vertices[j+1][i+1],vertices[j+1][i]
                color='cliff2'
                if (i+j)%2:a.face([aa,bb,dd],color);a.face([bb,cc,dd],color)
                else:a.face([aa,bb,cc],color);a.face([aa,cc,dd],color)
        edge=vertices[0]+[row[-1] for row in vertices[1:]]+vertices[-1][-2::-1]+[row[0] for row in vertices[-2:0:-1]]
        for aa,bb in zip(edge,edge[1:]+edge[:1]):a.face([aa,bb,(bb[0],bb[1],.25),(aa[0],aa[1],.25)],'cliff2')
        for aa,bb in zip(edge,edge[1:]+edge[:1]):
            a.face([(x0+w/2,y0+d/2,.25),(aa[0],aa[1],.25),(bb[0],bb[1],.25)],'cliff2')
        apron_boulders(label,vertices,rr,x0,y0,w,d)
        g.objects.append(dict(name='natural connecting rock apron',label=label,origin=[x0,y0,.25],size=[w,d,top-.25],walkable=False))


def apron_boulders(label,grid,rr,x0,y0,w,d):
    # Compute exact triangle height at each contact point on the authored slope.
    triangles=[]
    for j in range(len(grid)-1):
        for i in range(len(grid[0])-1):
            aa,bb,cc,dd=grid[j][i],grid[j][i+1],grid[j+1][i+1],grid[j+1][i]
            triangles.extend([(aa,bb,dd),(bb,cc,dd)] if (i+j)%2 else [(aa,bb,cc),(aa,cc,dd)])
    def surface(x,y):
        for tri in triangles:
            aa,bb,cc=np.array(tri)
            v0=bb[:2]-aa[:2];v1=cc[:2]-aa[:2];v2=np.array([x,y])-aa[:2]
            det=v0[0]*v1[1]-v1[0]*v0[1]
            u=(v2[0]*v1[1]-v1[0]*v2[1])/det;v=(v0[0]*v2[1]-v2[0]*v0[1])/det
            if u>=-1e-6 and v>=-1e-6 and u+v<=1+1e-6:return aa[2]+u*(bb[2]-aa[2])+v*(cc[2]-aa[2])
        return .25
    # Remove buried former crown anchors, keeping planting rooted on exposed surfaces.
    g.objects[:]=[o for o in g.objects if not (o['name']=='natural rock planting anchor' and x0<=o['origin'][0]<=x0+w and y0<=o['origin'][1]<=y0+d and surface(*o['origin'][:2])>o['origin'][2]+.05)]
    centers=[];target=round(w*d/25)
    for attempt in range(target*12):
        x=rr.uniform(x0+2.1,x0+w-2.1);y=rr.uniform(y0+2.1,y0+d-2.1)
        if any(math.hypot(x-xx,y-yy)<3.3 for xx,yy in centers):continue
        centers.append((x,y));radius=rr.uniform(1.7,3.0);height=rr.uniform(2.0,5.1)
        theta=rr.uniform(-.22,.22);n=8
        # Broken rectangular blocks with clipped corners, not round hexagonal boulders.
        outline=[(-.8,-.55),(-.48,-.83),(.59,-.83),(.91,-.45),(.77,.57),(.44,.83),(-.65,.7),(-.92,.32)]
        rim=[(x+radius*(xx*math.cos(theta)-yy*math.sin(theta)),y+radius*(xx*math.sin(theta)+yy*math.cos(theta))) for xx,yy in outline]
        rim=[(max(x0+.1,min(x0+w-.1,xx)),max(y0+.1,min(y0+d-.1,yy))) for xx,yy in rim]
        bottom=min(surface(xx,yy) for xx,yy in rim)-.35
        top=max(surface(x,y)+height*.5,bottom+height)
        lo=[(xx,yy,max(.25,bottom)) for xx,yy in rim]
        mid=[(xx,yy,bottom+(top-bottom)*.5) for xx,yy in rim]
        hi=[(x+(xx-x)*rr.uniform(.65,.9),y+(yy-y)*rr.uniform(.7,.9),top+rr.uniform(-.2,.2)) for xx,yy in rim]
        col=rr.choice(['cliff1','cliff2','cliff2','cliff3','cliff4'])
        for a_ring,b_ring in [(lo,mid),(mid,hi)]:
            for k in range(n):a.face([a_ring[k],a_ring[(k+1)%n],b_ring[(k+1)%n],b_ring[k]],col)
        # Triangulate from the crown center so the support height is explicit.
        crown=(sum(p[0] for p in hi)/n,sum(p[1] for p in hi)/n,top)
        for k in range(n):a.face([crown,hi[k],hi[(k+1)%n]],col)
        a.face(lo[::-1],col)
        g.objects.append(dict(name='natural slope boulder',zone=label,root=[x,y,max(.25,bottom)],top=top))
        if len(centers)%5==2:
            g.objects.append(dict(name='natural rock planting anchor',origin=list(crown),rim=list(max(hi,key=lambda p:p[1])),envelope=label))
        if len(centers)>=target:break
