"""Single source of room, opening, circulation and floor geometry (stud units)."""
BASE=(128,114)
MAIN_POLYGON=[(20,10),(78,10),(78,32),(44,32),(44,52),(20,52)]
FLOORS=[]

def floor(key,z,rects,holes=()):
    f=dict(id=key,z=z,rects=list(rects),holes=list(holes),walls=[],spaces=[],furniture=[],balconies=[])
    FLOORS.append(f);return f

def opening(a,w,kind='window',sill=3,height=7):
    return dict(a=a,w=w,kind=kind,sill=0 if kind=='door' else sill,height=9 if kind=='door' else height)

def wall(f,name,axis,c,a,b,opens=(),thickness=1):
    assert b>a
    for o in opens: assert a<=o['a']<o['a']+o['w']<=b,(name,o,a,b)
    f['walls'].append(dict(name=name,axis=axis,c=c,a=a,b=b,opens=list(opens),thickness=thickness,height=14))

def space(f,name,rect,node,kind='shared',parent=None):
    f['spaces'].append(dict(name=name,rect=rect,node=node,kind=kind,parent=parent))

def furniture(f,name,rect,height=2.5):
    f['furniture'].append(dict(name=name,rect=rect,height=height))

def bath(f,prefix,x,y):
    wall(f,prefix+' side','y',x+6.5,y,y+7)
    wall(f,prefix+' front','x',y+6.5,x,x+7,[opening(x+2,3,'door')])
    space(f,prefix,(x+.5,y+.5,5.5,5.5),(x+3,y+3),'bath')

# Main villa: a single L perimeter, never two overlapping building shells.
for idx,z in enumerate((40,54,68)):
    f=floor('main-'+str(idx),z,[(20,10,24,42),(44,10,34,22)],[(45,11,10,12)] if idx else [])
    wall(f,'main west','y',20.5,10,52,[opening(18,6),opening(38,6)] if idx else [opening(17,6),opening(40,4,'door')])
    wall(f,'main rear','x',10.5,20,78,[opening(24,5),opening(34,3),opening(66,7)])
    wall(f,'main east','y',77.5,10,32,[opening(18,7)])
    wall(f,'suite front','x',31.5,44,78,[opening(65,4,'door'),opening(72,3)] if idx else [opening(64,9)])
    wall(f,'L inner return','y',43.5,32,52,[opening(36,3),opening(44,3)] if idx else [opening(41,4,'door')])
    wall(f,'long-arm front','x',51.5,20,44,[opening(26,4,'door'),opening(33,4)] if idx else [opening(25,9)])
    # Core and suite boundary; corridor connects around the front of this core.
    wall(f,'main core west','y',44.5,10,26)
    wall(f,'main core east / suite entry','y',56.5,10,32,[opening(27,3,'door')])
    wall(f,'main core south','x',25.5,44,56,[opening(49,4,'door')])
    space(f,'Main stair landing',(45,23,10,2),(51,24),'stair')
    space(f,'Common corridor',(39,26,17,5),(42,28),'circulation')
    if idx:
        wall(f,'room access wall','y',38.5,10,52,[opening(25,3,'door'),opening(44,3,'door')])
        wall(f,'two-room separation','x',30.5,20,39)
        space(f,'Garden room — no balcony',(21,11,17,19),(27,23),'guest')
        space(f,'Corner room — balcony',(21,31,17,20),(27,41),'guest')
        space(f,'Extended suite — balcony',(57,11,20,20),(68,23),'guest')
        # Ensuite locations align vertically on the two guest floors.
        bath(f,'Garden room bath',31.5,10.5)
        bath(f,'Corner room bath',31.5,30.5)
        # Suite bath sits in its rear-left corner, opening into the suite.
        bath(f,'Suite bath',56.5,10.5)
        f['balconies']=[dict(name='Corner room balcony',rect=(22,52,15,4),node=(28,54)),
                        dict(name='Extended suite balcony',rect=(60,32,16,4),node=(67,34))]
        furniture(f,'Garden room bed',(23,13,6,8))
        furniture(f,'Corner room bed',(23,33,6,8))
        furniture(f,'Suite bed',(67,13,6,8))
    else:
        space(f,'Lobby / front desk',(21,25,22,26),(35,40),'lobby')
        space(f,'Lobby lounge / library',(57,11,20,20),(68,22),'lounge')
        wall(f,'Back office front','x',22.5,20,32,[opening(25,3,'door')])
        wall(f,'Back office east','y',31.5,10,23)
        space(f,'Back office',(21,11,10,11),(26,17),'service')
        bath(f,'Lobby WC',31.5,10.5)
        furniture(f,'Reception desk',(26,32,8,2),3)
        furniture(f,'Lobby sofa',(23,46,7,2),2)
        furniture(f,'Library sofa',(66,24,7,2),2)

# Cottage is one storey with its own front garden door.
f=floor('cottage',40,[(80,10,16,20)])
wall(f,'cottage west','y',80.5,10,30,[opening(17,5)])
wall(f,'cottage east','y',95.5,10,30,[opening(20,5)])
wall(f,'cottage rear','x',10.5,80,96,[opening(83,4)])
wall(f,'cottage garden front','x',29.5,80,96,[opening(85,4,'door'),opening(91,3)])
bath(f,'Cottage bath',88.5,10.5)
space(f,'Garden cottage',(81,11,14,18),(86,25),'guest')
furniture(f,'Cottage bed',(82,13,6,8))

# Dining, salon and spa share a vertically aligned core and wet-service zone.
for z,key in [(12,'spa'),(26,'salon'),(40,'dining')]:
    f=floor(key,z,[(96,40,30,30)],[(115,41,10,12)] if z>12 else [])
    wall(f,'service west','y',96.5,40,70,[opening(47,5),opening(56,3,'door')] if z==40 else [opening(47,5),opening(62,5)])
    wall(f,'service east','y',125.5,40,70,[opening(61,6)])
    wall(f,'service rear','x',40.5,96,126,[opening(100,6)])
    if z==26:
        # The front wall becomes an open arcade, authored as arches in 3D.
        wall(f,'open arcade front','x',69.5,96,126,[opening(99,10,'door'),opening(112,10,'door')])
    else:
        wall(f,'service front','x',69.5,96,126,[opening(100,7),opening(114,7)])
    wall(f,'service core west','y',114.5,40,56)
    wall(f,'service core south','x',55.5,114,126,[opening(119,4,'door')])
    wall(f,'rear program front','x',55.5,96,114,[opening(107,3,'door')])
    space(f,'Service stair landing',(115,53,10,2),(120,54),'stair')
    space(f,'Service corridor',(97,56,28,4),(111,57.5),'circulation')
    if z==40:
        space(f,'Kitchen / pantry',(97,41,17,14),(104,51),'service')
        space(f,'Restaurant / pool bar',(97,60,28,9),(111,61),'dining')
        furniture(f,'Kitchen worktop',(98,42,10,2),3)
        furniture(f,'Pool bar counter',(98,60,2,8),3)
        for x in (102,110,118): furniture(f,'Dining table',(x,63,3,3),2.5)
    elif z==26:
        space(f,'Salon',(97,41,17,14),(104,51),'salon')
        space(f,'Quiet lounge / arcade',(97,60,28,9),(111,62),'lounge')
        f['balconies']=[dict(name='Salon lounge terrace',rect=(98,70,26,4),node=(114,72))]
        furniture(f,'Salon stations',(98,42,2,10),3)
    else:
        wall(f,'Treatment separation','y',104.5,40,56)
        # Replace the rear partition with one door per treatment room.
        f['walls']=[w for w in f['walls'] if w['name']!='rear program front']
        wall(f,'Treatment doors','x',55.5,96,114,[opening(100,3,'door'),opening(108,3,'door')])
        space(f,'Treatment 1',(97,41,7,14),(101,50),'spa')
        space(f,'Treatment 2',(105,41,9,14),(109,50),'spa')
        wall(f,'Changing partition','y',109.5,60,70,[opening(63,3,'door')])
        wall(f,'Changing front','x',59.5,96,110,[opening(104,3,'door')])
        space(f,'Changing / showers',(97,60,12,9),(105,63),'bath')
        space(f,'Spa relaxation',(110,60,15,9),(119,63),'spa')
        furniture(f,'Treatment bed 1',(98,43,4,7),2)
        furniture(f,'Treatment bed 2',(106,43,4,7),2)

f=floor('site',40,[(2,12,18,40),(20,52,24,4),(44,32,34,24),
                   (78,30,18,30),(58,54,38,34)],[(66,64,22,12)])
space(f,'Common side garden',(2,12,18,40),(17,40),'garden')
space(f,'Arrival court',(44,36,34,20),(51,44),'circulation')
space(f,'Cottage garden',(80,32,16,14),(81,38),'garden')
space(f,'Shared access promenade',(78,46,18,14),(87,53),'circulation')
space(f,'Pool deck',(58,54,38,34),(62,61),'pool')
for x in (64,74,84): furniture(f,'Pool lounger',(x,81,4,6),1)
for name,r in [('Side garden north bed',(4,15,13,5)),('Side garden south bed',(4,45,13,5)),
               ('Cottage garden bed',(84,34,10,2))]: furniture(f,name,r,1)

PROGRAM=dict(main_guest_rooms=6,cottage_rooms=1,guest_floor_levels=[54,68],
             main_stair=[(45,11,10,14),[40,54,68]],service_stair=[(115,41,10,14),[12,26,40]],
             pool=(66,64,22,12),pool_deck=(58,54,38,34),
             exterior_stair=dict(x=44,width=14,start_y=56,risers=48,rise=.8,tread=1,landing_depth=6,top=40,bottom=1.6))

# Low perimeter guards stop at doorways and shared circulation interfaces.
site=next(f for f in FLOORS if f['id']=='site')
for name,axis,c,a,b in [('Garden outer guard','y',2.25,12,52),('Garden front guard','x',51.75,2,20),
                       ('Garden rear guard','x',12.25,2,20),('Pool left guard','y',58.25,56,88),
                       ('Pool front guard','x',87.75,58,96),('Pool outer right guard','y',95.75,70,88)]:
    wall(site,name,axis,c,a,b,thickness=.5)
    site['walls'][-1]['height']=2.2
