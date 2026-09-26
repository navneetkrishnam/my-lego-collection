# Cliffside Hotel Composition Study Implementation Plan

**Goal:** Produce the user-approved first step: a dimensioned architectural blockout that can be compared with the approved concept before detailed LEGO design.

**Architecture:** An independent procedural massing model exports plain LDraw triangle geometry and a dimension schedule. Mitsuba renders that geometry with consistent lighting and a front-left camera approximating the concept. This is a composition study, not an inventory or connection-verified model.

**Tech Stack:** Existing local Python environment, NumPy, Mitsuba, existing LDraw mesh utilities.

**Spec:** User-approved composition in conversation: broader three-storey villa, visible recessed connector, substantial lower two-storey wing with arcade, broad pool terrace, deep irregular cliff envelope and long descending staircase.

## Global constraints

- Piece count and inventory unrestricted for this exploration.
- Work only on step 1: composition, roof silhouettes, major openings, circulation and terrain envelopes.
- Preserve all preceding versions.
- No claim that illustration details are already translated into LEGO connections.
- No new generated concept image: review the geometry we actually author.

## Task 1: Author dimensional blockout

- [x] Create `data/mocs/cliffside-hotel-unrestricted/blockout/build.py` with boxes, polygon prisms, hipped roofs, major openings and a stepped stair volume.
- [x] Export `blockout.ldr` and `dimensions.json`. Use a provisional 96 × 88 stud base, terrace height 40 studs, a 40 × 28 stud main villa with 42 stud wall height, an 18 × 18 stud connector with 27 stud wall height, and a 28 × 26 stud wing with 28 stud wall height.
- [x] Use terracotta roof massing, warm pale walls and neutral grey cliff envelopes. No foliage, furniture or roof tile detailing.

## Task 2: Render and review

- [x] Create `render.py` reusing existing mesh utilities; render front-left, front, rear and top views from the same authored geometry.
- [x] Inspect front-left beside original concept; check building hierarchy, visibility of connector, open pool terrace and coherent stair route. Adjust major dimensions if inspection reveals occlusion or an imbalance.
- [x] Save input hashes with render metadata; verify deterministic regeneration and geometry finiteness/nondegenerate triangles.
- [x] Write a concise README with provisional dimensions, scope and next review decision. Deliver actual blockout image plus concept link, stopping at this composition checkpoint.

## Review outcome

First-view inspection led to a taller, more exposed 16 × 22 × 32 stud connector and raising the right wing floor to the pool terrace level. Side openings, balcony slab envelopes and a deeper stair landing were added. Deliverables remain geometry proxies; the rear facade and LEGO connections are unresolved by design at this checkpoint.

## User-directed composition revision 2

The user requested a true L-shaped villa, the villa garden along its outer side, and a multi-storey right wing extending below courtyard level. This is a revision of the current composition checkpoint, not a transition to detailed facade design.

- [x] Preserve revision 1 and author `blockout-v2/` with separate source and renders.
- [x] Join a 36 × 22 rear villa bar to a 16 × 15 forward return with a continuous L-shaped roof envelope.
- [x] Relocate the villa pergola and planting to x=3..22, beside the villa.
- [x] Set the right wing floors at 12, 26 and 40 studs, with the main courtyard at 40. Expose the lower floors by removing the high terrain under its footprint and moving it forward/outward beside the pool.
- [x] Add assertions checking the L recess, garden placement and lack of high terrain occupying the lower wing.
- [x] Render the four final views, inspect their geometry and verify provenance before handing back this revision.
