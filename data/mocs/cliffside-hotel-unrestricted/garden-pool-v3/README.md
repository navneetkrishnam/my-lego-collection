# Garden and pool detail review — v3

This revision develops the two gardens and the pool terrace in response to the user's request. It builds on `hotel-atmosphere-v2`, preserving its architecture, planting and approved v6 room layout. The earlier review included cypress trees, climbing flowers, planted pergolas, garden furniture and lantern geometry; this review adds garden focal features, tree and plant variety, pool amenities, and actual lantern emission in the renders.

## Gardens

The common side garden gains a compact tiered fountain in the open space between the pergola and southern bed. Its 4.8 × 4.8 stud footprint leaves the existing public garden approach available. The fountain has bowls, a basin and modeled streams. Lavender complements the existing flowers and cypress trees. An olive tree grows from an existing planted pot in the northern bed, providing a broader canopy below the tall cypresses.

The cottage garden gains a second olive tree in its existing planted pot, lavender along the front bed, cushions and pillows on the existing bench, and hanging lanterns on the pergola. The olive canopy stays below the first-floor garden-facing window. The foyer and private garden entrance remain unchanged.

## Pool terrace

The pool retains its 22 × 16 stud water footprint. The new surface has shallow modeled ripples and a glossy material; this is a stylized water proxy, not a fluid simulation. Segmented coping slabs and a turquoise waterline give the basin a finished edge. A ladder mounts on the northern coping with its rails and rungs extending into the pool void.

A striped, wall-mounted awning shades the existing loungers next to the service building. Its lowest modeled point is +46.7, and it occupies x89–95.95. It therefore stays over the service-side seating band, beyond the four-stud clear walking strip at x84.5–88.5. Brackets attach it to the solid west wall of the service building. A narrow towel stand fits between the loungers beside that wall. A topiary pot sits at the northern end of the seating band. Drinks and a folded towel use the existing side table. No seating is added at the cliff-facing pool edge.

The paving palette is warmer and less contrasty, reducing the previous checkerboard effect without changing the paver footprints.

## Lighting

Lantern faces now emit warm light. Existing lanterns and new pergola, garden-rail and pool-side fixtures share the luminous material. New hanging fixtures have visible supports; pool fixtures attach to the service wall. Emission is modest in daylight and stronger in the dusk view.

The dusk view is a direct-lighting study with 8 emitter samples and 2 BSDF samples per camera sample. Daylight views use path tracing. Studio lights are placed well beyond the camera, with their size increased proportionally, to keep lighting cards out of view while retaining broad illumination. The count of emitting triangles and the lighting mode are recorded in each render's metadata.

These are rendered light sources. Physical LEDs, wiring, batteries, heat and connection choices have not been designed. The hotel windows remain the existing opaque glazing proxies; this pass does not light room interiors.

## Plan and circulation consistency

`garden_pool.SITE_ITEMS` is the shared source for the fountain, towel stand and topiary footprints. The generator, courtyard plan and circulation checker all use this schedule. `atmosphere.LANDSCAPE_FURNITURE` continues to supply the earlier bistro setting and cottage bench.

All baseline named objects and all interior floor definitions are preserved. The new floor-standing items fit within the site and do not overlap existing furniture or each other. Circulation checks include their footprints, the earlier garden furniture and the cypress footprints, while preserving all four clear pool walking strips and access to all 57 destinations.

Decorative leaves, door swings, awning loads, exact headroom and physical assembly are outside that circulation check. Actual LEGO part quantities and connections remain unverified. Donor sets remain candidates; no inventory has been reserved.

## Review views

- `blockout-pool.png`: pool and service-side seating close-up.
- `blockout-garden.png`: common garden close-up, including fountain, pergola and planting.
- `blockout-cottage.png`: private garden close-up, including the olive tree and cushioned bench.
- `blockout-dusk.png`: full hotel with emitting lanterns.
- `blockout-concept.png`: full hotel in daylight.
- `blockout-front.png`, `blockout-plan.png`, `blockout-rear.png`: consistency views.
- `plan-arrival.png` / `.svg`: updated courtyard plan with the new site items.
- `plan-cottage`, `plan-guest-floor`, `plan-services`: retained room plans in PNG and SVG.
- `verification.json`: deterministic export, preservation, spatial and image-provenance checks.

The original concept image, source scripts, exported model and a per-file hash manifest are included in the review ZIP. Images are rendered from `blockout.ldr`, an authored architectural triangle mesh rather than LEGO part instances.

## Reproduce

Use `/private/tmp/fern-steam-py/bin/python` to run `donors.py`, `build.py`, `plans.py` and `check_layout.py`. Use `render.py --view VIEW --samples SAMPLES --width WIDTH` for the eight views, then run `verify.py`. Requires Mitsuba CPU, the repository's `fern-and-steam-v2/render_model.py` helper, local donor data and the preserved `hotel-atmosphere-v2` baseline. Final render sample counts and source hashes are stored beside each PNG.
