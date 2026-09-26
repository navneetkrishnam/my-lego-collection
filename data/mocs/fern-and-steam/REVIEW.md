# Revision 1 review record

## Independent checks completed

- Exact source memberships, ownership multipliers, and frozen input hashes were
  reconciled against the current repo at creation.
- The 115 model instances, 25-ID BOM, LDraw export and 26-donor allocation agree.
- No allocation takes more than one of an element from a given set copy.
- Ten automated tests pass, including duplicate-row handling, shortages,
  unsupported placements, disconnected foundations, blocking overhead parts,
  and the accessory contact regressions below.
- All five existing tracker inventory tests pass.
- Model, BOM, allocation, verification report, preview and PDF reproduce
  byte-identically on consecutive runs in the recorded authoring environment.
- All 18 PDF pages were rendered and visually reviewed. All 115 ordered
  placement IDs appear exactly once in the step tables. No extracted text
  bounds extend outside a page.

## Corrected before delivery

1. A rear-facing leaf tip intersected the right bench leg. The low plant was
   moved forward, and its neighboring front plant moved farther forward to
   maintain spacing. Inspection of official 32607 geometry found the seven
   leaf outlines within the base, no overlapping leaf XY bounding boxes, and
   no remaining leaf vertex inside the furniture or walls.
2. The counter mug handle intersected its white trim. It now points rearward.
3. The table mug handle intersected a neighboring stud. It also points rearward.
4. The flower color label now says Bright Pink (LDraw 29), equivalent to the
   source's LEGO Light Purple, instead of the different color Light Pink.
5. The illustration renderer now uses a per-pixel depth buffer, avoiding
   incorrect occlusion from sorting entire plate faces by their centers.

## Remaining limits

The completed model has not been physically assembled or fully checked in a
fine-mesh CAD collision engine. Mesh-vertex review is not proof of complete
mesh nonintersection. The leaf geometry extends approximately 0.3 LDU (0.12 mm)
below its simplified mounting plane; exact decorative mounting/clutch remains
for a trial build. Stability, strength, printed/mold equivalence and physical
inventory counts remain unverified. The PDF labels the model accordingly.

Geometry references:

- https://library.ldraw.org/library/official/parts/32607.dat
- https://library.ldraw.org/library/official/parts/s/3899s01.dat
- https://ldraw.org/parts/colour.html
