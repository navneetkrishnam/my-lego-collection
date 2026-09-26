# Fern & Steam artifact plan

**Goal:** Deliver a reproducible first custom model and an illustrated build
package under the approved all-sets donor assumption.

**Design:** `DESIGN.md`. This is model/artifact creation, not a tracker feature.

1. [x] Implement the conservative inventory and simplified structural verifier in
   `verify.py`, with small adversarial tests in `test_verify.py`: duplicate rows,
   multiple boxes, unknown IDs, shortages, collisions, floating pieces, pieces
   resting on tiles, disconnected foundations and blocked downward placement.
   Run `python3 -m unittest discover -s data/mocs/fern-and-steam -p 'test_*.py'`.
2. [x] Author `model.py` with an explicit part mapping and ordered construction.
   Export `model.json`, `fern-and-steam.ldr`, `inventory-snapshot.json`,
   `bom.json`, `picking-list.md`, and `verification.json`. Adapt the design until
   its quantities and the declared structural checks pass. Record hashes.
3. [x] Author `make_guide.py` to draw model-derived isometric/top-down schematics
   and a complete placement appendix in `output/pdf/fern-and-steam-build-guide.pdf`.
   Render every page, inspect the images and fix layout issues before delivery.
4. [x] Independently reconcile the LDraw export with model instances and BOM;
   regenerate and compare artifact hashes. Run the existing inventory tests.
   Deliver links and clearly distinguish passed checks from physical review.
