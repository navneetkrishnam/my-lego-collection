"""Author and export Fern & Steam. Python stdlib only; no tracker mutations.

Run once with --refresh-inventory to capture current source files. Subsequent
runs deliberately use the frozen snapshot. Coordinates: x left to right,
y back to front, z upward in plate heights, measured at the part's bottom.
"""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
from verify import conservative_inventory, check_model

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

# Short side is local LDraw X; long side is local Z for rectangular parts.
# Element identity/color are matched to the existing exact-ID source records.
# Geometry sources: https://library.ldraw.org/library/official/parts/<file>
PARTS = {}
def define(element, name, color, code, rgb, file, w, d, h=1, kind='box', studded=True):
    PARTS[element] = dict(element=element, name=name, color=color, ldraw_color=code,
        rgb=rgb, ldraw=file, w=w, d=d, h=h, kind=kind, studded=studded,
        geometry_source=f'https://library.ldraw.org/library/official/parts/{file}')

define('303526','Plate 4 x 8','Black',0,'#242728','3035.dat',4,8)
define('4509897','Plate 4 x 8','Tan',19,'#DEC69C','3035.dat',4,8)
define('4243824','Plate 4 x 4','Tan',19,'#DEC69C','3031.dat',4,4)
define('4114309','Plate 2 x 4','Tan',19,'#DEC69C','3020.dat',2,4)
define('4211414','Tile 1 x 2','Light bluish grey',71,'#A0A5A9','3069b.dat',1,2,studded=False)
define('300501','Brick 1 x 1','White',15,'#F4F4F4','3005.dat',1,1,3)
define('300401','Brick 1 x 2','White',15,'#F4F4F4','3004.dat',1,2,3)
define('301001','Brick 1 x 4','White',15,'#F4F4F4','3010.dat',1,4,3)
define('4211247','Plate 2 x 6','Reddish brown',70,'#582A12','3795.dat',2,6)
define('4221590','Plate 1 x 6','Reddish brown',70,'#582A12','3666.dat',1,6)
define('4216945','Plate 1 x 8','Reddish brown',70,'#582A12','3460.dat',1,8)
define('306901','Tile 1 x 2','White',15,'#F4F4F4','3069b.dat',1,2,studded=False)
define('4211388','Brick 1 x 2','Light bluish grey',71,'#A0A5A9','3004.dat',1,2,3)
define('4211186','Plate 2 x 4','Reddish brown',70,'#582A12','3020.dat',2,4)
define('4211225','Brick 1 x 4','Reddish brown',70,'#582A12','3010.dat',1,4,3)
define('4211151','Tile 1 x 2','Reddish brown',70,'#582A12','3069b.dat',1,2,studded=False)
define('4211194','Tile 1 x 4','Reddish brown',70,'#582A12','2431.dat',1,4,studded=False)
define('300301','Brick 2 x 2','White',15,'#F4F4F4','3003.dat',2,2,3)
define('4216695','Plate 2 x 2','Reddish brown',70,'#582A12','3022.dat',2,2)
define('4211210','Brick 2 x 2','Reddish brown',70,'#582A12','3003.dat',2,2,3)
define('302228','Plate 2 x 2','Green',2,'#237841','3022.dat',2,2)
define('6182261','Plant with three leaves','Bright green',10,'#4B9F4A','32607.dat',1,1,3/8,'leaf')
define('6212501','Flower with five petals','Bright pink',29,'#E4ADC8','24866.dat',1,1,2/8,'flower')
define('6295242','Flower with five petals','Coral',353,'#FF6D77','24866.dat',1,1,2/8,'flower')
define('389924','Mug','Yellow',14,'#F2CD37','3899.dat',1,1,18/8,'mug',False)

STEPS = [
    ('Lay out the foundation', 'On a flat surface, lay the eight black plates edge to edge. They are loose until the next step; do not lift them yet.'),
    ('Lock the base together', 'Press the tan layer onto the black layer. The offset seams join the foundation into a single assembly. Finish all 15 tan plates before lifting.'),
    ('Lay the courtyard path', 'Lay the light grey tiles in a stepped path from the front entrance toward the tea counter. Keep the marked areas studded for furniture and plants.'),
    ('Raise the kiosk, course 1', 'Add the four white corner posts, low back/side walls and the first course of the tea counter. The open side faces the path.'),
    ('Raise the kiosk, course 2', 'Repeat the post and wall positions one brick higher; complete the second and final course of the tea counter.'),
    ('Finish the wall and counter', 'Raise the posts and back/side walls one more course. Add the brown counter plate, the narrow back shelf, and the white counter trim.'),
    ('Make the courtyard bench', 'Add two grey supports, the brown seat plate, the front seat tiles and the upright backrest. The bench faces the front edge.'),
    ('Add table and planters', 'Add the small white table pedestal with brown top, then three brown planters capped with green plates.'),
    ('Plant the garden and serve tea', 'Attach the leaves and flowers at the marked studs. BOTH mug handles point REARWARD: the counter mug clears the white trim, and the table mug clears its neighboring stud.'),
    ('Raise the pergola posts', 'Add two more white bricks to each of the four posts. Complete all four posts to the same height.'),
    ('Fit the pergola beams', 'Fit the two brown 1 x 8 plates left-to-right across the front and rear pairs of posts. Support the posts while pressing the beam ends.'),
    ('Fit the five roof slats', 'Lay five brown 1 x 6 plates front-to-back across both beams. Keep the intentional gaps between slats. Review the completed model before lifting it by its base.'),
]

def author():
    pieces = []
    def add(e, x, y, z, step, turn=False):
        p = dict(PARTS[e])
        if turn:
            p['w'], p['d'] = p['d'], p['w']
        p.update(key=f'P{len(pieces)+1:03}', x=x, y=y, z=z, step=step, turn=turn, rotation=90 if turn else 0)
        pieces.append(p)
    # Two fully covered base layers with offset seams, including the central z seam.
    for y in (0,8):
        for x in (0,4,8,12): add('303526',x,y,0,1)
    for x in (2,10):
        for y in (0,8): add('4509897',x,y,1,2)
    add('4243824',6,0,1,2)
    add('4509897',6,4,1,2)
    add('4243824',6,12,1,2)
    for x in (0,14):
        for y in (0,4,8,12): add('4114309',x,y,1,2)
    # Nine paving tiles; identical elements remain individually identified.
    for x,y in [(8,14),(8,12),(7,10),(6,8)]:
        add('4211414',x,y,2,3,True)
        add('4211414',x,y+1,2,3,True)
    add('4211414',5,7,2,3,True)
    # White kiosk with four five-brick posts. Walls stop at three bricks high.
    for course in range(3):
        z=2+3*course; step=4+course
        for x,y in [(1,2),(8,2),(1,7),(8,7)]: add('300501',x,y,z,step)
        add('301001',2,2,z,step,True)
        add('300401',6,2,z,step,True)
        add('301001',1,3,z,step)
        if course < 2:
            for y in (5,6):
                for x in (2,4,6): add('300401',x,y,z,step,True)
    add('4211247',2,5,8,6,True)
    add('4221590',2,2,11,6,True)
    for x in (2,4,6): add('306901',x,6,9,6,True)
    # Bench: the front row is tiled, the rear row retains the backrest.
    for x in (11,14): add('4211388',x,7,2,7)
    add('4211186',11,7,5,7,True)
    for x in (11,13): add('4211151',x,8,6,7,True)
    add('4211225',11,7,6,7,True)
    add('4211194',11,7,9,7,True)
    add('300301',11,11,2,8)
    add('4216695',11,11,5,8)
    pots = [(11,2),(14,3),(2,11)]
    for x,y in pots:
        add('4211210',x,y,2,8)
        add('302228',x,y,5,8)
    plants = [(11,2,6),(14,3,6),(2,11,6),(5,12,2),(2,14,2),(14,14,2),(14,10,2)]
    for index,(x,y,z) in enumerate(plants):
        add('6182261',x,y,z,9)
        if index < 6:
            add('6212501' if index%2==0 else '6295242',x,y,z+3/8,9)
    add('389924',3,5,9,9)
    pieces[-1]['rotation']=180
    add('389924',11,11,6,9)
    pieces[-1]['rotation']=180
    for course in range(3,5):
        for x,y in [(1,2),(8,2),(1,7),(8,7)]: add('300501',x,y,2+3*course,10)
    for y in (2,7): add('4216945',1,y,17,11,True)
    for x in (1,3,5,7,8): add('4221590',x,2,18,12)
    return pieces

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

def capture():
    own_path=ROOT/'data/owned-sets.csv'
    owned={row['set_number']:int(row['quantity_owned']) for row in csv.DictReader(own_path.open())}
    paths={s:ROOT/f'public/data/parts/{s}.json' for s in owned}
    raw={s:json.loads(p.read_text()) for s,p in paths.items()}
    inv, invalid=conservative_inventory(owned,raw)
    catalog_path=ROOT/'public/data/sets.json'
    cache_path=ROOT/'public/data/parts-enrichment-cache.json'
    catalog={str(s['id']):s['name'] for s in json.loads(catalog_path.read_text())}
    cache=json.loads(cache_path.read_text())
    for element in PARTS:
        if element not in inv:
            raise ValueError(f'No inventory for {element}')
        records=[p for rows in raw.values() for p in rows if str(p.get('id'))==element]
        inv[element]['source_names']=sorted({p['name'] for p in records})
        inv[element]['color_metadata']=cache.get(element,{}).get('colorName')
        inv[element]['image_url']=records[0]['imageUrl']
        for source in inv[element]['sources']:
            source['name']=catalog[source['set']]
    hashes={str(p.relative_to(ROOT)):digest(p) for p in [own_path,catalog_path,cache_path,*paths.values()]}
    snap={'rule':'one exact ID per owned set copy; duplicate rows deduplicated',
          'assumptions':['All owned sets are complete and accessible.','No pieces are already reserved.','Source membership and enrichment metadata are correct.'],
          'excluded_rows_without_id':invalid,'owned_sets':owned,'input_sha256':hashes,
          'elements':{e:inv[e] for e in sorted(PARTS)}}
    write_json(HERE/'inventory-snapshot.json',snap)
    return snap

def allocate(bom):
    remaining={p['element']:p['required'] for p in bom}
    source_map={}
    for p in bom:
        for src in p['sources']:
            key=(src['set'],src['copy'])
            source_map.setdefault(key,{'name':src['name'],'elements':set()})['elements'].add(p['element'])
    picks=[]
    while any(remaining.values()):
        options=[]
        for key,src in source_map.items():
            useful=sorted(e for e in src['elements'] if remaining[e]>0)
            if useful: options.append((-len(useful),key,useful))
        if not options: raise ValueError('Allocation cannot satisfy the BOM')
        _,key,useful=min(options)
        src=source_map.pop(key)
        picks.append(dict(set=key[0],copy=key[1],name=src['name'],elements=useful))
        for e in useful: remaining[e]-=1
    return picks

def ldraw(pieces):
    lines=['0 Fern & Steam - garden tea kiosk, revision 1','0 Name: fern-and-steam.ldr',
           '0 Author: Navneet / Codex','0 // Inventory-checked prototype; physical build pending.',
           '0 // Origin: rear-left outer corner; X right, Z front, Y up is negative.']
    step=0
    for p in pieces:
        if step!=p['step']:
            if step: lines.append('0 STEP')
            step=p['step'];lines.append(f'0 // Step {step}: {STEPS[step-1][0]}')
        # LDraw origins are at the top body plane. Leaf=3 LDU, flower=2, mug=18.
        x=(p['x']+p['w']/2)*20; y=-(p['z']+p['h'])*8; z=(p['y']+p['d']/2)*20
        matrix={0:'1 0 0 0 1 0 0 0 1',90:'0 0 1 0 1 0 -1 0 0',
                180:'-1 0 0 0 1 0 0 0 -1'}[p['rotation']]
        lines.append(f"0 // {p['key']} LEGO element {p['element']}")
        lines.append(f"1 {p['ldraw_color']} {x:g} {y:g} {z:g} {matrix} {p['ldraw']}")
    lines.append('0 STEP')
    return '\n'.join(lines)+'\n'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--refresh-inventory',action='store_true')
    args=parser.parse_args()
    snap=capture() if args.refresh_inventory else json.loads((HERE/'inventory-snapshot.json').read_text())
    pieces=author()
    result=check_model(pieces,snap['elements'],(16,16))
    write_json(HERE/'model.json',dict(name='Fern & Steam',revision=1,footprint=[16,16],
        coordinate_units='x/y studs from rear-left outer corner; z plate heights from bottom',
        steps=[dict(number=i+1,title=t,description=d) for i,(t,d) in enumerate(STEPS)],pieces=pieces))
    write_json(HERE/'part-map.json',PARTS)
    (HERE/'fern-and-steam.ldr').write_text(ldraw(pieces))
    counts=Counter(p['element'] for p in pieces)
    bom=[]
    for e,n in sorted(counts.items()):
        row=dict(PARTS[e],required=n,minimum=snap['elements'][e]['minimum'],
            sources=snap['elements'][e]['sources'],image_url=snap['elements'][e]['image_url'])
        bom.append(row)
    write_json(HERE/'bom.json',bom)
    picks=allocate(bom) if result['inventory_pass'] else []
    write_json(HERE/'allocation.json',picks)
    result.update(piece_count=len(pieces),unique_elements=len(counts),steps=len(STEPS),
        donor_set_copies=len(picks),physical_build='NOT_TESTED',fine_mesh_collision='NOT_TESTED',
        clutch_and_stability='NOT_TESTED',element_mapping='MANUALLY_SELECTED_NOT_PHYSICALLY_CONFIRMED',
        geometry_scope='Axis-aligned structural bodies; integer stud overlap and prior support. Decorative bodies use mounting abstractions, not fine meshes.',
        reproducibility='Frozen input snapshot; stable ordering; deterministic allocation; no generation timestamps.',
        hashes={f:digest(HERE/f) for f in ['model.json','part-map.json','fern-and-steam.ldr','bom.json','inventory-snapshot.json','allocation.json','model.py','verify.py']})
    write_json(HERE/'verification.json',result)
    lines=['# Fern & Steam / conservative picking list','',f'{len(pieces)} pieces; {len(counts)} exact element IDs; {len(picks)} donor set copies in this deterministic allocation.','',
           'Take exactly ONE of each listed element from each listed set copy. This deliberately uses only the recorded minimum, and does not prove these are the fewest possible donor sets. If you find extra copies, record them before revising the allocation.','',
           '| Element ID | Part | Color | Required | Conservative minimum |','|---|---|---|---:|---:|']
    for b in bom:lines.append(f"| {b['element']} | {b['name']} | {b['color']} | {b['required']} | {b['minimum']} |")
    lines+=['','## Pick by donor set','']
    for p in picks:lines += [f"### {p['set']} / copy {p['copy']} / {p['name']}",'',', '.join(p['elements']),'']
    (HERE/'picking-list.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='hashes'},indent=2))
    if not(result['inventory_pass'] and result['structural_pass']): raise SystemExit(1)

if __name__=='__main__':main()
