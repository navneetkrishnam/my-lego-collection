"""Record local ownership and element-membership evidence; never infer quantities."""
import csv,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
owned={r['set_number']:int(r['quantity_owned']) for r in csv.DictReader((ROOT/'data/owned-sets.csv').open())}
catalog={s['id']:s for s in json.loads((ROOT/'public/data/sets.json').read_text())}
choices=[
 ('42655','Primary restaurant donor',['6245261','6404592','6361354','6235083'],['0.png','2.png','3.png'],
  'Adapt the visible dining chairs/tables and kitchen counter arrangement; tableware and tap are locally listed.'),
 ('42691','Supplementary restaurant / spa fittings',['6245261','6146054','4560180','6174229'],['0.png'],
  'Use dining/garden details as inspiration; tap and flat-tile elements are spa candidates. No intact module fit is claimed.'),
 ('42662','Primary salon donor',['6489198','6058368','4243668','6146054','6313992'],['0.png','3.png'],
  'Rebuild the visible mirror/styling-chair/counter setup inside the hotel envelope; reserve a separate wash station.'),
 ('41743','Supplementary salon donor',['6096993','4243668','6146054'],['0.png','2.png'],
  'Candidate second styling station and accessories; recolor surrounding built furniture to suit the hotel.'),
 ('10362','Library and spa finishing candidates',['6174229','6523320','6164288'],[],
  'Locally listed book elements for the library; flat tiles can finish custom spa furniture. Quantities unknown.')]
rows=[]
for sid,role,ids,photos,note in choices:
 assert owned.get(sid,0)>0
 path=ROOT/'public/data/parts'/f'{sid}.json'
 parts={p['id']:p for p in json.loads(path.read_text())}
 assert all(i in parts for i in ids)
 rows.append(dict(set_id=sid,name=catalog[sid]['name'],owned_copies=owned[sid],role=role,
  reuse_note=note,parts_source=str(path.relative_to(ROOT)),parts_source_sha256=sha(path),
  elements=[dict(element_id=i,name=parts[i]['name'],quantity_in_set=None) for i in ids],
  inspected_images=[dict(path=f'public/images/{sid}/{n}',sha256=sha(ROOT/f'public/images/{sid}/{n}')) for n in photos]))
out=dict(scope='Candidate donors; ownership and element membership only. Not an allocation or bill of materials.',
 sources={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'data/owned-sets.csv',ROOT/'public/data/sets.json']},
 donors=rows,exact_quantities_known=False,intact_module_fit_verified=False,inventory_reserved=False)
(HERE/'donor-candidates.json').write_text(json.dumps(out,indent=2)+'\n')
print('Recorded',len(rows),'owned donor sets; no quantity inference or stock reservation')
