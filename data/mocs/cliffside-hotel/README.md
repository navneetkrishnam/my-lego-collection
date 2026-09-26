# Cliffside Hotel — 2,188-piece digital build draft

Open **[guide.html](guide.html)** for the actual front/rear renders, searchable
picking list, donor allocations and every placement. Import
**[cliffside-hotel.ldr](cliffside-hotel.ldr)** into Studio to inspect the full model.
Keep the guide beside its images and evidence folder, or extract the whole ZIP.

The model occupies **48 × 40 studs (38.4 × 32 cm)** and uses **218 exact element
IDs** across **18 assembly stages**. It has a three-storey main building, a
two-storey guest wing, connecting pavilion, balconies, furnished rooms, a raised
pool terrace, straight stairs and stone outcrops. All tracked sets were eligible
donors; the tracker and previous cafe designs were not modified or reserved.

## What has been checked

- Deterministic authoring: a second run produces identical model JSON, LDraw,
  bill of materials and donor allocation files.
- Each placement is represented once in the BOM, and each required piece is
  allocated to an owned donor copy without exceeding that donor's allowance.
- No duplicate placements, ordinary-body overlaps or invalid transforms were
  found. The modeled stud/bar/clip connector graph has one connected component.
- Actual recursive LDraw mesh bounds were checked. The targeted mesh probe
  checks special parts and tilted instances against nearby parts. No unresolved
  strict surface crossings remain. Contacts inside matching stud and clip grip
  envelopes are identified separately in the report.
- Both previews use the exported model's exact geometry; their metadata records
  the model hash and hashes of the 220 LDraw dependency files. Neither preview
  is a new AI interpretation of the model.

See [verification.json](verification.json),
[geometry-verification.json](geometry-verification.json) and
[reproducibility.json](reproducibility.json) for the scope and evidence.

## What is still a prototype

**Physical build, rigidity, hinge friction, load capacity and assembly access
have not been tested.** The guide provides coordinate stages, not conventional
one-piece illustrated LEGO instructions. Build a roof assembly and a balcony
as physical prototypes before undertaking the complete model.

The mesh probe excludes coplanar contact and full containment. The attachment
graph establishes modeled connector positions, not structural strength. The
pitched roofs use free-angle bar/clip connections at a proposed 30 degrees.
The floor slabs and cornices require care when lifting the model; removable
floor handling is not mechanically certified.

The donor allocation is conditional on complete, accessible donor sets and
correct cached membership. It currently spreads picking across 131 sets under
the conservative allowance; this is **not a minimum-donor optimization**. More
complete per-set counts could substantially reduce the number of donors needed.

## Inventory evidence

The snapshot deduplicates exact element IDs within each owned donor copy. Its
default allowance is one piece per matching donor copy, not an inferred full
set inventory. Selected counts from official LEGO inventories replace that
allowance. They never add the printed quantity on top of the membership count.
Shape/colour aliases are not pooled together.

- [21341 instructions](https://www.lego.com/en-us/service/building-instructions/21341),
  printed inventory pages 259–262.
- [21353 instructions](https://www.lego.com/en-us/service/building-instructions/21353),
  printed inventory page 390.
- [42670 instructions](https://www.lego.com/en-us/service/building-instructions/42670),
  printed inventory page 322.

The rendered evidence pages, exact quantities and source PDF hashes are retained
in `evidence/` and `verified-donor-quantities.json`. The selected counts were
cross-checked against PDF text as well as visually inspected. The full PDFs
are not bundled.

## Relationship to the approved concept

The AI concept image is retained as `concept-approved.png`. The build draft is
visibly simpler: white/tan walls, brown roofs, straight stairs, restrained
planting and smaller stonework. It preserves the stepped architecture, terraces,
balconies and pool. It does not literally reproduce the concept's orange roof
tiles, ornate arched windows, shutters, perimeter balustrades or winding stairs.
Review the actual preview when deciding on further aesthetic changes.

## Reproduce in the repository

Run from the repo root, with Python 3.12+, numpy, Pillow and Mitsuba. PDF source
audits additionally use PyMuPDF. The local Studio catalog and LDraw library are
required at `/Applications/Studio 2.0`; the snapshot records their source hashes.

```sh
python data/mocs/cliffside-hotel/catalog.py
python data/mocs/cliffside-hotel/model.py
python -m unittest discover -s data/mocs/cliffside-hotel
python data/mocs/cliffside-hotel/audit.py
python data/mocs/cliffside-hotel/probe_geometry.py
python data/mocs/fern-and-steam-v2/render_model.py --input data/mocs/cliffside-hotel/cliffside-hotel.ldr --output data/mocs/cliffside-hotel/preview.png --samples 128
python data/mocs/fern-and-steam-v2/render_model.py --input data/mocs/cliffside-hotel/cliffside-hotel.ldr --output data/mocs/cliffside-hotel/preview-rear.png --samples 128 --rear
python data/mocs/cliffside-hotel/verify_package.py
python data/mocs/cliffside-hotel/make_guide.py
```

The working render path uses Mitsuba's CPU renderer. Do not use the crashing
Eyesight installation for this package. The existing cafe renderer supplies a
small missing LDraw primitive through its `ldraw/` fallback; its attribution is
retained there. Source scripts stay in the repository; the review ZIP contains
the model, guide, reports and evidence.

The guide was checked for data completeness, local links, JavaScript syntax,
filtering and pagination. A browser UI was unavailable for a visual guide check.
The model's front and rear images were visually inspected.
