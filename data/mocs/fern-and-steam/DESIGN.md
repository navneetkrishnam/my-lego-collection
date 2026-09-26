# Fern & Steam / revision 1

An original 16 x 16-stud garden tea kiosk designed for this collection. All
owned sets are eligible donors, as authorized in the conversation. The palette
is white, tan, reddish brown and light grey, with green foliage, pink/coral
flowers and yellow mugs. The scene contains a reinforced base, a stepped path,
an open tea counter, a low back wall, a four-post pergola, a bench, a small table
and planting. Figures are not included.

## Inventory contract

Use `data/owned-sets.csv` and `public/data/parts/<set>.json`. Count each exact,
non-null element ID once per owned set copy. Duplicate rows in one set never
increase the budget. Do not pool different IDs by name, substitute colors,
assume unrecorded quantities or use unidentified rows. All counts assume
complete, accessible sets and no previous reservations. Color metadata comes
from the existing enrichment cache and is recorded as such, not physically
verified. Choose explicit LDraw references; record their source and assumptions.

## Deliverables and construction checks

- A deterministic instance list with stud coordinates, plate-unit elevations,
  exact element IDs and step numbers; LDraw export and an exact BOM derived
  from that list.
- A frozen inventory snapshot for used IDs, input hashes, and a picking
  allocation that never takes more than one of an ID from any set copy.
- Structural checks for solid-body overlap, bounds, stud support, final
  connectivity and clear vertical placement in the stated build sequence.
  Checks use explicit simplified geometry, not a general LEGO CAD solver.
- Decorative leaf, flower and cup connections receive explicit mounting rules;
  their detailed meshes and clutch/stability remain manual-review items.
- A PDF with an actual model-derived schematic, part keys, numbered steps,
  a coordinate placement appendix and verification limitations.

Physical build, stability, fine collision checking and visual confirmation of
element-to-LDraw mappings remain pending. The initial model is an inventory-
checked prototype, never described as physically verified.

## Reproduction

The model is independent of the tracker UI. Its generator, verifier and tests
live beside the artifacts. Regeneration is offline from the captured source
data; refreshing inventory is an explicit action. No existing model is edited.
