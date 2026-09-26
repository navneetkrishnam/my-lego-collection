"""Exact-element inventory and canonical geometry catalog for the hotel."""
from collections import defaultdict
import csv,json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
STUDIO=Path('/Applications/Studio 2.0')

REGULAR={}
def family(kind,h,entries):
 for code,w,d in entries:REGULAR[str(code)]=dict(kind=kind,w=w,d=d,h=h,studded=kind!='tile')
family('plate',1,[(3024,1,1),(3023,2,1),(3623,3,1),(3710,4,1),(3666,6,1),(3460,8,1),(4477,10,1),(60479,12,1),(3022,2,2),(3021,3,2),(3020,4,2),(3795,6,2),(3034,8,2),(3832,10,2),(2445,12,2),(4282,16,2),(3031,4,4),(3032,6,4),(3035,8,4),(3030,10,4),(3029,12,4),(3958,6,6),(3036,8,6),(3033,10,6),(3028,12,6),(3456,14,6),(41539,8,8),(92438,16,8),(91405,16,16)])
family('brick',3,[(3005,1,1),(3004,2,1),(3622,3,1),(3010,4,1),(3009,6,1),(3008,8,1),(6111,10,1),(6112,12,1),(2465,16,1),(3003,2,2),(3002,3,2),(3001,4,2),(2456,6,2),(3007,8,2)])
family('tile',1,[(3070,1,1),(3069,2,1),(63864,3,1),(2431,4,1),(6636,6,1),(4162,8,1),(3068,2,2),(87079,4,2)])
family('brick',9,[(14716,1,1)])
family('brick',15,[('2453a',1,1),('2453b',1,1),(2454,2,1)])
# Canonical frames/panels run across local X, standard positive Y downward.
for code,w,h in [('60596',4,18),('60594',4,9),('42205',6,18),('60592',2,6),('60593',2,9)]:REGULAR[code]=dict(kind='frame',w=w,d=1,h=h,studded=True)
for code,w,h in [('60581',4,9),('59349',6,15),('87544',2,9),('4865b',2,3),('30413',4,3)]:REGULAR[code]=dict(kind='panel',w=w,d=1,h=h,studded=True)
SPECIAL={'40066':dict(kind='arch',w=6,d=1,h=21,studded=True),'6182':dict(kind='arch_small',w=4,d=1,h=6,studded=True),'3062':dict(kind='round',w=1,d=1,h=3,studded=True),'32607':dict(kind='leaf',w=1,d=1,h=1,studded=True),'24866':dict(kind='flower',w=1,d=1,h=1,studded=False),'2682':dict(kind='fern',w=1,d=1,h=1,studded=True),'3899':dict(kind='mug',w=1,d=1,h=3,studded=False),'60616':dict(kind='insert',w=0,d=0,h=0,studded=False),'60603':dict(kind='insert',w=0,d=0,h=0,studded=False),'42509':dict(kind='insert',w=0,d=0,h=0,studded=False)}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,data):p.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
for code,w,d in [('3039',2,2),('3040',1,2),('3037',4,2)]:
 SPECIAL[code]=dict(kind='slope',w=w,d=d,h=3,studded=True,origin_offset=[0,0,10])
for code in ['48336','60470b']:
 SPECIAL[code]=dict(kind='hinge',w=2,d=1,h=1,studded=True)
SPECIAL['15332']=dict(kind='fence',w=4,d=1,h=6,studded=True)
SPECIAL['87087']=dict(kind='side_stud_brick',w=1,d=1,h=3,studded=True)
def apply_verified(inventory,owned,rows):
 for r in rows:
  if r['set'] not in owned or not isinstance(r['quantity'],int) or r['quantity']<=0:raise ValueError('Invalid verified donor or quantity')
  target=inventory[r['element']]
  for copy in range(1,owned[r['set']]+1):
   src=next((s for s in target['sources'] if s['set']==r['set'] and s['copy']==copy),None)
   if src is None:
    src=dict(set=r['set'],copy=copy,quantity=0);target['sources'].append(src)
   target['minimum']+=r['quantity']-src['quantity'];src['quantity']=r['quantity'];src['rule']='verified instruction inventory';src['printed_page']=r['printed_page']
def capture():
 source=ROOT/'data/owned-sets.csv';owned={r['set_number']:int(r['quantity_owned']) for r in csv.DictReader(source.open())};inventory={};hashes={str(source.relative_to(ROOT)):sha(source)};invalid=0
 for s,n in sorted(owned.items()):
  p=ROOT/f'public/data/parts/{s}.json';hashes[str(p.relative_to(ROOT))]=sha(p);seen=set()
  for row in json.loads(p.read_text()):
   if row.get('id') is None or not str(row['id']).strip():invalid+=1;continue
   e=str(row['id'])
   if e in seen:continue
   seen.add(e);r=inventory.setdefault(e,dict(name=row['name'],minimum=0,sources=[]));r['minimum']+=n;r['sources'] += [dict(set=s,copy=i+1,quantity=1,rule='membership') for i in range(n)]
 overrides=HERE/'verified-donor-quantities.json'
 if overrides.exists():
  hashes[str(overrides.relative_to(ROOT))]=sha(overrides)
  apply_verified(inventory,owned,json.loads(overrides.read_text())['rows'])
 elfile=STUDIO/'data/elementInfoList.json';geofile=STUDIO/'data/StudioPartDefinition2.txt';colorfile=STUDIO/'data/StudioColorDefinition.txt'
 elements={str(r['elementId']):r for r in json.loads(elfile.read_text())};geometry={};colors={}
 for r in csv.DictReader(geofile.open(),delimiter='\t'):
  if int(r['Studio ItemNo'])>0 and r['LDraw ItemNo']:geometry.setdefault(r['BL ItemNo'],r['LDraw ItemNo'])
 for r in csv.DictReader(colorfile.open(),delimiter='\t'):
  if r['BL Color Code'] and r['LDraw Color Code'] and int(r['LDraw Color Code'])>=0:colors.setdefault(r['BL Color Code'],r)
 parts={};unmapped=[]
 for e,r in inventory.items():
  if e not in elements:continue
  item=elements[e];code=str(item['blItemNo']);blcolor=str(item['blColorCode']);dims=REGULAR.get(code,SPECIAL.get(code))
  if not dims:continue
  file=geometry.get(code);col=colors.get(blcolor)
  if not file or not col:unmapped.append(e);continue
  path=next((p for p in [STUDIO/'ldraw/parts'/file,STUDIO/'ldraw/UnOfficial/parts'/file] if p.exists()),None)
  if not path:unmapped.append(e);continue
  parts[e]=dict(r,**dims,element=e,bl_part=code,bl_color=int(blcolor),ldraw=file,ldraw_color=int(col['LDraw Color Code']),color=col['BL Color Name'],geometry_path=str(path),geometry_sha256=sha(path))
 # Use one preferred exact element per shape/color pool, never sum aliases.
 preferred={}
 for e,r in sorted(parts.items(),key=lambda q:(-q[1]['minimum'],q[0])):preferred.setdefault(r['bl_part']+':'+str(r['ldraw_color']),e)
 snapshot=dict(rule='One exact element per owned set copy; deduplicate rows; do not sum aliases within a shape/color pool.',assumptions=['Donor sets complete and accessible.','No other reservations.','Cached membership is correct.'],owned_sets=owned,excluded_rows_without_id=invalid,input_sha256=hashes,catalog_sha256={str(p):sha(p) for p in [elfile,geofile,colorfile]},parts=parts,preferred=preferred,unmapped_candidate_elements=unmapped)
 dump(HERE/'inventory-snapshot.json',snapshot)
 report=defaultdict(lambda:dict(elements=0,minimum=0,stud_area=0))
 for e in preferred.values():
  p=parts[e];r=report[p['color']+' / '+p['kind']];r['elements']+=1;r['minimum']+=p['minimum'];r['stud_area']+=p['w']*p['d']*p['minimum']
 dump(HERE/'palette-summary.json',dict(report))
 print('Catalog:',len(parts),'exact elements,',len(preferred),'shape/color pools; unmapped candidates',len(unmapped))
 return snapshot
if __name__=='__main__':capture()
