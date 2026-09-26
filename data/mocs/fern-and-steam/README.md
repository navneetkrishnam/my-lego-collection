> Superseded schematic prototype. Later actual-mesh review found incorrect local axes for several rectangular parts and accessory mounting heights. Do not use this revision as physical build instructions; use the [Courtyard Edition](../fern-and-steam-v2/README.md) for further development.

# Fern & Steam

An original **115-piece, 16 x 16-stud garden tea kiosk**, designed from the
conservative inventory of this LEGO collection. All owned sets are eligible
donors. This is revision 1, an **inventory-checked prototype**, not a physically
verified build. The model is approximately 12.8 x 12.8 cm in footprint.

Start with `output/pdf/fern-and-steam-build-guide.pdf` at the repository root.
The guide has 18 pages: a model-derived preview, verification scope, coordinate
legend, an exact-ID parts palette, 12 illustrated construction steps and a
physical test record. Its illustrations are assembly schematics with simplified
decorative shapes; they are not screenshots from a CAD fine-collision check.

## Files

- `fern-and-steam.ldr`: editable LDraw model with ordered STEP markers.
- `preview.png`: a schematic of the actual saved model.
- `picking-list.md`: exact quantities and a deterministic allocation by donor.
- `model.json`: every piece's exact element ID, coordinates and orientation.
- `bom.json`: bill of materials derived from model instances.
- `inventory-snapshot.json`: frozen lower-bound counts, source set copies,
  raw-source hashes and source color/name metadata for the used elements.
- `part-map.json`: explicitly selected element-to-LDraw geometry/color mapping.
- `allocation.json`: at most one of an ID picked from each set copy.
- `verification.json`: structural/inventory checks and artifact hashes.

The conservative allocation spans **26 donor sets**. It is not claimed to
minimize the number of donor sets, and actual per-set counts may allow a much
smaller picking session. Do not silently treat additional quantities as verified.

## What passed, and what remains

The 115 instances use 25 exact IDs with zero conservative shortages. The
simplified checks found zero overlapping structural boxes, zero unsupported
placements, zero out-of-bounds structural footprints, and no earlier structural
box blocking the stated downward insertion order. Their final connection graph
contains one assembly. Ten tests cover the core rules and reviewed accessory contacts;
`audit.py` independently reconciles the exports and donor allocation.

These checks assume complete, accessible sets, no previous reservations, and
correct source membership. They do not confirm physical inventory. The
element-to-LDraw mapping and cached color metadata were selected/reviewed for
this model and still need visual confirmation. LDraw 29 Bright Pink corresponds
to the source's LEGO Light Purple; LDraw 2 Green corresponds to LEGO Dark Green.

Fifteen leaf/flower/mug instances use simplified mounting geometry. An independent
review identified a leaf/bench intersection and a mug/trim intersection in an
earlier draft; the leaf was moved and both mugs rotated rearward. The table mug
also needed this turn to keep its handle clear of the adjacent stud. Fine
mesh collisions across the complete model, clutch, strength, stability and
physical assembly remain **not tested**. Never force a connection. Build on a
flat surface and finish the two-layer base before lifting it.

## Reproduce without network access

From the repository root, using Python 3:

```sh
python3 -m unittest discover -s data/mocs/fern-and-steam -p 'test_*.py'
python3 data/mocs/fern-and-steam/model.py
python3 data/mocs/fern-and-steam/audit.py
```

The generator uses the frozen inventory snapshot by default. To deliberately
capture current tracker data, use `model.py --refresh-inventory`; this replaces
the previous snapshot and its assumptions and should be treated as a new audit.

To regenerate the PDF, install `requirements-guide.txt` in a separate virtual
environment, then run `python data/mocs/fern-and-steam/make_guide.py`. PDF creation
uses ReportLab; rendering uses PyMuPDF. It writes final PDF output under
`output/pdf/` and QA images under `tmp/pdfs/fern-and-steam/`.

## References

- [LDraw model format](https://www.ldraw.org/article/218.html).
- [LDraw color reference](https://ldraw.org/parts/colour.html).
- [Official three-leaf geometry](https://library.ldraw.org/library/official/parts/32607.dat).
- [Official flower geometry](https://library.ldraw.org/library/official/parts/24866.dat).
- [Official cup geometry](https://library.ldraw.org/library/official/parts/3899.dat).

Each rectangular geometry URL is recorded in `part-map.json`. The model refers
to official library parts; it does not bundle or modify the LDraw part library.
