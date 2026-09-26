"""Self-contained offline coordinate review guide, with no network dependencies."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent

def make():
 data={name:json.loads((H/file).read_text()) for name,file in [('model','model.json'),('bom','bom.json'),('allocation','allocation.json'),('verification','verification.json'),('geometry','geometry-verification.json')]}
 used={q['element'] for q in data['model']['pieces']}
 data['spec']={e:p for e,p in json.loads((H/'inventory-snapshot.json').read_text())['parts'].items() if e in used}
 payload=json.dumps(data,separators=(',',':')).replace('</','<\\/')
 template=(H/'guide-template.html').read_text()
 (H/'guide.html').write_text(template.replace('__DATA__',payload))
 print('Guide:',len(data['model']['pieces']),'placements;',len(data['bom']),'exact elements;',len(data['allocation']),'donor allocations')

if __name__=='__main__':make()
