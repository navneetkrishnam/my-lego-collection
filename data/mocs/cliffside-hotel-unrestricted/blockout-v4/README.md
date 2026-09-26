# Cliffside Hotel — enlarged cottage and donor-aware services, v4

This revision implements the user's cottage, corridor-window and donor-reuse changes to the accepted room-programmed v3. The geometry is an architectural proxy, not an assembly of verified LEGO parts. Earlier revisions remain preserved.

## Changes for review

| Area | Revised arrangement |
|---|---|
| Cottage 01 | 32 × 28 stud footprint (896 square studs), up from 16 × 20 (320). A public lounge/library occupies the west half; a private guest bedroom with ensuite occupies the east half. A front foyer has independent doors to both. |
| Main-villa ground floor | Reception and lobby stay in the long arm, with direct common-garden access. The former library becomes hotel office/luggage space. |
| Main-villa corridor | Two 3-stud-wide pool-facing window openings on each of the three floors, between the stair core and courtyard: six new windows total. |
| Service wing | Deepened from 30 × 30 to 30 × 38 studs. The stair location, courtyard entrance and three floor levels stay aligned. |
| Dining at +40 | Two four-seat tables, kitchen/pantry with island, and a bar counter. Eight seats are shown; a full-occupancy banquet is not assumed. |
| Salon at +26 | Two 4 × 4 styling-chair envelopes, mirror counter, a separate 4 × 4 wash-station envelope and a waiting/lounge area opening to the arcade. |
| Spa at +12 | Two treatment rooms, larger changing/shower and relaxation zones. Furniture will be custom built using candidate donor taps, tiles and ordinary structural elements. |

The main villa still contains six guest rooms: on each upper floor, one long-arm room without a balcony, one long-arm room with a balcony, and an extended suite in the horizontal arm with its own balcony. Cottage 01 remains the seventh guest accommodation, now sharing its larger building with a public library. No public library route crosses its bedroom.

The cottage is shifted two studs east as it grows. Its roof has a one-stud horizontal clearance from the main roof, and a one-stud plan clearance from the service roof. The front porch is four studs deep; the garden pergola moves forward, leaving the public entry clear. The shared promenade to the restaurant remains outside the cottage. The cottage foundation and the service plinth extend beneath the enlarged footprints.

The main side garden, aligned exterior stairs, pool and its continuous walking loop retain their previous arrangement. The base remains 128 × 114 studs (102.4 × 91.2 cm at physical stud scale).

## Owned sets and reuse strategy

See `donor-reuse.md` for the proposal and `donor-candidates.json` for local ownership, element IDs and source hashes. Confirmed owned candidates include 42655, 42691, 42662, 41743 and 10362. All owned sets remain eligible donors; these five are the most relevant starting candidates for this revision.

Reuse furniture ideas and individual pieces inside a consistent cream/terracotta hotel exterior. The original restaurant/salon facades do not determine the hotel shape. The interior blocks reserve space for future assemblies; they are not imported donor submodels or dimensionally verified copies. Exact quantities and competition for the same piece across rooms remain to be resolved when generating an actual part-level bill of materials.

## Drawings

- `blockout-concept.png`: updated overall composition.
- `blockout-front.png`: straight stairs, corridor windows and descending services.
- `blockout-plan.png`: enlarged roof footprints and surrounding space.
- `blockout-rear.png`: cottage scale and rear building arrangement.
- `plan-arrival.png` / `.svg`: the public library, private bedroom, reception, gardens, promenade, dining and pool.
- `plan-guest-floor.png` / `.svg`: guest-room separation and new corridor windows.
- `plan-services.png` / `.svg`: dining, salon and spa arrangements.

## Verification and limits

The 0.5-stud navigation grid is derived from floor plates, walls and actual doorway gaps. Floor holes, furniture and pergola posts are excluded. Stair landing nodes link floors. All 50 destinations must be reachable. A second traversal closes bedrooms, bathrooms, offices/kitchen and treatment rooms: all stair landings plus the public cottage foyer and library must remain reachable. The cottage garden is now a public library approach, while the separate promenade carries through traffic.

Additional checks cover deterministic export, the seven-room program, six added corridor windows, larger cottage/service footprints, eight dining chairs, furniture-envelope collisions, cottage roof separation, stair alignment, pool-support and balcony-support envelopes, shaft locations and donor-source freshness. Image hashes tie the four rendered views and three plan sheets to their current sources. Run `verify.py` to regenerate `verification.json`.

These checks verify this planning model. They do not prove LEGO connection strength, part availability in sufficient quantities, door swings, exact donor-module fit, full body-width navigation, accessible circulation, structural stability or real-building compliance. The solid rock volumes indicate support regions; the eventual LEGO structure must use a designed modular frame. No spa set or new parts purchase is assumed, and no inventory is reserved.

## Reproduction

From this directory, using the existing `/private/tmp/fern-steam-py/bin/python` environment, run `donors.py`, `build.py`, `plans.py`, and `check_layout.py`. Render with `render.py --view concept --samples 128 --width 1600`, then `front`, `plan` and `rear` with `--samples 48 --width 1200`. Finally run `verify.py`.

Rendering uses the repo's `data/mocs/fern-and-steam-v2/render_model.py` helper and Mitsuba CPU. The review ZIP is an artifact snapshot; reproduction also requires that repository helper and the Python dependencies. No Eyesight render is involved.

Next checkpoint: accept the space allocation, then translate one room/furniture module at a time into real donor-compatible LEGO assemblies before dressing the whole facade.
