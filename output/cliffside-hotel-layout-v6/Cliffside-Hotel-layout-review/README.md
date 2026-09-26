# Hotel layout v6 — two-storey cottage and revised pool seating

This revision applies the user's request for a two-floor cottage and a larger pool with seating between the water and the service building. It also corrects the weak garden representation identified during the preceding review. Existing building positions and footprints are retained.

## Cottage 01

Cottage 01 remains one private accommodation, now spanning levels +40 and +54 within its 44 × 28 stud footprint. The main villa still has six guest rooms, giving seven accommodations in total.

- **Ground floor:** retained foyer and private garden entry; sitting room, a small dining nook and bathroom.
- **First floor:** bedroom, dressing area and bathroom. The seven-stud-wide front window at x86–93 is above and faces the private garden, whose footprint is x80–96 / y36–46.
- **Private stair:** an internal U-stair at x104 / y9 links both floors. Its 35 plate-height risers fit the 14-stud floor separation; the upper slab has a matching 10 × 12 stud opening with a landing beyond it.
- **Roof:** raised to the second-storey wall head, beginning at +68.5. Its plan footprint is unchanged; its right edge still aligns with the service roof.

The two storeys are one suite, not two independently bookable rooms. The plan and navigation model distinguish private cottage circulation from public hotel routes. Cottage ground-level windows were adjusted around the new stair core.

## Pool and seating

The water area grows from **22 × 12 to 22 × 16 studs**, an increase of one-third, by extending in depth and shifting four studs left. The outer pool-deck footprint remains 38 × 34 studs.

Two loungers occupy x89–95 at y63–67 and y72–76, next to the service building's x96 wall. They face west toward the pool. A small table sits between them. The service entrance and its approach remain unobstructed.

A four-stud walking strip runs between the water's coping and the seating area. There are three clear studs along the left side and 7.5 behind the pool. The nine-stud strip between the front coping and the cliff-facing guard has no seating. The nearest lounger ends 11.5 studs before that front guard. The existing edge guards remain; this layout moves the furniture away from the exposed end of the deck as requested.

These are explicit spatial setbacks in the model, not a safety certification or a test of LEGO guard strength.

## Garden consistency

The garden's reserved footprint remains 16 × 10 studs. A visible 10 × 6 lawn beneath the pergola and a low front planting bed now make it recognizable in 3D. The garden entry path and public promenade remain separate. The pergola footprints are drawn in the plans and read from the same layout schedule by the model and navigation checker. Lawn surfaces likewise feed both the plan and model.

The plan's pale garden tint denotes the overall garden zone; the darker green rectangle is the modeled lawn. This makes the difference between reserved garden area and actual planting explicit.

## Preserved work

The main villa's three floor programs and exterior detail objects are unchanged from `villa-exterior-v1`. The dining, salon and spa floor programs remain unchanged. The straight exterior stair, main side garden, cottage/service right-edge alignment and overall 128 × 114 stud base are retained. The main villa is detailed; cottage and service facades are still architectural blockouts.

## Review files

- `blockout-concept.png`: overall hotel, two-storey cottage, garden and pool arrangement.
- `blockout-front.png`: storey heights, window above the cottage garden and straight stair.
- `blockout-plan.png`: roof footprints, larger pool and seating beside services.
- `blockout-rear.png`: raised cottage roof and unchanged building positions.
- `plan-arrival.png` / `.svg`: ground-floor routes, visible garden, pool and seating.
- `plan-cottage.png` / `.svg`: both private cottage floors and aligned stair opening.
- `plan-guest-floor.png` / `.svg`: main-villa guest floor, retained.
- `plan-services.png` / `.svg`: service rooms, retained.

## Verification scope

The model exports deterministically. Checks cover 57 planning destinations, a public route to the villa library and all service landings without entering the cottage/garden, the new private stair and upper-floor opening, garden-facing window location, matching garden surfaces, pool geometry, seating placement, furniture-envelope collisions, clear walking strips, support envelopes, unchanged main/service floor definitions and unchanged villa exterior objects. Source and image hashes tie the four rendered views and four plan sheets to this revision.

This remains a proxy study. Navigation uses a 0.5-stud grid with declared stair links and operable doors; it does not simulate people, door movement or every decorative surface. Actual LEGO parts, connections, load capacity, stair headroom, guard strength and donor quantities require construction-level work. The existing donor list remains a set of candidates; no pieces have been reserved.

## Reproduce

With `/private/tmp/fern-steam-py/bin/python`, run `donors.py`, `build.py`, `plans.py` and `check_layout.py`. Render `concept` at 1600 px / 128 samples and `front`, `plan`, `rear` at 1200 px / 48 samples, then run `verify.py`.

Mitsuba CPU, the repository helper `data/mocs/fern-and-steam-v2/render_model.py`, local donor data and the previous `villa-exterior-v1` export are required. `villa-detail.ldr` is also regenerated as an auxiliary geometry extract, but the four full-hotel views and the two-floor cottage plan are the review deliverables for this revision. Prior versions are preserved.
