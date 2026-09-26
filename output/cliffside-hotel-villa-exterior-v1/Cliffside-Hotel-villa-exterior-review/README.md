# Main villa — exterior appearance study 1

The user's approved **blockout-v5** remains the source of the hotel layout. This checkpoint develops only the main villa's exterior against the original cliffside-hotel concept. It is a deterministic architectural proxy, not a LEGO parts assembly.

## Review

Start with **`villa-detail-villa.png`**, an isolated courtyard-side view that exposes the L recess, entrance, corridor windows and balconies. **`blockout-concept.png`** shows the same villa in the complete hotel. The cottage, service wing, terrain, pool and site remain at their approved blockout level.

| Reference feature | This pass |
|---|---|
| Warm cream masonry | Fine stone course joints, projecting corner stones and layered cornice details. |
| Green shutters and timber windows | Recessed glass-colored panes, wooden frames/transoms and individual green shutter slats. Shutters are omitted where adjacent openings leave insufficient wall space. |
| Detailed balconies | Main-villa placeholder rails replaced with dark slender rails and spindles, pale fascia trim and compact flower planters. Deck positions and sizes stay fixed. |
| Welcoming entrance | Stone jambs, an arched stone head, paired glazed timber door leaves and wall lanterns. |
| Terracotta roof | Individual barrel-shaped tile surfaces following the local roof fall, courses clipped to the existing eaves, ridge covers and two slender chimney envelopes. |

The concept has round-headed openings and more elaborate entrance columns. This pass preserves the approved rectangular opening schedule and places stone relieving arches above door lintels. It does not claim an exact copy of the concept. Doors are rendered closed as operable appearance elements; the circulation plan still assumes they can open. Glazing uses an opaque glass-colored proxy material, and the lanterns use a warm-colored material rather than a simulated electrical light.

The villa's masonry openings, room partitions, floors, stair shafts, cottage alignment, guest-room count and circulation routes are unchanged. Chimneys are architectural exterior envelopes; internal flues, fireplaces and actual roof penetrations have not yet been designed. Roof surface texture and balcony details are similarly appearance geometry awaiting a real LEGO construction solution.

## Scope preservation

`layout.py` is byte-for-byte identical to approved v5. `verify.py` compares the complete exported floor and room program to v5, then compares all non-detail objects to the v5 export. Only the main villa's old balcony rail objects are removed; all new objects have a `villa ` prefix. The new detail model is a deterministic spatial selection of the same authored geometry, not a separate imagined building.

The 50 existing floor-plan destinations, public access to the villa library and service stairs, and pool walking loop remain checked on the planning grid. Those navigation checks use the approved floor/door/furniture geometry; they do not simulate door motion or treat every decorative surface as a walking obstacle. No claim of LEGO connection strength or full collision-free physical assembly is made.

## Files

- `villa-detail-villa.png`: close review of the villa exterior from the courtyard side.
- `blockout-concept.png`, `blockout-front.png`, `blockout-plan.png`, `blockout-rear.png`: full-model views.
- `villa-detail.ldr`: isolated villa proxy mesh for the close view.
- `blockout.ldr`: full hotel proxy mesh.
- `plan-arrival.png`, `plan-guest-floor.png`, `plan-services.png` (also SVG): the preserved planning layout.
- `exterior.py`: deterministic villa facade, balcony and roof detail generator.
- `build.py`: composes the approved base geometry and main-villa details.
- `verification.json`: scoped layout preservation, geometry, donor-source and render-provenance checks.

The review ZIP also includes the original `reference-concept.png` for comparison. Donor candidates remain unchanged from v5; no actual part allocation or piece estimate has been made for this exterior study.

## Reproduce

Using `/private/tmp/fern-steam-py/bin/python`, run `donors.py`, `build.py`, `plans.py` and `check_layout.py`. Render `concept` at 1600 px / 128 samples; `front`, `plan`, `rear` at 1200 px / 48 samples. Render the close view with `render.py --model villa-detail --view villa --width 1600 --samples 128`. Then run `verify.py`.

Mitsuba CPU and the repository's `data/mocs/fern-and-steam-v2/render_model.py` helper are required. Reproduction of the preservation checks also requires the sibling approved `blockout-v5`. The review ZIP is an artifact snapshot, not a standalone tool installation.

After exterior review, the next checkpoint is to apply the chosen facade language to the other buildings, or revise the villa details first. Physical LEGO module design and donor quantity reconciliation remain subsequent work.
