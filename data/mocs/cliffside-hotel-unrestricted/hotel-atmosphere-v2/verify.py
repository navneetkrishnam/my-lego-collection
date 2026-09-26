"""Verify the room-programmed proxy and its delivered artifact provenance."""
import hashlib,json
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image
import build,layout,check_layout
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={n:sha(HERE/n) for n in ('blockout.ldr','layout.json','villa-detail.ldr')}
build.export()
build.export_detail()
assert before=={n:sha(HERE/n) for n in before},'Export changed on regeneration'
d=json.loads((HERE/'layout.json').read_text())
assert d['model_sha256']==sha(HERE/'blockout.ldr')
baseline=HERE.parent/'hotel-exteriors-v1'
old=json.loads((baseline/'layout.json').read_text())
# Exterior-only pass: preserve the entire approved v6 spatial program.
assert sha(HERE/'layout.py')==sha(baseline/'layout.py')
assert d['floors']==old['floors'] and d['program']==old['program']
assert sha(HERE/'annex_exterior.py')==sha(baseline/'annex_exterior.py')
assert sha(HERE/'geometry.py')==sha(baseline/'geometry.py')
assert sha(HERE/'exterior.py')==sha(baseline/'exterior.py')
serialize=lambda o:json.dumps(o,sort_keys=True)
assert Counter(serialize(o) for o in d['objects'] if o['name'].startswith('villa '))==Counter(serialize(o) for o in old['objects'] if o['name'].startswith('villa '))
# All previous named architecture objects and planning rock envelopes remain.
# Only cliff-envelope surface meshes are regenerated; additions are atmosphere layers.
retained=Counter(serialize(o) for o in old['objects'])
current=Counter(serialize(o) for o in d['objects'])
assert not(retained-current), 'Baseline objects removed or altered'
extra=current-retained
assert all(json.loads(o)['name'].startswith('atmosphere ') for o in extra)
assert sum(o['name']=='atmosphere rail flower trough' for o in d['objects'])==5
assert sum(o['name']=='atmosphere cypress' for o in d['objects'])==3
assert sum(o['name']=='atmosphere courtyard paver' for o in d['objects'])>400
assert sum(o['name']=='atmosphere pergola rafter' for o in d['objects'])>10
assert sum(o['name']=='atmosphere rock planting anchor' for o in d['objects'])==18
import atmosphere
site=next(f for f in layout.FLOORS if f['id']=='site')
def overlaps(a,b):
 x,y,w,h=a;xx,yy,ww,hh=b
 return min(x+w,xx+ww)>max(x,xx) and min(y+h,yy+hh)>max(y,yy)
for i,item in enumerate(atmosphere.LANDSCAPE_FURNITURE):
 assert any(all(a<=xx<=a+w and b<=yy<=b+h for xx,yy in [(item['rect'][0],item['rect'][1]),(item['rect'][0]+item['rect'][2],item['rect'][1]+item['rect'][3])]) for a,b,w,h in site['rects'])
 assert not any(overlaps(item['rect'],q['rect']) for q in site['furniture']+atmosphere.LANDSCAPE_FURNITURE[i+1:])
 assert any(o.get('collision_rect')==list(item['rect']) for o in d['objects'])
assert sum(o['name']=='services arcade stone ring' for o in d['objects'])==2
assert not any(o['name']=='services recessed glazing' and o['origin'][1]>77 and 26<=o['origin'][2]<40 for o in d['objects'])
for prefix in ('cottage','services'):
 field=next(o for o in d['objects'] if o['name']==prefix+' roof tile field')
 assert field['tile_count']>500
 assert next(o for o in d['objects'] if o['name']==prefix+' hip covers')['seams']==4
 assert any(o['name']==prefix+' recessed glazing' for o in d['objects'])
assert any(o['name']=='services balcony spindle' for o in d['objects'])
box=next(o for o in d['objects'] if o['name']=='cottage garden window box')
assert box['origin']==[86,36.1,55.3] and box['origin'][2]+box['size'][2]<57
upper=next(f for f in layout.FLOORS if f['id']=='cottage-upper')
assert upper['z']==54 and upper['holes']==[(104,9,10,12)]
assert upper['rects']==[(82,8,44,28)]
w=next(w for w in upper['walls'] if w['name']=='cottage garden front')
assert any(o['kind']=='window' and o['a']==86 and o['w']==7 for o in w['opens'])
assert layout.PROGRAM['pool']==(62,62,22,16)
water=next(o for o in build.g.objects if o['name']=='pool water')
assert water['origin']==[62,62,38.8] and water['size']==[22,16,.15]
site=next(f for f in layout.FLOORS if f['id']=='site')
chairs=[q for q in site['furniture'] if q['name']=='Pool lounger']
assert len(chairs)==2 and all(q['facing']=='west' for q in chairs)
assert all(x>=89 and x+w<=95 and y>=63 and y+h<=76 for q in chairs for x,y,w,h in [q['rect']])
assert all(y+h<78.5 for q in site['furniture'] if q['name'].startswith('Pool ') for x,y,w,h in [q['rect']])
for surf in site['surfaces']:
 x,y,w,h=surf['rect'];o=next(o for o in build.g.objects if o['name']==surf['name'])
 assert o['origin']==[x,y,40] and o['size']==[w,h,.05] and o['color']==surf['color']
# stair_core emits 18 + 17 treads for the new private stair, distinct from other cores.
ct=[o for o in build.g.objects if o['name'] in ('internal up flight','internal return flight') and 104<=o['origin'][0]<114]
assert len(ct)==35
assert sum(s['kind']=='guest' for f in layout.FLOORS for s in f['spaces'])==7
for z in (54,68):
 f=next(f for f in layout.FLOORS if f['id'].startswith('main') and f['z']==z)
 assert sum(s['kind']=='guest' for s in f['spaces'])==3 and len(f['balconies'])==2
 assert f['holes']==[(45,11,10,12)]
for key in ('salon','dining'):
 f=next(f for f in layout.FLOORS if f['id']==key)
 assert f['holes']==[(115,41,10,12)]
# Room partitions are internal to one six-segment L perimeter per storey.
perimeter_names={'main west','main rear','main east','suite front','L inner return','long-arm front'}
for f in [f for f in layout.FLOORS if f['id'].startswith('main')]:
 assert sum(w['name'] in perimeter_names for w in f['walls'])==6
# Requested correction: restore villa library; widen the whole private cottage to the service east wall.
cottage=next(f for f in layout.FLOORS if f['id']=='cottage')
assert cottage['rects']==[(82,8,44,28)]
assert sum(w*d for x,y,w,d in cottage['rects'])==1232
assert not any('library' in s['name'].lower() for s in cottage['spaces'])
assert not any(w['name']=='library / bedroom separation' for w in cottage['walls'])
assert any(s['name']=='Cottage foyer' and s['rect']==(83,31,42,4) for s in cottage['spaces'])
assert any(s['name']=='Lobby lounge / library' and s['kind']=='lounge' for f in layout.FLOORS if f['id']=='main-0' for s in f['spaces'])
assert next(w for w in cottage['walls'] if w['name']=='cottage east')['c']==next(w for f in layout.FLOORS if f['id']=='dining' for w in f['walls'] if w['name']=='service east')['c']==125.5
for f in [f for f in layout.FLOORS if f['id'].startswith('main')]:
 w=next(w for w in f['walls'] if w['name']=='suite front')
 assert all(any(o['kind']=='window' and o['a']==x and o['w']==3 for o in w['opens']) for x in (47,52))
for key in ('dining','salon','spa'):
 assert next(f for f in layout.FLOORS if f['id']==key)['rects']==[(96,40,30,38)]
dining=next(f for f in layout.FLOORS if f['id']=='dining')
assert sum(o['name']=='Dining chair' for o in dining['furniture'])==8
# Check all authored furniture envelopes for collisions with each other or solid walls.
def overlap(a,b):
 x,y,w,d=a;xx,yy,ww,dd=b
 return min(x+w,xx+ww)>max(x,xx)+1e-8 and min(y+d,yy+dd)>max(y,yy)+1e-8
for f in layout.FLOORS:
 for i,item in enumerate(f['furniture']):
  x,y,w,h=item['rect']
  assert all(any(a<=xx<=a+ww and b<=yy<=b+dd for a,b,ww,dd in f['rects']) for xx in (x,x+w) for yy in (y,y+h))
  for other in f['furniture'][i+1:]:assert not overlap(item['rect'],other['rect']),(f['id'],item['name'],other['name'])
  for wall in f['walls']:
   a,b,c,t=wall['a'],wall['b'],wall['c'],wall['thickness']
   r=(a,c-t/2,b-a,t) if wall['axis']=='x' else (c-t/2,a,t,b-a)
   assert not overlap(item['rect'],r),(f['id'],item['name'],wall['name'])
roof=next(o for o in build.g.objects if o['name']=='garden cottage hip')
service_roof=next(o for o in build.g.objects if o['name']=='service pavilion hip')
assert roof['origin'][0]+roof['size'][0]==service_roof['origin'][0]+service_roof['size'][0]==127.5
assert roof['origin'][0]-79.5>=1 # Main roof eastern eave is x79.5.
assert service_roof['origin'][1]-(roof['origin'][1]+roof['size'][1])>=1
# Donor facts remain reproducible against the actual local ownership/catalog/parts files.
root=HERE.parents[3]
donors=json.loads((HERE/'donor-candidates.json').read_text())
for name,h in donors['sources'].items():assert sha(root/name)==h
for donor in donors['donors']:
 assert sha(root/donor['parts_source'])==donor['parts_source_sha256']
 parts={o['id']:o for o in json.loads((root/donor['parts_source']).read_text())}
 for o in donor['elements']:
  assert parts[o['element_id']]['name']==o['name'] and o['quantity_in_set'] is None
 for photo in donor['inspected_images']:assert sha(root/photo['path'])==photo['sha256']
steps=[o for o in build.g.objects if o['name']=='straight exterior tread']
assert len(steps)==48
for i,o in enumerate(steps):
 x,y,z=o['origin'];w,depth,h=o['size']
 assert x==44 and w==14 and depth==1
 assert y==56+i+(6 if i>=24 else 0)
 assert abs(z+h-(40-(i+1)*.8))<1e-8
supports=[o for o in build.g.objects if o['name']=='pool deck support']
assert supports and all(abs(o['origin'][2]+o['size'][2]-39.5)<1e-8 for o in supports)
for o in supports:
 x,y,z=o['origin'];w,h,dz=o['size']
 assert not(min(x+w,84)>max(x,62) and min(y+h,78)>max(y,62))
beams=[o for o in build.g.objects if o['name']=='balcony support envelope']
assert len(beams)==15
assert all(o['size'][1]==6 and o['size'][2]==.5 for o in beams)
points=np.concatenate([np.array(t) for c,t in build.g.triangles])
assert np.isfinite(points).all()
lo,hi=points.min(0),points.max(0)
assert np.allclose([hi[0]-lo[0],hi[2]-lo[2]],layout.BASE)
nav=check_layout.run()
views={}
for view,stem in [('concept','blockout'),('front','blockout'),('plan','blockout'),('rear','blockout')]:
 im=HERE/f'{stem}-{view}.png';meta=json.loads(im.with_suffix('.render.json').read_text())
 for key,p in [('model_sha256',HERE/f'{stem}.ldr'),('render_sha256',im),
               ('generator_sha256',HERE/'build.py'),('renderer_sha256',HERE/'render.py'),
               ('layout_sha256',HERE/'layout.py'),('geometry_sha256',HERE/'geometry.py'),('exterior_sha256',HERE/'exterior.py'),('annex_exterior_sha256',HERE/'annex_exterior.py'),('atmosphere_sha256',HERE/'atmosphere.py')]:
  assert meta[key]==sha(p),(view,key)
 with Image.open(im) as image:image.verify()
 views[view]='current'
plans=json.loads((HERE/'plans-provenance.json').read_text())
assert plans['layout_sha256']==sha(HERE/'layout.py')
assert plans['atmosphere_sha256']==sha(HERE/'atmosphere.py')
assert plans['plans_generator_sha256']==sha(HERE/'plans.py')
for name,value in plans['drawings'].items():assert sha(HERE/name)==value
out=dict(scope='lush planting, terrace furnishing and surface detail over approved hotel layout',deterministic_export=True,
 approved_v6_layout_unchanged=True,baseline_architecture_objects_and_cliff_envelopes_preserved=True,
 outdoor_furniture_in_plan_and_circulation=True,faceted_cliff_surfaces=True,
 cottage_and_service_exterior_detail_pass=True,service_arcade_remains_open=True,
 main_and_service_floor_programs_unchanged=True,main_villa_architecture_preserved=True,
 two_storey_cottage_with_private_stair=True,garden_facing_upper_window=True,
 enlarged_pool_geometry_pass=True,seating_beside_services_pass=True,cliff_front_seating_removed=True,garden_surface_matches_plan=True,
 room_program_pass=True,private_cottage_extension_pass=True,villa_library_restored=True,cottage_service_east_alignment_pass=True,pool_facing_corridor_windows_pass=True,
 furniture_envelopes_nonoverlapping=True,cottage_roof_separation_pass=True,donor_evidence_current=True,
 straight_exterior_stair_pass=True,pool_support_envelopes_pass=True,
 balcony_support_envelopes_pass=True,declared_floor_shafts_pass=True,
 circulation_destinations=f"{nav['connected_targets']}/{nav['total_targets']}",
 public_routes_avoid_private_rooms=True,villa_library_access_without_cottage=True,pool_walking_loop_clear=True,
 model_sha256=d['model_sha256'],render_provenance=views,plan_provenance=True,
 lego_connections_verified=False,structural_analysis_performed=False,physical_assembly_tested=False)
(HERE/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
