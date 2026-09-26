"""Deterministic, exact-element authoring of the Courtyard Edition.

Requires the installed Studio catalog only when refreshing the snapshot.
Positions are lower-left body bounds, in studs, with z in plate heights.
LDraw exports preserve actual canonical part geometry and explicit inserts.
"""
from collections import Counter
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STUDIO = Path('/Applications/Studio 2.0')
SPECS = {}


def group(ids, w, d, h=1, kind='box', studded=True, native='z'):
    for e in ids.split():
        SPECS[e] = dict(w=w, d=d, h=h, kind=kind, studded=studded, native=native)


group('303626 4210794', 6, 8)
group('303401 4113988 4211406 303426 4210997', 2, 8)
group('302001 4114309 4211395 4211186 302026', 2, 4)
group('379501 4113993 379526 4211247', 2, 6)
group('371001 4113233 371026 4211190', 1, 4)
group('366601 4124067 366626 4221590', 1, 6)
group('302326', 1, 2)
group('300501 4113915', 1, 1, 3)
group('300401 4109995 4211149', 1, 2, 3)
group('301001 4113916 4211225 4245571', 1, 4, 3)
group('300901 4112982', 1, 6, 3)
group('300301 4211210', 2, 2, 3)
group('4211201', 2, 4, 3)
group('4211388', 1, 2, 3)
group('4211481 4544139', 1, 8, studded=False)
group('4211549 4157277 663626 663601 4211204', 1, 6, studded=False)
group('4211356 4550324 243126 243101 4211194', 1, 4, studded=False)
group('4211414 4114026 306901 4211151', 1, 2, studded=False)
group('4211415 4125253 307001', 1, 1, studded=False)
group('4211413 4185177 306801', 2, 2, studded=False)
group('4560183 6122047 4560178', 2, 4, studded=False)
group('4216695 302228', 2, 2)
group('6249033', 6, 1, 21, kind='arch', native='x')
group('6031057', 4, 1, 6, kind='small_arch', native='x')
group('6262945', 4, 1, 18, kind='frame', native='x')
group('4530590', 4, 1, 9, kind='frame', native='x')
group('6256127', 6, 1, 18, kind='frame', native='x')
group('6514119 6514142 6511024', 0, 0, 0, kind='insert', studded=False)
group('6503221', 6, 3, 6, kind='roof', native='x')
group('6182261 6229130 6400754', 1, 1, 1, kind='leaf')
group('6212501 6295242 6206149', 1, 1, 1, kind='flower', studded=False)
group('4211183', 1, 1, 3, kind='round')
group('4659665', 1, 1, 3, kind='mug', studded=False)
group('6447541', 1, 1, 1, kind='fern')

STEPS = [
    ('Foundation', 'Arrange the twelve 6 × 8 plates on a flat surface.'),
    ('Lock the foundation', 'Add the offset upper layer. Complete it before lifting the base.'),
    ('Paved courtyard', 'Fit the pale-grey exterior and tan interior tiles. Leave the marked studded attachment areas.'),
    ('Window sills and pillars', 'Build the low sills and tan entrance pillars.'),
    ('Lower glazing', 'Fit the lower side and rear frames with their matching panes.'),
    ('Upper glazing and entrance', 'Add the upper windows and the glazed entrance door. Insert panes before the cornice.'),
    ('Cafe counter', 'Build the counter inside the open serving arch, then add its white mug.'),
    ('Arched facade', 'Add both large arches, the small tan entrance arch, and the four outer-pillar fillers.'),
    ('Roof cornice', 'Tie the walls with two crossing plate layers. Keep the central glazed opening clear.'),
    ('Lantern support frame', 'Make the lantern rail subassembly: connect the three lower beams with the two eave rows before placing it on the cornice. Add the upper rails and shoulder trim.'),
    ('Glass roof', 'Fit the four fixed windscreens in opposing pairs; cap and tie their upper studs.'),
    ('Bench and bistro table', 'Build the timber bench and compact square table.'),
    ('Raised garden beds', 'Add the brown raised beds and brown mounting plates.'),
    ('Flowers and finishing', 'Attach leaves and flowers at the recorded studs; finish with the table mug.'),
]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture():
    own_file = ROOT / 'data/owned-sets.csv'
    owned = {r['set_number']: int(r['quantity_owned']) for r in csv.DictReader(own_file.open())}
    inventory = {}
    hashes = {str(own_file.relative_to(ROOT)): sha(own_file)}
    invalid = 0
    for s, copies in sorted(owned.items()):
        path = ROOT / f'public/data/parts/{s}.json'
        hashes[str(path.relative_to(ROOT))] = sha(path)
        seen = set()
        for row in json.loads(path.read_text()):
            e = row.get('id')
            if e is None or not str(e).strip():
                invalid += 1
                continue
            e = str(e)
            if e in seen:
                continue
            seen.add(e)
            r = inventory.setdefault(e, dict(minimum=0, name=row['name'], sources=[]))
            r['minimum'] += copies
            r['sources'].extend(dict(set=s, copy=i + 1) for i in range(copies))
    elements = {str(r['elementId']): r for r in json.loads((STUDIO / 'data/elementInfoList.json').read_text())}
    geometries = {}
    for row in csv.DictReader((STUDIO / 'data/StudioPartDefinition2.txt').open(), delimiter='\t'):
        if int(row['Studio ItemNo']) > 0 and row['LDraw ItemNo']:
            geometries.setdefault(row['BL ItemNo'], row['LDraw ItemNo'])
    colors = {}
    for row in csv.DictReader((STUDIO / 'data/StudioColorDefinition.txt').open(), delimiter='\t'):
        if row['BL Color Code'] and row['LDraw Color Code'] and int(row['LDraw Color Code']) >= 0:
            colors.setdefault(row['BL Color Code'], row)
    parts = {}
    for e, spec in SPECS.items():
        inv = inventory[e]
        elem = elements[e]
        color = colors[str(elem['blColorCode'])]
        file = geometries[str(elem['blItemNo'])]
        part_path = next((p for p in [STUDIO / 'ldraw/parts' / file, STUDIO / 'ldraw/UnOfficial/parts' / file] if p.exists()), None)
        if not part_path:
            raise ValueError(f'Missing geometry {e}: {file}')
        parts[e] = dict(spec, **inv, ldraw=file, bl_part=str(elem['blItemNo']),
                        ldraw_color=int(color['LDraw Color Code']), color=color['BL Color Name'],
                        geometry_sha256=sha(part_path), geometry_path=str(part_path))
    snapshot = dict(rule='One exact element ID per owned set copy; duplicate rows deduplicated.',
                    assumptions=['All donor sets are complete and accessible.', 'No pieces are reserved elsewhere.',
                                 'Cached set membership is correct; per-set quantities are unknown.'],
                    owned_sets=owned, excluded_rows_without_id=invalid, input_sha256=hashes, parts=parts)
    write_json(HERE / 'inventory-snapshot.json', snapshot)
    return snapshot


def rotation(degrees):
    c = round(math.cos(math.radians(degrees)), 10)
    s = round(math.sin(math.radians(degrees)), 10)
    return [c, 0, s, 0, 1, 0, -s, 0, c]


def transform(mat, point):
    return [sum(mat[3 * i + j] * point[j] for j in range(3)) for i in range(3)]


def author(snapshot):
    parts = snapshot['parts']
    pieces = []
    used = Counter()

    def add(e, x, y, z, step, turn=False, angle=None):
        s = parts[e]
        w, d = (s['d'], s['w']) if turn else (s['w'], s['d'])
        if angle is None:
            # Standard rectangular LDraw bricks/plates have their long axis X.
            # Authored regular specs use short-X/long-Y footprints.
            angle = (0 if turn else 90) if s['native']=='z' and s['w']<s['d'] else (90 if turn else 0)
        p = dict(key=f'P{len(pieces)+1:04}', element=e, x=x, y=y, z=z,
                 w=w, d=d, h=s['h'], kind=s['kind'], studded=s['studded'], step=step,
                 matrix=rotation(angle), origin=[20*(x+w/2), -8*(z+s['h']), 20*(y+d/2)])
        pieces.append(p)
        used[e] += 1
        return p

    def insert(frame, e, offset):
        delta = transform(frame['matrix'], offset)
        p = dict(key=f'P{len(pieces)+1:04}', element=e, kind='insert', step=frame['step'],
                 matrix=frame['matrix'], origin=[a+b for a,b in zip(frame['origin'], delta)],
                 parent=frame['key'], attachment='catalog-compatible frame insert', offset=offset)
        pieces.append(p)
        used[e] += 1
        return p

    # Foundation seams crossed by the orthogonal upper layer.
    for row, y in enumerate(range(0, 24, 8)):
        for col, x in enumerate(range(0, 24, 6)):
            add('303626' if (row+col)%2 == 0 else '4210794', x, y, 0, 1)
    for row, y in enumerate(range(0, 24, 2)):
        e = '303426' if row % 2 == 0 else '4210997'
        if row % 2 == 0:
            for x in (0, 8, 16): add('4210997' if row==10 and x==16 else e, x, y, 1, 2, True)
        else:
            for x in (4, 12): add(e, x, y, 1, 2, True)
            for x in (0, 20): add('302026', x, y, 1, 2, True)

    # Reserve base studs for walls and furniture. All remaining cells are tiled.
    reserved = set()
    def reserve(x, y, w, d):
        reserved.update((a,b) for a in range(x,x+w) for b in range(y,y+d))
    reserve(3, 4, 18, 1)
    reserve(3, 5, 1, 7); reserve(20, 5, 1, 7)
    reserve(3, 12, 18, 1)
    reserve(10, 11, 4, 1)  # recessed glazing behind middle arch
    reserve(16, 10, 4, 2)  # counter
    reserve(8, 16, 1, 2); reserve(13, 16, 1, 2)  # bench legs
    reserve(17, 18, 2, 2)  # table
    beds = [(1,15,2,4), (3,19,4,2), (20,16,2,4), (10,13,4,2), (1,6,2,4), (21,7,2,4)]
    for b in beds: reserve(*b)

    # Prefer long paving courses and larger interior tiles; deterministic scan.
    grey = ['4560183', '4211481', '4211549', '4211356', '4211413', '4211414', '4211415']
    tan = ['6122047', '4544139', '4157277', '4550324', '4185177', '4114026', '4125253']
    interior = {(x,y) for x in range(4,20) for y in range(5,12)} - reserved
    exterior = {(x,y) for x in range(24) for y in range(24)} - reserved - interior
    for region, candidates in [(exterior,grey), (interior,tan)]:
        while region:
            x,y = min(region, key=lambda p:(p[1],p[0]))
            placed = False
            for e in candidates:
                if used[e] >= parts[e]['minimum']: continue
                for turn in (True, False):
                    s=parts[e]; w,d=(s['d'],s['w']) if turn else (s['w'],s['d'])
                    cells={(a,b) for a in range(x,x+w) for b in range(y,y+d)}
                    if cells <= region:
                        add(e,x,y,2,3,turn); region -= cells; placed=True; break
                if placed: break
            if not placed: raise ValueError(f'No tile for {x,y}')

    # Narrow tan entrance piers. Door body height6bricks; ornamental arch2.
    for z in range(2,26,3):
        for x in (3,8): add('4113915',x,12,z,4)
    for x in (9,15): add('300901',x,12,2,4,True)
    for x in (3,20):
        for y in (4,8): add('301001',x,y,2,4)
    for x in (4,14): add('300901',x,4,2,4,True)
    add('301001',10,4,2,4,True)
    add('301001',10,11,2,4,True)

    def window(x,y,z,turn=False,wide=False,step=5):
        frame=add('6256127' if wide else '4530590',x,y,z,step,turn)
        insert(frame,'6511024' if wide else '6514142',[0,4.5,5] if wide else [0,8,4])
        return frame
    for x in (3,20):
        for y in (4,8):
            for z in (5,14): window(x,y,z,True,step=5 if z==5 else 6)
            add('301001',x,y,23,6)
    for x in (4,14):
        window(x,4,5,wide=True)
        add('300901',x,4,23,6,True)
    for y in (4,11):
        for z in (5,14): window(10,y,z,step=5 if z==5 else 6)
        add('301001',10,y,23,6,True)
    door=add('6262945',4,12,2,6)
    insert(door,'6514119',[-32,0,5])
    add('6031057',4,12,20,7)
    for x in (9,15):
        add('6249033',x,12,5,7)
        for xx in (x,x+5): add('300501',xx,12,23,7)

    # White first cornice layer follows walls; tan second layer crosses seams.
    for y in (4,12):
        for x in (3,9,15): add('366601',x,y,26,8,True)
    for x in (3,20):
        add('366601',x,5,26,8)
    # Full-width front and rear two-stud bands lock walls and side rails.
    for y in (3,11):
        for x in (3,9,15): add('379501',x,y,27,8,True)
    for x in (3,19):
        add('379501',x,5,27,8)
    # Fill opaque shoulders: 3 studs on either side of the 12-stud lantern.
    add('366601',3,5,28,9)
    add('379501',4,5,28,9)
    add('379501',18,5,28,9)
    add('366601',20,5,28,9)
    for y in (3,12):
        for x in (3,9,15): add('366601',x,y,28,9,True)
    for x in (3,18):
        # Complete the shoulder corners beside the black eave plates.
        for y in (4,11):
            add('302326',x,y,28,9,True)
    # Rail frame: eaves plus outer & central longitudinal support.
    for y in (4,10):
        for x in (6,12): add('379526',x,y,28,9,True)
    for x in (6,17): add('371026',x,6,28,9)
    for x in (6,11,16): add('379526',x,5,27,9)  # subassembly rails tied by eaves above
    for x in (11,12): add('371026',x,6,28,9)
    # Smooth opaque bands and white shoulders.
    for y in (3,4,11,12):
        for x in (3,9,15): add('663601',x,y,29,9,True)
    for x in (3,4,5,18,19,20): add('663601',x,5,29,9)

    # Four windscreens: body lower rim29, top35. Origins offset from bounds.
    for x in (6,12):
        p=add('6503221',x,5,29,10)
        p['origin']=[20*(x+3),-8*35,20*7.5]
        p=add('6503221',x,8,29,10,angle=180)
        p['origin']=[20*(x+3),-8*35,20*8.5]
    for x in (6,12): add('379526',x,7,35,10,True)
    for y in (7,8):
        for x in (6,10,14): add('371026',x,y,36,10,True)
        for x in (6,12): add('663626',x,y,37,10,True)

    # Counter accessible through right arch; brown worktop.
    for z in (2,5):
        for y in (10,11): add('4245571' if y==11 else '4211225',16,y,z,11,True)
    add('4211186',16,10,8,11,True)
    for x in (16,18): add('4211151',x,11,9,11,True)
    add('4659665',19,10,9,11,angle=180)
    # Bench seat and two-course back, with tiled arms/front seat strip.
    for x in (8,13): add('4211388',x,16,2,12)
    add('4211247',8,16,5,12,True)
    for x in (8,12): add('4211149',x,16,6,12,True)
    add('4211149',10,16,6,12,True)
    add('4211204',8,16,9,12,True)
    add('4211204',8,17,6,12,True)
    add('300301',17,18,2,12)
    add('4216695',17,18,5,12)
    # Table leaves studs available for the cup.
    add('4659665',18,19,6,14,angle=0)

    for i,(x,y,w,d) in enumerate(beds):
        height = 1
        if i==3:
            for b in (y,y+1): add('4211225',x,b,2,13,True)
        else:
            add('4211201',x,y,2,13,w==4)
        add('4211186',x,y,5,13,w==4)
        # Each leaf cluster keeps a two-stud spacing; a few stems vary height.
        for j,(a,b) in enumerate(( (a,b) for a in range(x,x+w,2) for b in range(y,y+d,2) )):
            base=3+3*height
            if i in (0,2,4,5):
                add('4211183',a,b,base,14); base += 3
            e=['6400754','6229130','6182261'][(i+j)%3]
            add(e,a,b,base,14,angle=0 if i%2==0 else 180)
            add(['6212501','6206149','6295242'][(i+j)%3],a,b,base+1,14)
            # Offset lower leaf, on a distinct stud, away from each upper cluster.
            if i in (0,2,4,5) and j==0:
                add('6447541',a+1,b+1,3+3*height,14,angle=0 if i%2==0 else 180)
            else:
                add('6229130',a+1,b+1,3+3*height,14,angle=180 if i%2==0 else 0)

    # Frozen, mesh-reviewed leaf arrangement. Every plant remains on a real
    # stud in its planter; the mapping must be revisited if instances change.
    layout=json.loads((HERE/'plant-layout.json').read_text())
    plants={p['key']:p for p in pieces if p['kind'] in ('leaf','flower','fern')}
    if set(layout)!=set(plants): raise ValueError('Plant layout does not match authored instances')
    for key, placement in layout.items():
        p=plants[key]
        p['origin'][0] += 20*(placement['x']-p['x'])
        p['origin'][2] += 20*(placement['y']-p['y'])
        p['x'],p['y']=placement['x'],placement['y']
        p['matrix']=rotation(placement['angle'])
    # Install the counter before enclosing the cafe, for unobstructed access.
    for p in pieces:
        if p['step']==11: p['step']=7
        elif 7<=p['step']<=10: p['step']+=1
    # Stable construction order, with frame inserts directly after their parent.
    pieces.sort(key=lambda p:p['step'])
    return pieces


def export(snapshot, pieces):
    counts=Counter(p['element'] for p in pieces)
    bom=[]
    allocations=[]
    for e,n in sorted(counts.items()):
        s=snapshot['parts'][e]
        bom.append(dict(element=e, name=s['name'], color=s['color'], ldraw=s['ldraw'],
                        required=n, conservative_available=s['minimum'], margin=s['minimum']-n))
        for i, donor in enumerate(s['sources'][:n]): allocations.append(dict(element=e, instance=i+1, **donor))
    write_json(HERE/'model.json',dict(title='Fern & Steam — Courtyard Edition', footprint=[24,24],
               coordinate_system='x/y studs from rear-left; z upward in plates; LDraw origin/matrix authoritative',
               steps=[dict(number=i+1,title=t,note=n) for i,(t,n) in enumerate(STEPS)], pieces=pieces))
    write_json(HERE/'bom.json',bom)
    write_json(HERE/'allocation.json',allocations)
    lines=['0 Fern & Steam - Courtyard Edition', '0 Name: fern-and-steam-v2.ldr',
           '0 Author: LEGO Tracker custom design', '0 Unofficial model; physical build not tested.']
    step=0
    for p in pieces:
        if p['step'] != step:
            if step: lines.append('0 STEP')
            step=p['step']; lines.append(f'0 Step {step}: {STEPS[step-1][0]}')
        s=snapshot['parts'][p['element']]
        lines.append(f"0 {p['key']} ELEMENT {p['element']}")
        numbers=' '.join(f'{v:g}' for v in p['origin']+p['matrix'])
        lines.append(f"1 {s['ldraw_color']} {numbers} {s['ldraw']}")
    (HERE/'fern-and-steam-v2.ldr').write_text('\n'.join(lines)+'\n')
    picking=['# Courtyard Edition picking list','',
             'Conservative allowance: one exact element per owned donor-set copy. Actual quantities may be higher.',
             'Assumes complete, accessible sets and no other reservations. Do not treat a set count as an audited loose-parts count.','',
             '| Element | Color | Part | Required | Conservative available |', '|---|---|---|---:|---:|']
    for b in bom: picking.append(f"| {b['element']} | {b['color']} | {b['name']} | {b['required']} | {b['conservative_available']} |")
    picking.extend(['','## Donor allocation','', 'Each listing below takes exactly one copy of the element from that donor box.',''])
    donors={}
    for a in allocations: donors.setdefault((a['set'],a['copy']),[]).append(a['element'])
    for (s,c), es in sorted(donors.items()): picking.append(f"- Set {s}, copy {c}: "+', '.join(es))
    (HERE/'picking-list.md').write_text('\n'.join(picking)+'\n')
    shortages={b['element']:-b['margin'] for b in bom if b['margin']<0}
    print(json.dumps(dict(pieces=len(pieces),exact_elements=len(counts),donor_boxes=len(donors),shortages=shortages),indent=2))
    return shortages


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--refresh-inventory',action='store_true')
    args=parser.parse_args()
    snap=capture() if args.refresh_inventory else json.loads((HERE/'inventory-snapshot.json').read_text())
    if export(snap,author(snap)): raise SystemExit('Inventory shortages must be resolved.')
