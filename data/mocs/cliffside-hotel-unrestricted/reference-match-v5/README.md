# Reference match review — v5

This pass responds to the request for pots on the staircase and repeated comparison against the supplied [reference concept](reference-concept.png), aiming for approximately 75% visual resemblance. The comparison is a design judgment, not a computed image similarity metric. The saved first iteration is under `iterations/01`; the final visual assessment is in `COMPARISON.md`.

## Staircase

Ten additional terracotta pots now stand directly along the staircase edges, on level stone pads. The pads span adjacent tread edges and are supported into the existing solid stair volume. They are not balanced across uneven treads. Plants alternate between flowers, herbs and citrus, with varied size and spacing.

The stair remains 14 studs wide. Its reserved clear centre is now 9 studs wide, rather than the full 14 studs claimed before edge pots were added. Full plant envelopes and pad caps stay outside that centre. The three previous outer ledge pots remain, and larger rooted rose bushes grow beside the landings. `plan-staircase.png` and `.svg` show all ten stair pots and the clear route.

Separate limestone tread caps, projecting nosings and guard facing add masonry detail without shifting the 48 original treads or the straight alignment.

## Other reference-driven changes

- Rock fragments have clipped rectangular outlines and a mix of grey and tan stone, reducing the previous rounded-boulder appearance.
- Broader rose pockets, fuller pool-wall cascades and grouped crevice foliage increase planting density where the reference concentrates it.
- Ovate leaves with raised midribs replace the earlier diamond shapes.
- Four selected villa window openings gain arched stone infill and voussoirs. The openings retain their original bounding positions; their glazed upper corners now become stone. No door opening is altered, and the room plan remains unchanged.
- Smaller, varied courtyard pavers replace the coarse repeating pattern.
- Glossy blue sea tiles and small highlights add surface variation along the visible water edge.
- Warmer daylight and warm brown glazing proxies move the colour balance toward the concept. Glazing is still an opaque material proxy, not a rendered furnished interior.

The main villa, two-storey cottage, descending service building, pool size, gardens, furniture layout and public/private access program are preserved. The earlier garden fountain, trees, lavender, pool shade, towels and lanterns remain.

## Verification

`verify.py` checks deterministic export, preserved architecture records and room layouts, the 57 modeled circulation destinations, outdoor pot footprints, stair pot supports and their nine-stud clear centre, arched window bounds, and source/image provenance. The five plan sheets share their placement schedules with the model.

The full physical shape of every leaf, door swing and assembly is not collision-tested. The staircase pads, rock supports and rose beds are solid proxy volumes, not engineered LEGO assemblies. Part quantities, LEGO connections, structural performance, physical assembly and lighting wiring remain unverified.

## Review files

Use `blockout-front.png` alongside the reference as requested, and `blockout-concept.png` for a closer camera-angle comparison. Pool, garden, cottage, overhead, rear and dusk views provide additional checks. Five `plan-*` sheets cover the courtyard, guest floor, cottage, services and staircase.

Reproduce with `/private/tmp/fern-steam-py/bin/python`: run `build.py`, `plans.py`, `check_layout.py`, all eight `render.py --view VIEW --width WIDTH --samples SAMPLES` commands, and `verify.py`. Requires the repository's Mitsuba helper, preserved `natural-landscape-v4` baseline, local donor records, NumPy and Pillow. The ZIP includes source and review artifacts; it is not a standalone installation of those dependencies.
