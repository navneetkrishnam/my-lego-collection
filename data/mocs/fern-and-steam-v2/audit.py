"""Conservative inventory and stud-graph audit, with explicitly bounded claims.

This does not replace Studio collision checking or a physical build. Solid
boxes cover ordinary bricks/plates/tiles; decorative meshes are not boxes.
"""
from collections import Counter, defaultdict
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def ports(p, top):
    if p['kind']=='insert' or top and not p['studded']: return set()
    z=p['z']+(p['h'] if top else 0)
    cells={(p['x']+a+.5,p['y']+b+.5,z) for a in range(int(p['w'])) for b in range(int(p['d']))}
    if p['kind']=='arch' and top:
        return {(x,y,z-3 if x in (p['x']+.5,p['x']+5.5) else z) for x,y,z in cells}
    if p['kind']=='small_arch' and not top:
        return {(x,y,z) for x,y,z in cells if x in (p['x']+.5,p['x']+3.5)}
    if p['kind']=='roof':
        if top:
            rear=p['matrix'][0]<0
            return {(p['x']+a+.5,p['y']+(.5 if rear else 2.5),z) for a in (0,5)}
        return {(x,y,z) for x,y,z in cells if x in (p['x']+.5,p['x']+5.5) or y in (p['y']+.5,p['y']+2.5)}
    return cells


def inspect_model(pieces, inventory):
    counts=Counter(p['element'] for p in pieces)
    shortages={e:n-inventory.get(e,0) for e,n in sorted(counts.items()) if n>inventory.get(e,0)}
    graph={p['key']:set() for p in pieces}
    tops=defaultdict(set)
    bottoms=defaultdict(set)
    overlaps=[]
    outside=[]
    duplicate=[]
    seen={}
    by_key={p['key']:p for p in pieces}
    insert_errors=[]
    expected={'6514119':('6262945',[-32,0,5]), '6514142':('4530590',[0,8,4]),
              '6511024':('6256127',[0,4.5,5])}
    for p in pieces:
        if p['kind']=='insert':
            parent=by_key.get(p.get('parent'))
            rule=expected.get(p['element'])
            if not parent or not rule or parent['element']!=rule[0] or p.get('offset')!=rule[1]:
                insert_errors.append(p['key'])
            else:
                expected_origin=[parent['origin'][i]+sum(parent['matrix'][3*i+j]*rule[1][j]
                                  for j in range(3)) for i in range(3)]
                if p.get('matrix')!=parent.get('matrix') or any(abs(a-b)>1e-6 for a,b in zip(p.get('origin',[]),expected_origin)) or len(p.get('origin',[]))!=3:
                    insert_errors.append(p['key'])
                graph[p['key']].add(parent['key']); graph[parent['key']].add(p['key'])
            continue
        for pt in ports(p,True): tops[pt].add(p['key'])
        for pt in ports(p,False): bottoms[pt].add(p['key'])
        if p['x']<0 or p['y']<0 or p['z']<0 or p['x']+p['w']>24 or p['y']+p['d']>24:
            outside.append(p['key'])
        loc=(p['element'],p['x'],p['y'],p['z'],p['w'],p['d'])
        if loc in seen: duplicate.append([seen[loc],p['key']])
        seen[loc]=p['key']
    for pt in tops.keys() & bottoms.keys():
        for a in tops[pt]:
            for b in bottoms[pt]:
                if a!=b: graph[a].add(b); graph[b].add(a)
    ordinary=[p for p in pieces if p['kind']=='box']
    for i,a in enumerate(ordinary):
        for b in ordinary[i+1:]:
            if all(min(a[axis]+a[size],b[axis]+b[size])-max(a[axis],b[axis])>1e-7
                   for axis,size in [('x','w'),('y','d'),('z','h')]): overlaps.append([a['key'],b['key']])
    remaining=set(graph); components=[]
    while remaining:
        todo=[min(remaining)]; component=[]
        while todo:
            key=todo.pop()
            if key not in remaining: continue
            remaining.remove(key); component.append(key); todo.extend(graph[key] & remaining)
        components.append(sorted(component))
    return dict(shortages=shortages, duplicate_placements=duplicate, nominal_out_of_bounds=outside,
                solid_body_overlaps=overlaps, invalid_inserts=insert_errors,
                connected_components=len(components), isolated_components=sorted(components,key=len)[:-1],
                stud_graph_connected=len(components)==1,
                inventory_pass=not shortages,
                regular_solid_overlap_pass=not overlaps,
                limitations=['No triangle-level full-model collision test.',
                             'Stud graph checks engagement positions, not clutch strength, loading or build access.',
                             'Arch/frame/roof/plant/mug meshes are excluded from ordinary solid-box collision checks.',
                             'Decorative geometry can extend beyond its nominal mounting footprint.',
                             'Physical build NOT TESTED.'])


if __name__=='__main__':
    model=json.loads((HERE/'model.json').read_text())
    snapshot=json.loads((HERE/'inventory-snapshot.json').read_text())
    report=inspect_model(model['pieces'],{e:s['minimum'] for e,s in snapshot['parts'].items()})
    (HERE/'verification.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2))
    if any(report[k] for k in ('shortages','duplicate_placements','nominal_out_of_bounds','solid_body_overlaps','invalid_inserts')) or not report['stud_graph_connected']:
        raise SystemExit(1)
