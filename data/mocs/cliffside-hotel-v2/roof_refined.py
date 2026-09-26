"""Shallow, fully stud-connected hip roof made from canonical owned parts.

Eight thin courses replace the three tall, separated slope terraces.  Each
course rises one plate and retreats one stud on all four sides: an honest
stepped approximation to a 21.8-degree hip, not a continuously pitched skin.
The caller provides a complete studded deck at ``base``. No hinge, custom
geometry, unsupported diagonal placement, or reddish-brown 3039 is needed.
"""
from collections import Counter

from engine import rect


def _tile_strip(m, cells, z, colors):
    """Pack even strips without spending scarce single-stud closure tiles."""
    cells = set(cells)
    while cells:
        xx, yy = min(cells, key=lambda p: (p[1], p[0]))
        choices = [e for e in m.available(['tile'], colors, 8)
                   if min(m.parts[e]['w'], m.parts[e]['d']) == 1
                   and max(m.parts[e]['w'], m.parts[e]['d']) % 2 == 0]
        choices.sort(key=lambda e: (-m.parts[e]['w'] * m.parts[e]['d'],
                                    colors.index(m.parts[e]['ldraw_color'])))
        for e in choices:
            p = m.parts[e]
            for turn in (False, True):
                ww, dd = (p['d'], p['w']) if turn else (p['w'], p['d'])
                foot = rect(xx, yy, ww, dd)
                if foot <= cells:
                    m.put(e, xx, yy, z, turn)
                    cells -= foot
                    break
            else:
                continue
            break
        else:
            raise ValueError(f'Insufficient even brown roof tiles at {xx, yy, z}')


def roof(m, x=1, y=1, w=26, d=16, base=71):
    """Add interlocked plate decks, thin tiled hips and two ridge chimneys.

    Allocation is transactional. The returned fields preserve roof_study's
    interface; ``chimneys`` additionally records both stacks. The exposed
    perimeter of each level is tiled; the entire inner plateau is studded
    plate packing that carries the following course without floating pieces.
    """
    if any(not isinstance(v, int) for v in (x, y, w, d, base)):
        raise ValueError('Roof coordinates and dimensions must be integers')
    if d < 10 or d % 2 or w % 2 or w < d + 6:
        raise ValueError('Hip roof needs even depth >=10 and even width >=depth+6')

    start = len(m.pieces)
    previous = (m.module, m.step, m.serial, m.remaining.copy())
    levels = d // 2
    ridge_x, ridge_y = x + levels - 1, y + levels - 1
    ridge_w = w - 2 * (levels - 1)
    chimney_xy = [(ridge_x + 1, ridge_y),
                  (ridge_x + ridge_w - 3, ridge_y)]
    chimney_cells = set().union(*(rect(cx, cy, 2, 2)
                                  for cx, cy in chimney_xy))
    report = dict(slope_count=0, footprint=[x, y, w, d], base=base,
                  ridge_top=base + levels, courses=[],
                  construction='One-plate-rise, one-stud-setback tiled hip',
                  limitations=['The hip is finely stepped, not a smooth pitched plane.',
                               'Physical clutch, lifting and handling remain untested.'])
    hidden = [72, 71, 0, 1, 14, 4, 2, 322, 326, 321, 27, 323, 29, 5]
    try:
        m.module = 'main-roof'
        for course in range(levels):
            m.step = 42 + course
            xx, yy = x + course, y + course
            ww, dd = w - 2 * course, d - 2 * course
            zz = base + course
            footprint = rect(xx, yy, ww, dd)
            inside = rect(xx + 1, yy + 1, ww - 2, dd - 2)
            perimeter = footprint - inside
            if course == levels - 1:
                perimeter -= chimney_cells
            # A dark timber-like drip edge contains the reddish-brown roof.
            # Remaining upper brown courses may use dark brown when the
            # exact reddish-brown tile stock is exhausted.
            colors = [308, 70] if course == 0 else [70, 308]
            if course == levels - 1:
                m.fill(perimeter, zz, ['tile'], colors, 8, color_first=True)
            else:
                # Separate even-length strips avoid stranding scarce 1x1
                # tiles when a greedy 2x2 corner consumes a side's first cell.
                strips = [rect(xx, yy, ww, 1), rect(xx, yy + dd - 1, ww, 1),
                          rect(xx, yy + 1, 1, dd - 2),
                          rect(xx + ww - 1, yy + 1, 1, dd - 2)]
                for strip in strips:
                    _tile_strip(m, strip, zz, colors)
            # Large hidden plates make this a light layered shell. They meet
            # the tile ring edge-to-edge; the next layer spans their joints.
            m.fill(inside, zz, ['plate'], hidden, 64)
            report['courses'].append(dict(footprint=[xx, yy, ww, dd],
                                          base=zz, slopes=0))

        m.step = 42 + levels
        chimney_base = base + levels - 1
        for cx, cy in chimney_xy:
            cells = rect(cx, cy, 2, 2)
            for zz in (chimney_base, chimney_base + 3):
                m.fill(cells, zz, ['brick'], [19, 15], 4, color_first=True)
            m.fill(cells, chimney_base + 6, ['tile'], [70, 308], 4,
                   color_first=True)
        report['chimneys'] = [[cx, cy, chimney_base, 2, 2, 7]
                               for cx, cy in chimney_xy]
        report['chimney'] = report['chimneys'][0][:]
        report['piece_count'] = len(m.pieces) - start
        report['used'] = dict(sorted(Counter(q['element']
                                            for q in m.pieces[start:]).items()))
    except Exception:
        del m.pieces[start:]
        m.module, m.step, m.serial, m.remaining = previous
        raise
    m.module, m.step = previous[:2]
    return report
