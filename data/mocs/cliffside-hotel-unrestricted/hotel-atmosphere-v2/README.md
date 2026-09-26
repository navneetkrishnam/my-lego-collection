# Cliffside Hotel — richer exterior atmosphere

This revision responds to the request for substantially more decoration and a closer feel to the original concept. It builds on `hotel-exteriors-v1` and keeps the approved v6 building positions, floor plans, room program, doors, stairs, pool and lounge-chair locations.

## What changed

- **Planting across the architecture:** five long balcony/terrace flower troughs with trailing growth, larger climbing roses on solid facade piers, three cypress trees, fuller existing garden beds, terracotta pots and planted rock pockets. Pink, pale rose and cream flowers contrast with several greens.
- **Both pergolas:** timber rafters and lattice, flowering canopies and climbing stems around their existing posts. A two-seat bistro setting sits in the common garden; a bench sits inside the cottage's private garden.
- **Terrace finish:** varied stone pavers, turned stone balusters mounted above the existing perimeter guards, lanterns along the stair parapets and cushions on the existing pool loungers.
- **Cliff and retaining walls:** masonry courses dress the retaining faces. The 18 rectangular cliff placeholders become layered faceted rocks within their original planning envelopes, with planting rooted on their modeled upper surfaces. Trailing plants soften the retaining faces below the gardens and pool.

The original image remains the visual reference for planted terraces, flowering balconies, cream stone, green shutters, terracotta and lanterns. The room program and building proportions follow the later user-approved layout. This is a denser architectural study, not an assertion that it precisely reproduces the concept or that its geometry represents real LEGO parts.

## Spatial consistency

All previous named architecture objects and the complete floor program are preserved. The cliff-envelope records retain their bounds; their surface geometry is deliberately replaced. Main-villa and annex architectural source modules are unchanged. The villa extract now includes new decoration, so its file hash intentionally differs from the prior extract.

The four outdoor furniture envelopes are sourced from `atmosphere.LANDSCAPE_FURNITURE` by the model, arrival plan and circulation checker. Garden seating is drawn in brown on `plan-arrival.png` / `.svg`; the other three plan sheets retain their layouts. The planting itself is shown in the rendered views. New furniture does not overlap the existing furniture or one another. Circulation includes its footprints and the cypress footprints, keeps public routes outside private rooms, and checks the four clear strips around the pool.

Climbers are placed on solid facade piers with exclusion margins around declared windows and doors. Pergola canopies sit above the existing beams. Balustrades and stair lamps mount on existing guards/parapets. Balcony troughs and trailing plants sit along the outer rails. No new seating is placed at the exposed front of the pool deck.

## Review files

- `blockout-concept.png`: overall planted hotel.
- `blockout-front.png`: flowering elevations, terrace railings and aligned stair.
- `blockout-plan.png`: building footprints, pergola canopies, pool and outdoor furniture.
- `blockout-rear.png`: rear view and unchanged building placement.
- `plan-arrival.png` / `.svg`: courtyard plan including the new garden furniture.
- `plan-cottage`, `plan-guest-floor`, `plan-services`: interior layout sheets in PNG and SVG.
- `blockout.ldr`: the actual triangle mesh used for these renders.
- `verification.json`: export, layout, circulation and image-provenance checks.
- `donor-candidates.json`: retained interior donor candidates with current local-data hashes; no stock allocation.

`reference-concept.png` is included in the review ZIP. The package includes the generator sources and a per-file hash manifest.

## Verification limits

The deterministic exporter rejects non-finite and degenerate triangles. Checks cover full baseline program equality, preservation of named architecture, new landscape furniture envelopes, 57 navigation destinations, the pool loop, whole-scene bounds, roof separation and current image/plan provenance.

Navigation uses a half-stud floor grid and declared stair connections. It does not simulate door swings, people, every leaf projection or structural loads. Plants, furniture, roof tiles, arches and rockwork are authored proxy meshes. Glazing and lanterns are colored opaque surfaces. Actual LEGO parts, quantities, connections, support engineering and physical assembly remain later work. No donor pieces have been reserved.

## Reproduction

Use `/private/tmp/fern-steam-py/bin/python` to run `donors.py`, `build.py`, `plans.py` and `check_layout.py`. Render `concept` with `render.py --view concept --samples 128 --width 1600`; render `front`, `plan`, `rear` at 48 samples / 1200 px. Then run `verify.py`.

Requires Mitsuba CPU, the repository's `data/mocs/fern-and-steam-v2/render_model.py` helper, local donor data and the preserved `hotel-exteriors-v1` baseline. All review images come from the actual exported geometry.
