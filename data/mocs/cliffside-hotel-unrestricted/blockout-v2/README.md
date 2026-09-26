# Cliffside Hotel — composition revision 2

This revision implements the user's three corrections to the first unrestricted blockout. It remains step 1: architectural composition, not finished LEGO detailing.

1. **L-shaped main villa.** A 36 × 22 stud rear bar joins a 16 × 15 stud forward return. Both are three storeys, with 42 stud wall height. The footprint has a real 20 × 15 stud recess facing the entrance court. A continuous L-shaped hip-roof envelope follows it; this is not a flat wall with a projecting balcony attached.
2. **Garden beside the villa.** The main garden occupies the outer left side, with pergola and plain green planting envelopes. Its planting and pergola are wholly left of the villa footprint. The front recess and apron remain an entrance court. The shared pool/garden terrace remains on the right side of the complex.
3. **Right wing descends into the cliff.** Three floors begin at heights 12, 26 and 40 studs; the main courtyard is at 40. Thus two floors start below courtyard level. The middle of these floors is an open arcade. The wing stands on a low plinth instead of the high plateau, and has been moved forward and outward so its lower facade is visible beside the pool terrace.

## Dimensions

| Item | Stud units |
|---|---|
| Base | 120 × 88 |
| Overall height including base | 90.75 |
| Main villa footprint perimeter | (22,10), (58,10), (58,32), (38,32), (38,47), (22,47) |
| Main villa garden bounds | x=3..22, depth=12..50 |
| Connector | 16 × 22 × 32 walls, starting at height 40 |
| Right wing footprint | x=90..118, depth=40..66 |
| Right wing | 28 × 26 × 42 walls, starting at height 12 |
| Right wing floor levels | 12, 26, 40 |
| Pool terrace | height 38 |
| Pool | 22 × 12 |
| Stair clear width | 14 |

At literal LEGO stud scale the provisional footprint is 96 × 70.4 cm, height approximately 72.6 cm. The expanded width makes room for the side garden and for an exposed descending wing. This is not a final size commitment. All vertical numbers above are studs, not plates.

## Review files

- `blockout-concept.png`: main front-left view, using the same camera direction as revision 1.
- `blockout-plan.png`: overhead footprint; the L and side garden are clearest here.
- `blockout-front.png`: shows the wing's floor levels relative to the pool terrace.
- `blockout-rear.png`: reverse massing view; rear facade design remains unresolved.
- `blockout.ldr`: authored proxy triangles, **not LEGO part instances**.
- `dimensions.json`: component envelope schedule and model hash.
- `verification.json`: scoped geometry and provenance checks.

The first unrestricted blockout is preserved in `../blockout/`. The approved illustration remains `../../cliffside-hotel-v3/reference-concept.png`.

## Scope

Windows, planting beds, cliff blocks, roof surfaces and parapets are placeholders. The hip-roof envelope is a triangulated continuous surface over two intersecting roof volumes. It does not prescribe LEGO roof connections. Interior joins, doorway design, final rockwork, stair geometry on a LEGO plate grid and full construction checks remain later work. No bill of materials, donor allocation or physical assembly claim is made.

Reproduce with `/private/tmp/fern-steam-py/bin/python build.py`, then `render.py --view concept --samples 160 --width 1600` with the same interpreter. The renderer uses mesh utilities already in this repository and the installed Mitsuba environment. Run `verify.py` after rendering all four views.
