# Cliffside Hotel — private cottage aligned with service wing, v5

This corrects v4 following the user's annotated plan. The lounge/library returns to the main villa's former hotel-office/luggage room. Cottage 01 is restored to one wholly private accommodation and extends east to the service building's right-hand wall. The foyer, private garden access, corridor windows and service layout are retained.

## Space allocation

| Area | v5 arrangement |
|---|---|
| Villa, courtyard level +40 | Reception/lobby and common side garden in the long arm; public lounge/library in the horizontal arm. Back office and common WC remain in their existing positions. |
| Cottage 01, +40 | One 44 × 28 stud building, x82–126 and y8–36. The full 42 × 21 stud interior behind the foyer belongs to the private accommodation, including its sitting and sleeping areas and ensuite. |
| Cottage foyer | Extends across the interior frontage, 42 × 4 studs, with garden-facing entry and doors into the private accommodation. |
| Cottage garden | Retained in front of the cottage, with the same pergola and garden approach. Public through-traffic uses the separate promenade. |
| Service wing | 30 × 38 studs, x96–126. Dining/kitchen at +40, salon/lounge at +26, spa/changing at +12. |

The cottage has no public lounge/library and no partition dividing a public library from a reduced bedroom. The sitting and sleeping furniture occupy one open private room; the bathroom and foyer retain their own walls. There are still six main-villa guest rooms plus Cottage 01.

The **right-hand exterior wall faces of cottage and service building both end at x126** (wall centreline x125.5). Their right-hand roof eaves both end at x127.5. This follows the red alignment line in the user's plan; the two buildings do not have equal widths because the cottage starts farther left. Cottage width grows from 32 to 44 studs, while its 28-stud depth remains. Its foundation and front porch extend to the same new edge. A one-stud plan gap remains between the cottage and service roof eaves; a one-stud horizontal gap remains from the main-villa eastern eave.

The public library has a door from the main-villa common corridor. The blue route in `plan-arrival.png` now ends there. The brown route is the private garden/cottage approach. The right-hand brown alignment line marks the shared exterior wall extent. Moving the public library back to the villa restores private use of the cottage garden.

## Preserved service and outdoor scheme

The service building retains its eight dining seats, kitchen island and bar counter, two salon styling chairs, wash station, lower spa rooms and aligned public stair core. The six pool-facing main-villa corridor windows remain. Exterior stair flights remain straight and aligned. The pool and its clear walking loop retain their geometry. The base remains 128 × 114 studs (102.4 × 91.2 cm at physical stud scale).

`donor-reuse.md` and `donor-candidates.json` retain the restaurant/salon/spa-fittings proposal and local ownership/element evidence. Library book candidates now belong to the villa library. These remain candidate uses, with no claimed quantity allocation or intact donor-module fit.

## Review artifacts

- `plan-arrival.png` / `.svg`: corrected cottage, library location and access routes.
- `plan-guest-floor.png` / `.svg`: the unchanged three-room guest-floor layout and corridor windows.
- `plan-services.png` / `.svg`: retained service-room and furnishing arrangement.
- `blockout-concept.png`, `blockout-front.png`, `blockout-plan.png`, `blockout-rear.png`: four views rendered from the actual revised proxy geometry.
- `verification.json`: deterministic export, layout checks and artifact provenance.

## Verification scope

`check_layout.py` derives a navigation grid from the authored floor plates, walls, door gaps, furniture, pergola posts and shaft holes. All 50 destinations must remain reachable. A separate traversal closes guest rooms, private areas, bathrooms, office/kitchen, treatment rooms and the cottage garden. The villa library and all public stair landings must remain reachable without entering those areas. The four pool-circulation strips must remain clear.

`verify.py` additionally checks the public library's location, absence of a cottage library, private foyer dimensions, cottage footprint, matching cottage/service eastern wall and roof extents, seven-room program, corridor windows, furniture-envelope collisions, roof gaps, support envelopes, stair alignment and deterministic geometry. Current image and plan hashes tie the review drawings to their sources. Donor evidence is checked against the local ownership, catalog, parts and image files.

This is an architectural proxy, not a LEGO part-level assembly. The checks do not establish LEGO connection strength, exact donor quantities, full body-width navigation, door swings, structural stability or real-building compliance. Furniture and foundations are spatial/support envelopes awaiting actual LEGO design. No inventory has been reserved or edited.

## Reproduce

Use the existing `/private/tmp/fern-steam-py/bin/python` environment. Run `donors.py`, `build.py`, `plans.py` and `check_layout.py`; render `concept` at 1600 px / 128 samples and `front`, `plan`, `rear` at 1200 px / 48 samples; then run `verify.py`.

The renderer uses Mitsuba CPU and the repository helper `data/mocs/fern-and-steam-v2/render_model.py`. The ZIP is a review snapshot; those dependencies and the repository data are required for reproduction. Earlier studies remain in sibling folders, including `blockout-v4`.
