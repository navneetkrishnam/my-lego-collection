# Fixed glazed lantern roof research

Recommended: a **12 × 6-stud, two-brick-high glazed lantern**, centered on the proposed 18 × 10-stud building. Its four fixed windscreens avoid angled window frames, hinges, or floating glazing. Leave 3-stud opaque shoulders and 2-stud front/rear roof bands around it.

This is a geometry-supported proposal, not a physical build test. Counts below are conservative membership counts: each exact element ID counts at most once per owned set copy.

## Glazing and exact inventory

| Element ID | Owned cached color | Conservative available | Shape | Donor sets |
|---|---|---:|---|---|
| 6503221 | Transparent | 5 | 92583.dat, Windscreen 3 × 6 × 2 | 60500, 60454, 60453, 42659, 11370 |
| 6503219 | Tr. Light Blue | 3 | 92583.dat | 60316, 60330, 60371 |
| 6510175 | Transparent | 9 | 4176.dat, Windscreen 2 × 6 × 2 | 60488, 60435, 60452, 60404, 42695, 42644, 42659, 60363, 42603 |

Use **4 × 6503221**. Only five clear 92583 windscreens are conservatively established, so a six-piece 18-stud-wide version is not supported. The older 6255920 listing has no cached color or Studio mapping and occurs in the same three sets as the blue windscreen; do not assume it supplies a sixth clear piece.

Exact element-to-shape/color mappings were checked in `/Applications/Studio 2.0/data/elementInfoList.json`: 6503221 → BrickLink 92583, color 12; 6503219 → 92583, color 15. Shape geometry is the official LDraw part distributed locally in `/Applications/Studio 2.0/ldraw/parts/92583.dat` (official update 2010-03). Public geometry source: https://library.ldraw.org/library/official/parts/92583.dat .

## Coordinates and attachment

Use standard LDraw axes, with positive Y downward. Let the roof ridge be Y=0 and roof center be X=Z=0. A 92583 body has bounds X=[−60,60], Y=[0,48], Z=[−50,10]. Its two upper studs are at (±50,0,0).

Place four clear windscreens:

| Center | Rotation |
|---|---|
| (−60,0,−10) | identity |
| (+60,0,−10) | identity |
| (−60,0,+10) | 180° about Y: diag(−1,1,−1) |
| (+60,0,+10) | 180° about Y: diag(−1,1,−1) |

Combined body bounds: X=[−120,120], Z=[−60,60], Y=[0,48]. The glass slopes are approximately 45°. Each part includes clear triangular side cheeks and an open high back; the opposing high backs meet at Z=0. A two-stud-deep ridge cap covers the central opening and connects the opposed parts.

Lower supports need a connected studded frame with its top plane at Y=48. Its useful stud locations are:

- Eaves: X=−110,−90,…,+110, at Z=−50 and Z=+50.
- Outer side rails: X=−110 and +110, at Z=−30,−10,+10,+30.
- Central two-column rail: X=−10 and +10, at Z=−30,−10,+10,+30.

These positions are a normal stud grid, and the eave and side rails support the windscreens' underside rim. Keep the glazed bays open underneath. Connect the rail frame into the cornice/opaque roof bands; avoid four disconnected perimeter assemblies.

Upper studs of the assembled roof occur at X={−110,−10,+10,+110}, Z={−10,+10}, Y=0. Add two 2 × 6 plates running across X, with centers (−60,−8,0) and (+60,−8,0). Each connects all four top studs of its opposing pair. Use **identity rotation**: actual 3795.dat has its long axis on local X (X bounds ±60, Z bounds ±20). The 3666.dat 1 × 6 and 3710.dat 1 × 4 plates also run along local X; do not assume the long dimension is Z. Then bridge the seam between these ridge plates with a 1 × 4 plate running across X at (0,−16,−10), and optionally another at (0,−16,+10). Finish with an even layer of tiles. The final cap needs leveling plates under any tiles beyond the seam bridge so all tiles sit at the same height.

## Support and cap candidates

| Element ID | Shape/color | Conservative available | Suggested use |
|---|---|---:|---|
| 379526 | 3795.dat, black plate 2 × 6 | 25 | 2 for ridge; optional lower frame |
| 366626 | 3666.dat, black plate 1 × 6 | 34 | eave/side frame rails |
| 371026 | 3710.dat, black plate 1 × 4 | 29 | ridge seam bridges and frame |
| 302326 | 3023.dat, black plate 1 × 2 | 43 | cap leveling and frame ties |
| 663626 | 6636.dat, black tile 1 × 6 | 28 | smooth ridge cap |
| 243126 | 2431.dat, black tile 1 × 4 | 17 | shorter ridge cap segments |
| 379501 | 3795.dat, white plate 2 × 6 | 23 | white alternative |
| 366601 | 3666.dat, white plate 1 × 6 | 36 | white alternative |

Counts are total collection minima before the parent model allocates other modules. A complete BOM must check the model's combined demand.

The 4176 windscreen is an alternative 18 × 4-stud lantern using six clear pieces, but its glazing is steeper and the roof is much shallower; the 92583 12 × 6 solution is the preferable translation of the approved concept.
