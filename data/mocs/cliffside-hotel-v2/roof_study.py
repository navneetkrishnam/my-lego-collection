"""Continuous, inventory-limited roof study for the 24-stud hotel facade.

Units follow engine.Model: horizontal studs, vertical plates, Z upward.
The default footprint uses 66 exact reddish-brown 3039 slopes.  No custom
geometry, non-right-angle transforms, or hinge assemblies are introduced.
The caller supplies a complete, studded roof deck at ``base``.
"""
from collections import Counter


def _rect(x, y, w, d):
    return {(xx, yy) for xx in range(x, x + w) for yy in range(y, y + d)}


def roof(m, x=1, y=1, w=26, d=16, base=68):
    """Add three connected roof courses; roll back allocation on shortage.

    The sides are intentionally tiled stair steps, the front and back are
    actual 45-degree slopes, and the ridge is flat.  Returns an allocation
    report, including the exact footprint and chimney location.
    """
    if any(not isinstance(v, int) for v in (x, y, w, d, base)):
        raise ValueError('Roof coordinates and dimensions must be integers')
    if w < 16 or w % 2 or d < 16 or d % 2:
        raise ValueError('Three-course roof needs even width >=16 and depth >=16')
    slope_element = '4211202'
    needed = sum(w - 4 * course for course in range(3))
    if m.remaining.get(slope_element, 0) < needed:
        raise ValueError(
            f'Roof requires {needed} exact 4211202 reddish-brown 3039 slopes; '
            f'{m.remaining.get(slope_element, 0)} remain. Reserve roof first.'
        )
    p = m.parts[slope_element]
    if (p['bl_part'], p['w'], p['d'], p['h']) != ('3039', 2, 2, 3):
        raise ValueError('Roof requires canonical 3039 dimensions 2x2x3 plates')
    if p.get('origin_offset') != [0, 0, 10]:
        raise ValueError('Canonical 3039 needs origin_offset [0,0,10]')

    start = len(m.pieces)
    previous = (m.module, m.step, m.serial, m.remaining.copy())
    m.module = 'main-roof'
    report = {'slope_count': needed, 'footprint': [x, y, w, d],
              'base': base, 'ridge_top': base + 10, 'courses': []}
    # Never use cream facade stock for concealed packing. All exterior parts
    # are brown, except the deliberately cream chimney and its brown cap.
    hidden = [72, 71, 0, 1, 14, 4, 2, 322, 326, 321, 27, 323, 29, 5]
    warm = [70, 308, 484, 84, 28]
    try:
        for course in range(3):
            xx, yy = x + 2 * course, y + 2 * course
            ww, dd = w - 4 * course, d - 4 * course
            zz = base + 3 * course
            m.step = 42 + course
            # With Model's rotated canonical origin offset, angle=0 slopes
            # down toward -Y, and 180 slopes down toward +Y. All placements
            # keep their regular rectangular underside on the supplied deck.
            for sx in range(xx, xx + ww, 2):
                m.put(slope_element, sx, yy, zz, angle=0)
                m.put(slope_element, sx, yy + dd - 2, zz, angle=180)

            # A solid central plateau carries the complete next course.
            # It also covers every underlying seam, with no suspended panels.
            inner = _rect(xx + 2, yy + 2, ww - 4, dd - 4)
            m.fill(inner, zz, ['brick'], hidden, 32)

            # Two-stud-wide tiled terraces form the lower stepped hip ends.
            # Two plate courses + one tile equal each three-plate roof rise.
            ends = (_rect(xx, yy + 2, 2, dd - 4)
                    | _rect(xx + ww - 2, yy + 2, 2, dd - 4))
            for plate_height in (0, 1):
                m.fill(ends, zz + plate_height, ['plate'], warm, 16,
                       color_first=True)
            m.fill(ends, zz + 2, ['tile'], warm, 8, color_first=True)
            report['courses'].append({'footprint': [xx, yy, ww, dd],
                                      'base': zz, 'slopes': ww})

        m.step = 45
        ridge = _rect(x + 6, y + 6, w - 12, d - 12)
        # A 2x2 chimney stands directly on the studded structural plateau,
        # with a matching opening in the surrounding ridge tiling.
        chimney_x, chimney_y = x + 8, y + 7
        chimney = _rect(chimney_x, chimney_y, 2, 2)
        m.fill(ridge - chimney, base + 9, ['tile'], warm, 8,
               color_first=True)
        for level in (base + 9, base + 12):
            m.fill(chimney, level, ['brick'], [19, 15], 4,
                   color_first=True)
        m.fill(chimney, base + 15, ['tile'], [70, 28, 308], 4,
               color_first=True)
        report['chimney'] = [chimney_x, chimney_y, base + 9, 2, 2, 7]
        report['piece_count'] = len(m.pieces) - start
        report['used'] = dict(sorted(Counter(
            q['element'] for q in m.pieces[start:]).items()))
    except Exception:
        del m.pieces[start:]
        m.module, m.step, m.serial, m.remaining = previous
        raise
    m.module, m.step = previous[:2]
    return report
