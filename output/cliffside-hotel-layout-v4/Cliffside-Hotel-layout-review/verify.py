"""Verify the room-programmed proxy and its delivered artifact provenance."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
import build,layout,check_layout
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={n:sha(HERE/n) for n in ('blockout.ldr','layout.json')}
build.export()
assert before=={n:sha(HERE/n) for n in before},'Export changed on regeneration'
d=json.loads((HERE/'layout.json').read_text())
assert d['model_sha256']==sha(HERE/'blockout.ldr')
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
# Requested revision: a larger cottage, public library and daylight to the corridor.
cottage=next(f for f in layout.FLOORS if f['id']=='cottage')
assert cottage['rects']==[(82,8,32,28)]
assert sum(w*d for x,y,w,d in cottage['rects'])==896
assert any(s['name']=='Lounge / library' and s['kind']=='lounge' for s in cottage['spaces'])
assert not any('library' in s['name'].lower() for f in layout.FLOORS if f['id'].startswith('main') for s in f['spaces'])
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
 assert not(min(x+w,88)>max(x,66) and min(y+h,76)>max(y,64))
beams=[o for o in build.g.objects if o['name']=='balcony support envelope']
assert len(beams)==15
assert all(o['size'][1]==6 and o['size'][2]==.5 for o in beams)
points=np.concatenate([np.array(t) for c,t in build.g.triangles])
assert np.isfinite(points).all()
lo,hi=points.min(0),points.max(0)
assert np.allclose([hi[0]-lo[0],hi[2]-lo[2]],layout.BASE)
nav=check_layout.run()
views={}
for view in ('concept','front','plan','rear'):
 im=HERE/f'blockout-{view}.png';meta=json.loads(im.with_suffix('.render.json').read_text())
 for key,p in [('model_sha256',HERE/'blockout.ldr'),('render_sha256',im),
               ('generator_sha256',HERE/'build.py'),('renderer_sha256',HERE/'render.py'),
               ('layout_sha256',HERE/'layout.py'),('geometry_sha256',HERE/'geometry.py')]:
  assert meta[key]==sha(p),(view,key)
 with Image.open(im) as image:image.verify()
 views[view]='current'
plans=json.loads((HERE/'plans-provenance.json').read_text())
assert plans['layout_sha256']==sha(HERE/'layout.py')
for name,value in plans['drawings'].items():assert sha(HERE/name)==value
out=dict(scope='room-programmed architectural proxy',deterministic_export=True,
 room_program_pass=True,cottage_enlargement_and_library_pass=True,pool_facing_corridor_windows_pass=True,
 furniture_envelopes_nonoverlapping=True,cottage_roof_separation_pass=True,donor_evidence_current=True,
 straight_exterior_stair_pass=True,pool_support_envelopes_pass=True,
 balcony_support_envelopes_pass=True,declared_floor_shafts_pass=True,
 circulation_destinations=f"{nav['connected_targets']}/{nav['total_targets']}",
 public_routes_avoid_private_rooms=True,public_library_access_without_bedroom=True,pool_walking_loop_clear=True,
 model_sha256=d['model_sha256'],render_provenance=views,plan_provenance=True,
 lego_connections_verified=False,structural_analysis_performed=False,physical_assembly_tested=False)
(HERE/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
