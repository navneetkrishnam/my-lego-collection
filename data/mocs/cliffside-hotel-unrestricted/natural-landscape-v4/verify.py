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
baseline=HERE.parent/'garden-pool-v3'
old=json.loads((baseline/'layout.json').read_text())
# Exterior-only pass: preserve the entire approved v6 spatial program.
assert sha(HERE/'layout.py')==sha(baseline/'layout.py')
assert d['floors']==old['floors'] and d['program']==old['program']
assert sha(HERE/'annex_exterior.py')==sha(baseline/'annex_exterior.py')
assert sha(HERE/'geometry.py')==sha(baseline/'geometry.py')
assert sha(HERE/'exterior.py')==sha(baseline/'exterior.py')
assert sha(HERE/'garden_pool.py')==sha(baseline/'garden_pool.py')
serialize=lambda o:json.dumps(o,sort_keys=True)
assert Counter(serialize(o) for o in d['objects'] if o['name'].startswith('villa '))==Counter(serialize(o) for o in old['objects'] if o['name'].startswith('villa '))
# Preserve architecture and amenities, while intentionally replacing decorative planting/rock.
architecture=lambda o:not o['name'].startswith(('atmosphere ','natural '))
retained=Counter(serialize(o) for o in old['objects'] if architecture(o))
current=Counter(serialize(o) for o in d['objects'] if architecture(o))
assert retained==current,'Architecture or garden/pool amenity records changed'
assert sum(o['name']=='atmosphere rail flower trough' for o in d['objects'])==5
assert sum(o['name']=='atmosphere cypress' for o in d['objects'])==3
assert sum(o['name']=='atmosphere courtyard paver' for o in d['objects'])>400
assert sum(o['name']=='atmosphere pergola rafter' for o in d['objects'])>10
assert sum(o['name']=='natural fractured rock' for o in d['objects'])>70
assert sum(o['name']=='natural rock planting anchor' for o in d['objects'])>12
import atmosphere,garden_pool,natural
site=next(f for f in layout.FLOORS if f['id']=='site')
def overlaps(a,b):
 x,y,w,h=a;xx,yy,ww,hh=b
 return min(x+w,xx+ww)>max(x,xx) and min(y+h,yy+hh)>max(y,yy)
outdoor=atmosphere.LANDSCAPE_FURNITURE+garden_pool.SITE_ITEMS
for i,item in enumerate(outdoor):
 assert any(all(a<=xx<=a+w and b<=yy<=b+h for xx,yy in [(item['rect'][0],item['rect'][1]),(item['rect'][0]+item['rect'][2],item['rect'][1]+item['rect'][3])]) for a,b,w,h in site['rects'])
 assert not any(overlaps(item['rect'],q['rect']) for q in site['furniture']+outdoor[i+1:])
 assert any(o.get('collision_rect')==list(item['rect']) for o in d['objects'])
# All new standing plants reserve their entire horizontal foliage envelope.
for item in natural.POT_ITEMS:
 floors=[f for f in layout.FLOORS if f['z']==item['level']]
 plates=[r for f in floors for r in f['rects']+[b['rect'] for b in f['balconies']]]
 x,y,w,h=item['rect']
 assert any(a<=x and b<=y and x+w<=a+ww and y+h<=b+hh for a,b,ww,hh in plates),item['name']
 obstacles=[q for f in floors for q in f['furniture']]
 if item['level']==40:
  obstacles+=outdoor
  for name,xx,yy,ww,hh in layout.PROGRAM['pergolas']:
   obstacles += [dict(rect=(u,v,1,1)) for u in (xx,xx+ww-1) for v in (yy,yy+hh-1)]
 assert not any(overlaps(item['rect'],q['rect']) for q in obstacles),item['name']
 for f in floors:
  for wall in f['walls']:
   a,b,c,t=wall['a'],wall['b'],wall['c'],wall['thickness']
   wr=(a,c-t/2,b-a,t) if wall['axis']=='x' else (c-t/2,a,t,b-a)
   assert not overlaps(item['rect'],wr),(item['name'],wall['name'])
 for q in natural.POT_ITEMS:
  if q is not item and q['level']==item['level']:assert not overlaps(item['rect'],q['rect']),(item['name'],q['name'])
 assert any(o['name']=='natural planted pot' and o['label']==item['name'] and o['collision_rect']==list(item['rect']) for o in d['objects'])
assert sum(o['name']=='natural planted pot' for o in d['objects'])==21
ledges=[o for o in d['objects'] if o['name']=='natural stair planter ledge']
assert len(ledges)==3
for o in ledges:
 x,y,z=o['origin'];w,h,dz=o['size']
 assert x+w<42.8 or x>59.2,'Stair planter encroaches on stair or guard'
assert len(natural.CASCADE_ROOTS)==3 and len({q[2] for q in natural.CASCADE_ROOTS})==3
assert not any(o['name']=='atmosphere climber pool retaining cascade' for o in d['objects'])
aprons=[o for o in d['objects'] if o['name']=='natural connecting rock apron']
assert len(aprons)==3
for o in aprons:
 x,y,z=o['origin'];w,h,dz=o['size']
 assert 1<x and x+w<127 and 1<y and y+h<113
 assert x+w<42.8 or x>59.2
 assert z+dz<39.5
 assert not any(overlaps((x,y,w,h),r) for f in layout.FLOORS if f['z']<=26 for r in f['rects'])
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
# Keep the exact display base and all solid architecture/rock within its footprint.
# Natural leaves and thin woody twigs may overhang by at most one stud.
base_object=next(o for o in d['objects'] if o['name']=='base')
assert base_object['origin']==[0,0,-1] and base_object['size']==[128,114,1]
soft_colors={'foliage_dark','foliage_mid','foliage_light','rose','rose_light','cream_flower','flower_gold','timber'}
hard_points=np.concatenate([np.array(t) for color,t in build.g.triangles if color not in soft_colors])
assert hard_points[:,0].min()>=0 and hard_points[:,0].max()<=128
assert hard_points[:,2].min()>=0 and hard_points[:,2].max()<=114
assert lo[0]>=-1 and hi[0]<=129 and lo[2]>=-1 and hi[2]<=115
foliage_overhang={'west_studs':max(0,float(-lo[0])),'east_studs':max(0,float(hi[0]-128)),
                 'north_studs':max(0,float(-lo[2])),'south_studs':max(0,float(hi[2]-114))} 
nav=check_layout.run()
assert sum(o['name']=='garden pool olive tree' for o in d['objects'])==2
assert all(z+h<57 for x,y,z,h,r in garden_pool.OLIVES)
assert sum(o['name']=='garden pool tiered fountain' for o in d['objects'])==1
assert sum(o['name']=='garden pool lavender clump' for o in d['objects'])>=15
awning=next(o for o in d['objects'] if o['name']=='garden pool service-side awning')
assert awning['origin'][0]>=89 and awning['origin'][2]>=46.7
assert awning['origin'][0]+awning['size'][0]<96
assert next(o for o in d['objects'] if o['name']=='garden pool ripple surface')['rect']==list(layout.PROGRAM['pool'])
views={}
for view,stem in [('concept','blockout'),('front','blockout'),('plan','blockout'),('rear','blockout'),('pool','blockout'),('garden','blockout'),('dusk','blockout'),('cottage','blockout')]:
 im=HERE/f'{stem}-{view}.png';meta=json.loads(im.with_suffix('.render.json').read_text())
 for key,p in [('model_sha256',HERE/f'{stem}.ldr'),('render_sha256',im),
               ('generator_sha256',HERE/'build.py'),('renderer_sha256',HERE/'render.py'),
               ('layout_sha256',HERE/'layout.py'),('geometry_sha256',HERE/'geometry.py'),('exterior_sha256',HERE/'exterior.py'),('annex_exterior_sha256',HERE/'annex_exterior.py'),('atmosphere_sha256',HERE/'atmosphere.py'),('garden_pool_sha256',HERE/'garden_pool.py'),('natural_sha256',HERE/'natural.py')]:
  assert meta[key]==sha(p),(view,key)
 assert meta['luminous_triangles']>0
 assert 'emitting lantern surfaces' in meta['lighting']
 with Image.open(im) as image:image.verify()
 views[view]='current'
plans=json.loads((HERE/'plans-provenance.json').read_text())
assert plans['layout_sha256']==sha(HERE/'layout.py')
assert plans['atmosphere_sha256']==sha(HERE/'atmosphere.py')
assert plans['garden_pool_sha256']==sha(HERE/'garden_pool.py')
assert plans['natural_sha256']==sha(HERE/'natural.py')
assert plans['plans_generator_sha256']==sha(HERE/'plans.py')
for name,value in plans['drawings'].items():assert sha(HERE/name)==value
reference=HERE/'reference-concept.png'
assert sha(reference)==sha(HERE.parent/'reference-concept.png')
assert sha(reference)=='ebf1e0ac0c13cfb5e602b7fb6c23d5bb9a1ec7ca9aa90efc63d8b459a9074e6a'
out=dict(reference_sha256=sha(reference),foliage_overhang=foliage_overhang,hardscape_within_base=True,scope='reference-led natural cliff, rooted asymmetric creepers and distributed pots over approved hotel layout',deterministic_export=True,
 added_potted_accents=21,irregular_fractured_rock=True,asymmetric_rooted_creepers=True,plant_footprints_checked=True,
 approved_v6_layout_unchanged=True,baseline_architecture_objects_and_cliff_envelopes_preserved=True,
 new_site_items_in_plan_and_circulation=True,olive_trees_and_lavender=True,olive_canopies_below_upper_window_sill=True,
 fountain_and_pool_ripple_surface=True,service_side_shade_clear_of_pool_loop=True,lantern_surfaces_emit_light=True,
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
