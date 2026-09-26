# Digital review record

Reviewed 2026-09-11 against the exact generated instances and recursive Studio
LDraw geometry. No physical build or full solid collision certification.

## Corrections made

1. **Rectangular part axes:** Actual standard LDraw bricks and plates run their
   long dimension along local X. The old schematic assumed local Z. Revision 2
   uses the correct transforms; the actual mesh footprint audit passes.
2. **Accessory mounting heights:** 32607 leaves and 24866 flowers have an
   8-LDU mounting height in this geometry; 3899 mugs use 24 LDU. Origins now use
   those body bottoms, rather than the thinner decorative surfaces.
3. **Plant identity:** Element 6447541 maps to `2682a.dat`. `2682.dat` is an
   unrelated monorail switch in the installed library.
4. **Plant clashes:** A targeted edge/triangle probe detected 23 accessory pair
   crossings, including leaves through window frames. Plant rotations and
   positions were adjusted on existing planter studs, retaining the BOM.
   Rechecking the final 54 nearby pairs finds no strict surface crossings.
5. **Inventory:** Hidden base plates and planter bricks were reassigned to
   available exact elements. The combined BOM has no conservative shortages.
6. **Assembly access:** The cafe counter precedes the arches and roof. Window
   inserts precede the cornice. Roof notes identify the rail subassembly.
7. **Rendering:** Full front/rear framing is checked. The preview is generated
   from 264,936 actual triangles. Step meshes use distinct cache keys to avoid
   replacing a full-model mesh with a partial assembly during concurrent work.

## Evidence

- `verification.json`: inventory, ordinary body boxes, insert poses and stud
  graph. Six focused tests cover disconnection, tile attachment, seam bridging,
  shortages, ordinary collisions, half-stud offsets and displaced inserts.
- `geometry-verification.json`: all 337 non-insert body bottoms and the regular
  mesh footprints agree with authored dimensions.
- `accessory-geometry-review.json`: targeted leaf/flower/fern/mug crossings.
- `preview.render.json` and `rear.render.json`: model and library provenance.
- Architecture and roof research documents: exact identity and connection
  offsets, with catalog and geometry references.

## Limits

Mesh bounds do not establish collision freedom. Strict triangle-edge tests
miss coplanar contacts and containment. The graph does not test clutch force,
load or an actual builder's access. Transparent panes use canonical catalog
representations with documented minor mold/tolerance differences. A trial
physical assembly and Studio's full model checks remain the next verification
stage.
