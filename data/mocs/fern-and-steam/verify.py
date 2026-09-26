"""Conservative inventory and explicitly simplified construction checks."""
from collections import Counter


def conservative_inventory(owned, set_parts):
    inventory, invalid = {}, 0
    for set_id, copies in sorted(owned.items()):
        seen = set()
        for part in set_parts[set_id]:
            raw = part.get('id')
            if raw is None or not str(raw).strip():
                invalid += 1
                continue
            element = str(raw)
            if element in seen:
                continue
            seen.add(element)
            row = inventory.setdefault(element, {'minimum': 0, 'sources': []})
            row['minimum'] += copies
            row['sources'].extend({'set': set_id, 'copy': i + 1} for i in range(copies))
    return inventory, invalid


def check_model(pieces, inventory, footprint):
    used = Counter(p['element'] for p in pieces)
    result = {
        'shortages': {k: n - inventory.get(k, {}).get('minimum', 0)
                      for k, n in sorted(used.items()) if n > inventory.get(k, {}).get('minimum', 0)},
        'overlaps': [], 'unsupported': [], 'out_of_bounds': [],
        'blocked_insertions': [], 'components': 0,
        'simplified_accessory_instances': sum(p['kind'] != 'box' for p in pieces),
    }
    graph = [set() for _ in pieces]
    def intersect(a, b, axis, size):
        return min(a[axis] + a[size], b[axis] + b[size]) - max(a[axis], b[axis]) > 1e-8
    def xy(a, b):
        return intersect(a, b, 'x', 'w') and intersect(a, b, 'y', 'd')
    def top(p):
        return p['z'] + p['h']
    for i, p in enumerate(pieces):
        if p['x'] < 0 or p['y'] < 0 or p['z'] < 0 or p['x'] + p['w'] > footprint[0] or p['y'] + p['d'] > footprint[1]:
            result['out_of_bounds'].append(p['key'])
        supports = []
        for j, q in enumerate(pieces[:i]):
            if not xy(p, q):
                continue
            if p['kind'] == q['kind'] == 'box' and intersect(p, q, 'z', 'h'):
                result['overlaps'].append([p['key'], q['key']])
            if abs(p['z'] - top(q)) < 1e-8 and q['studded']:
                supports.append(j)
                graph[i].add(j)
                graph[j].add(i)
            if p['kind'] == q['kind'] == 'box' and q['z'] >= top(p) - 1e-8:
                result['blocked_insertions'].append([p['key'], q['key']])
        if p['z'] > 0 and not supports:
            result['unsupported'].append(p['key'])
    unseen = set(range(len(pieces)))
    while unseen:
        result['components'] += 1
        todo = [min(unseen)]
        while todo:
            index = todo.pop()
            if index not in unseen:
                continue
            unseen.remove(index)
            todo.extend(graph[index] & unseen)
    result['structural_pass'] = not any(result[k] for k in (
        'overlaps', 'unsupported', 'out_of_bounds', 'blocked_insertions')) and result['components'] == 1
    result['inventory_pass'] = not result['shortages']
    return result
