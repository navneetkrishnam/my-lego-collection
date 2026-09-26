# Natural landscape review — v4

This revision uses the user's [Cliffside Hotel concept](reference-concept.png) as the decoration baseline. Its aim is the reference's layered, inhabited Mediterranean setting: terracotta pots at useful thresholds, fractured rock rather than a column grid, and rooted growth with uneven lengths, branches and exposed wall between plants. It builds on `garden-pool-v3` and retains the approved v6 building layout and the garden/pool amenities.

## What changed

- **21 additional planted pots:** 14 at courtyard level, four on guest/service balconies and three on dedicated stair-side stone ledges. Citrus, herbs and flowering plants use different pot heights, sizes and terracotta tones. Locations include the lobby entrance, library terrace, cottage foyer, common garden, promenade and pool seating area. The 14-stud stair remains clear; no chairs were added along the cliff edge.
- **Irregular rock formations:** the reserved cliff envelopes now contain unequal, staggered fractured masses and broken fragments. Three connecting slopes join the outcrops, with differently sized boulders embedded at computed surface contacts. These external slopes stay outside stairs and lower service rooms. The underlying retaining/support cores remain proxy volumes.
- **More natural creepers:** the five repeated pool-wall ribbons become three plants with different root spacing, drop lengths and lateral branches. Other creepers taper, branch asymmetrically, and alternate dense foliage with exposed stems. Facade stems are routed over solid wall and foliage placement is screened around openings. Balcony planters have gaps and unequal trailing growth.
- **Crevice planting:** fern-like fronds, sparse flowers and short trailing ivy are anchored to exposed modeled rock crowns. Buried anchors are removed when connecting slopes cover them.

The existing fountain, olive and cypress trees, lavender, cottage seating, pool shade, towels, ladder and emitting lanterns remain. Interior plans, building positions, doors, windows, pool footprint and stair alignment remain unchanged. This does not reproduce the concept's building proportions: the later, user-approved room program is the architectural baseline.

## Review images

- `blockout-concept.png`: full hotel daylight view; compare decoration with the supplied reference.
- `blockout-front.png`, `blockout-plan.png`, `blockout-rear.png`: complementary full-model views.
- `blockout-pool.png`: pool and service-side seating.
- `blockout-garden.png`: common side garden.
- `blockout-cottage.png`: private cottage garden.
- `blockout-dusk.png`: rendered lantern illumination.
- Four `plan-*.png` / `.svg` sheets: approved plans with added standing-pot footprints where applicable.

## Engineering checks and limits

`natural.POT_ITEMS` supplies the same conservative horizontal plant envelopes to the model, plan and circulation checker. Checks include floor/terrace containment, other furniture, walls, pergola posts, mutual plant overlap, the four pool walking strips and all 57 modeled destinations. Stair-side pots have dedicated ledges outside both stair guards. Connecting slope bounds are checked against the base, stairs and lower service rooms. Solid architecture and rock remain within the 128 × 114 stud base. A few leaves and thin twigs overhang its sides by less than one stud (under 8 mm); measured values are recorded separately in the verification report.

`verify.py` also checks deterministic regeneration, preservation of architecture and garden/pool amenities, source/image hashes and donor evidence. The delivery's `verification.json` records the result. Random variation uses fixed seeds, so irregular placement remains reproducible.

This is an authored architectural triangle mesh, not LEGO part placements. Detailed leaf/stem intersections, exact door swings, structural performance, LEGO connections, part quantities, physical assembly and LED wiring are not verified. The dusk image is a direct-lighting study; it does not simulate a designed physical lighting circuit. No donor inventory is reserved.

## Reproduce

Use `/private/tmp/fern-steam-py/bin/python` with `build.py`, `plans.py`, `check_layout.py`, then `render.py --view VIEW --width WIDTH --samples SAMPLES` and `verify.py`. This requires the repository's `fern-and-steam-v2/render_model.py`, preserved `garden-pool-v3` baseline, local donor records, NumPy, Pillow and Mitsuba CPU. The ZIP contains review assets and source, but those repository dependencies are required for reproduction.
