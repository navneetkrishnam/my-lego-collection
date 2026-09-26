"""Independent artifact reconciliation (stdlib only)."""
import collections
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def main():
    model=json.loads((HERE/'model.json').read_text())
    snap=json.loads((HERE/'inventory-snapshot.json').read_text())
    bom=json.loads((HERE/'bom.json').read_text())
    picks=json.loads((HERE/'allocation.json').read_text())
    report=json.loads((HERE/'verification.json').read_text())
    ps=model['pieces']
    assert len({p['key'] for p in ps})==len(ps)
    assert [p['step'] for p in ps]==sorted(p['step'] for p in ps)
    for p in ps:
        assert all(isinstance(p[k],int) and p[k]>=0 for k in ('x','y'))
        assert all(p[k]>0 for k in ('w','d','h'))
        assert p['rotation'] in (0,90,180)
    counts=collections.Counter(p['element'] for p in ps)
    assert counts=={b['element']:b['required'] for b in bom}
    for e,n in counts.items():assert n<=snap['elements'][e]['minimum']
    allocated=collections.Counter();seen=set()
    for pick in picks:
        donor=(pick['set'],pick['copy'])
        assert donor not in seen;seen.add(donor)
        assert len(pick['elements'])==len(set(pick['elements']))
        for e in pick['elements']:
            assert any((s['set'],s['copy'])==donor for s in snap['elements'][e]['sources'])
            allocated[e]+=1
    assert allocated==counts
    # Reconcile parsed LDraw instances, colors, transforms and elevations.
    tokens=[l.split() for l in (HERE/'fern-and-steam.ldr').read_text().splitlines() if l.startswith('1 ')]
    assert len(tokens)==len(ps)
    transforms={0:[1,0,0,0,1,0,0,0,1],90:[0,0,1,0,1,0,-1,0,0],180:[-1,0,0,0,1,0,0,0,-1]}
    for p,t in zip(ps,tokens):
        assert len(t)==15
        assert int(t[1])==p['ldraw_color'] and t[-1]==p['ldraw']
        assert [float(v) for v in t[2:5]]==[(p['x']+p['w']/2)*20,-(p['z']+p['h'])*8,(p['y']+p['d']/2)*20]
        assert [float(v) for v in t[5:14]]==transforms[p['rotation']]
    assert report['piece_count']==sum(counts.values())
    assert report['unique_elements']==len(counts)
    for file,sha in report['hashes'].items():
        assert hashlib.sha256((HERE/file).read_bytes()).hexdigest()==sha,file
    print(f'PASS: {len(ps)} LDraw placements = model = BOM = donor allocation; exact IDs, integer stud grid, rotations and recorded hashes reconcile.')

if __name__=='__main__':main()
