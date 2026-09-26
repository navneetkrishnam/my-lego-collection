"""Check the requested massing corrections, not LEGO connections."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image
import build

HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={name:sha(HERE/name) for name in ('blockout.ldr','dimensions.json')}
build.export()
assert before=={name:sha(HERE/name) for name in before},'Nondeterministic export'
d=json.loads((HERE/'dimensions.json').read_text())
assert d['model_sha256']==sha(HERE/'blockout.ldr')
points=np.concatenate([np.array(t) for color,t in build.triangles])
lo,hi=points.min(0),points.max(0)
assert np.isfinite(points).all()
assert np.allclose([hi[0]-lo[0],hi[2]-lo[2]],d['base_studs'])
assert abs(hi[1]-lo[1]-d['maximum_height_studs'])<1e-8

def named(name):
    return [o for o in build.objects if o['name']==name]

floors=[named('main villa rear bar floor')[0],named('main villa forward return floor')[0]]
def in_villa(x,y):
    return any(o['origin'][0]<x<o['origin'][0]+o['size'][0] and
               o['origin'][1]<y<o['origin'][1]+o['size'][1] for o in floors)
assert in_villa(50,20) and in_villa(30,40) and not in_villa(50,40)
assert len(named('joined L roof'))==1
for o in build.objects:
    if o['name'].startswith(('side garden planter','side garden planting','side garden pergola')):
        assert o['origin'][0]+o['size'][0] <= 22
floor_names=['descending wing lower floor floor','arcade floor','descending wing upper floor floor']
assert [named(n)[0]['origin'][2] for n in floor_names]==[12,26,40]
assert [v<d['main_courtyard_level_studs'] for v in d['right_wing_floor_levels_studs']]==[True,True,False]
# No high terrain slab may occupy the descending wing's floor volume.
for o in build.objects:
    if o['color'] not in ('rock','rock2'):
        continue
    x,y,z=o['origin'];w,depth,h=o['size']
    overlaps=(min(x+w,118)>max(x,90) and min(y+depth,66)>max(y,40))
    assert not overlaps or z+h<=12+1e-8,(o['name'],'terrain obscures the lower floor')
views={}
for view in ('concept','front','rear','plan'):
    img=HERE/f'blockout-{view}.png'
    meta=json.loads(img.with_suffix('.render.json').read_text())
    for key,p in [('model_sha256',HERE/'blockout.ldr'),('render_sha256',img),
                  ('generator_sha256',HERE/'build.py'),('renderer_sha256',HERE/'render.py')]:
        assert meta[key]==sha(p),(view,key)
    with Image.open(img) as im:
        im.verify()
    views[view]='current hashes and readable image'
result={'scope':'architectural proxy only','deterministic_export':True,
        'finite_nondegenerate_geometry':True,'dimensions_match':True,
        'main_villa_has_L_footprint':True,'garden_and_pergola_beside_villa':True,
        'two_right_wing_floor_levels_below_courtyard':True,
        'no_high_terrain_inside_descending_wing':True,
        'model_sha256':d['model_sha256'],'views':views,
        'lego_parts_verified':False,'physical_assembly_tested':False}
(HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
