# Cliffside Hotel — unrestricted composition study

Step 1 of the redesign approved on 13 September 2026. The deliverable is an architectural blockout for reviewing proportions, silhouette and arrangement. Its geometry is authored and rendered locally, not an AI-generated replacement image.

## Review images

- `blockout-concept.png`: front-left view approximating the approved illustration's viewpoint.
- `blockout-front.png`: front elevation with slight elevation to expose terraces.
- `blockout-rear.png`: rear massing view; rear architectural design remains a later task.
- `blockout-plan.png`: overhead view for footprints, pool and circulation.
- Approved illustration: `../../cliffside-hotel-v3/reference-concept.png`.

## Provisional dimensions

| Element | Dimensions in stud units |
|---|---|
| Display base | 96 wide × 88 deep |
| Main villa walls | 40 wide × 28 deep × 42 high |
| Middle building walls | 16 wide × 22 deep × 32 high |
| Right wing walls | 28 wide × 26 deep × 28 high |
| Main terrace level | 40 above water datum |
| Right wing / pool terrace level | 38 above water datum |
| Pool | 22 × 12 |
| Stair clear width | 14 |
| Overall height including base | 90.75 |

If retained at LEGO stud scale, the footprint is 76.8 × 70.4 cm and height is approximately 72.6 cm. These are study dimensions, not a final size commitment or piece estimate. Vertical units are studs too, not plates.

## What changed after the first visual inspection

The middle building was raised from 27 to 32 studs and brought forward to expose its facade between the wings. The right arcade floor was raised to the pool terrace datum. The pool has an exposed recessed water plane. Main-villa side openings and simple balcony slab envelopes were added to make side and front proportions readable. The stair landing was widened in depth from 3 to 6 studs.

## Interpretation and limits

The three roof silhouettes step down from the villa through the middle building to the right wing. The pool and arcade face a shared open courtyard. The stair descends in two offset flights between large terrain volumes.

Rectangular window voids indicate opening size and rhythm; final arches, shutters, glazing and surrounds are not designed yet. Rock blocks represent cliff envelopes, not finished rockwork. Solid terrace parapets stand in for future balustrades. Pergola frames show sheltered-space extent. Roof planes are continuous hip envelopes, not LEGO tile assemblies. Rear walls are deliberately unresolved.

`blockout.ldr` contains triangle proxy geometry, not LEGO part instances. It must not be treated as a bill of materials, build instructions or a connection-verified model. No donor allocation, physical assembly or legal connection claim is made. Stair risers and terrace transitions also need conversion to a buildable part grid later.

## Reproduce

Use `/private/tmp/fern-steam-py/bin/python build.py` from this directory. Then run that Python executable with `render.py --view concept --samples 160 --width 1600`. Other available views are `front`, `rear` and `plan`.

`dimensions.json` records component envelopes and the LDraw hash. Each render has adjacent JSON provenance recording model, image, generator and renderer hashes. The verification report checks deterministic regeneration, finite nondegenerate triangles, render provenance and dimensions only.

## Next checkpoint

Review the balance of the three buildings, courtyard and cliff against the approved concept. Once the composition is accepted, develop one representative facade bay and roof corner with actual LEGO parts before applying that architectural language across the whole model. Landscaping and full construction verification follow in separate stages.
