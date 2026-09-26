# Hotel Room Layout Implementation Plan

**Goal:** Revise the accepted composition into a coherent minifigure-scale hotel plan matching the user's room, garden, service and circulation requirements.

**Architecture:** A single structured layout defines floor plates, perimeter and partition walls, door/window openings, rooms and stair shafts. The 3D proxy model and annotated plan drawings both consume it. Navigation checks use the floor geometry and door openings, not a manually declared room adjacency graph.

**Tech Stack:** Existing Python/NumPy/Mitsuba environment; native SVG plan drawings.

**Spec:** User's latest review: straight exterior stairs; two rooms per upper floor in the long L arm (one balcony, one without); one extended balcony room in the horizontal arm; lobby/front desk on the ground floor; common side garden; garden cottage; separate descending dining/salon/spa building; a shared access route and usable pool surrounds.

## Constraints and assumptions

- Continue the composition/planning checkpoint, without presenting proxy geometry as a verified LEGO assembly.
- Main villa: ground-floor lobby plus two guest floors, each containing exactly three guest rooms. Six main-villa rooms plus one cottage.
- Keep the genuine L outline; author its perimeter once, eliminating overlaid complete building shells.
- Main and service stair cores must fit within explicit floor openings and link public corridors.
- Keep the cottage garden outside the shared through-route.
- Straight exterior stair flights share the same x coordinates and width, with consistent rises and treads.
- Pool deck includes a continuous circulation strip and separate lounger bays.
- Prior studies remain preserved.

## Work

- [x] Define `blockout-v3/layout.py`: room program, floor plates, walls, openings, balcony and service levels.
- [x] Author `build.py` from that layout, with straight exterior stairs, stair cores, explicit door openings and pool furniture envelopes.
- [x] Generate annotated site, guest-floor and service-floor SVG plans from the same layout.
- [x] Render and inspect exterior, front and overhead views; inspect floor plans against the model.
- [x] Check room counts, door/corridor connectivity, stair alignment, terrace continuity, opening widths, deterministic export and render provenance.
- [x] Deliver this planning revision with its remaining construction limitations stated plainly.
