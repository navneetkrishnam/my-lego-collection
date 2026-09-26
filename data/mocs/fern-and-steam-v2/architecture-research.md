# Architectural part references for revision 2

Research checked 2026-09-11. Element IDs and colors are directly confirmed by the installed BrickLink Studio catalog, `/Applications/Studio 2.0/data/elementInfoList.json`; canonical geometry names are confirmed by `StudioPartDefinition2.txt`. These are primary BrickLink application data. Repo `public/data/parts-enrichment-cache.json` independently matches all listed colors.

| Owned element | Color / LDraw color | BrickLink part | Canonical LDraw geometry |
|---|---|---|---|
| 6249033 | White / 15 | 40066 | `40066.dat` |
| 6031098 | White / 15 | 6182 | `6182.dat` |
| 6031057 | Tan / 19 | 6182 | `6182.dat` |
| 6262945 | White / 15 | 60596 | `60596.dat` |
| 6514119 | Trans-Clear / 47 | 60616 | `60616a.dat` (Studio canonical representation; see mold caveat) |
| 4530590 | White / 15 | 60594 | `60594.dat` |
| 6514142 | Trans-Clear / 47 | 60603 | `86210.dat` (`60603.dat` is an identity alias) |
| 6256127 | White / 15 | 42205 | `42205.dat` |
| 6511024 | Trans-Clear / 47 | 42509 | `42509.dat` |

## Independent web references

- [BrickLink element 6249033 → arch frame 40066](https://www.bricklink.com/v2/catalog/catalogitem.page?ccName=6249033&id=172802&idColor=1) and [official LDraw geometry](https://library.ldraw.org/parts/7495).
- [BrickLink element 6031098 → arch 6182](https://www.bricklink.com/v2/catalog/catalogitem.page?ccName=6031098&id=1473&idColor=1). The tan element is directly mapped in the installed BrickLink catalog.
- [BrickLink frame 60596](https://www.bricklink.com/v2/catalog/catalogitem.page?P=60596) and [frame 60594](https://www.bricklink.com/v2/catalog/catalogitem.page?P=60594). Their white element mappings are direct records in the installed catalog.
- [BrickLink element 6514119 → door 60616](https://www.bricklink.com/v2/catalog/catalogitem.page?ccName=6514119&id=78047&idColor=12); alternate LEGO numbers 35290/35291 are listed. It explicitly fits frame 60596.
- [LEGO Pick a Brick element 6514142 → design 35318](https://www.lego.com/fr-ca/pick-and-build/pick-a-brick?page=23); [BrickLink 60603](https://www.bricklink.com/v2/catalog/catalogitem.page?P=60603) lists alternate IDs 35318 and 86210 and explicitly fits frame 60594. [Official 86210 geometry](https://library.ldraw.org/library/official/parts/86210.dat) identifies BrickLink 60603.
- [LEGO Pick a Brick element 6256127 → frame 42205](https://www.lego.com/de-de/pick-and-build/pick-a-brick?appearsIn=60469&perPage=100&sort=created_at-desc).
- [BrickLink element 6511024 → pane 42509](https://www.bricklink.com/v2/catalog/catalogitem.page?ccName=6511024&id=176800&idColor=12) and [LEGO design 42509](https://www.lego.com/en-us/pick-and-build/pick-a-brick?page=26).

## Origins and structural geometry

Coordinates below are LDraw units: 20 per stud, 24 per brick, 8 per plate. Parts are upright with +Y downward, X across the wall and Z through its thickness. For a supporting surface at model Y=S, place a frame's origin at S minus its listed body height. Origins are at the upper body plane, excluding protruding studs.

| Part | Body X extent | Body Y extent | Body Z extent | Top attachment notes |
|---|---|---|---|---|
| 6182 | −40…40 | 0…48 | −10…10 | Four studs at X=−30,−10,10,30; bottom supported only by outer one-stud legs |
| 40066 | −60…60 | 0…168 | −10…10 | Central four studs at Y=0; outer two at X=±50, Y=24 |
| 60594 | −40…40 | 0…72 | −10…10 | Four studs, regular spacing |
| 60596 | −40…40 | 0…144 | −10…10 | Four studs, regular spacing |
| 42205 | −60…60 | 0…144 | −10…10 | Six studs, regular spacing |

**40066 does not have a level six-stud top.** Its outer pillar stud bases are one brick below the middle four. A straight six-stud lintel needs one-brick fillers over the two outer pillars. Geometry in `UnOfficial/parts/s/40066s01.dat` shows the central studs; `UnOfficial/parts/40066.dat` explicitly places the outer studs at `(±50,24,0)`. The arch opening has vertical sides at X=±40, an inside radius of 40 centered on `(0,48)`, and an inner crown at Y=8; the sill top is Y=160.

6182's opening is only two studs wide: its inside radius is 20 centered on `(0,28)`, with the inner crown at Y=8 and vertical opening sides X=±20. It is an ornamental small arch, not a four-stud-wide minifigure doorway.

## Frame and insert transforms

Apply these offsets in the frame's local axes, then apply the frame's world transform to both parts. Identity means `1 0 0 0 1 0 0 0 1`.

- **60596 + 60616a:** closed, left hinge: insert offset `(-32,0,5)`, identity. Closed, right hinge: `(32,0,5)`, Y rotation 180° (`-1 0 0 0 1 0 0 0 -1`). The door's local X=0 is its hinge axis; its panel extends toward +X. This mounting is explicitly documented in the [official door header](https://library.ldraw.org/library/official/parts/60616a.dat). The corresponding `60616b.dat` has identical placement instructions. Swing the leaf around its local Y hinge axis, retaining the hinge offset.
- **60594 + 86210:** top-hinged, closed insert offset `(0,8,4)`, identity. This follows the installed Studio connection transforms: frame custom connector type 200 at `(0,8,4)` and pane connector 201 at `(0,0,0)` have the same orientation. The pane has hinge ends X=±36 at Y=0; its lower edge Y=56 becomes frame Y=64, matching the opening. Frame also offers the upside-down bottom-hinge location `(0,60,4)`; prefer the simpler top hinge.
- **42205 + 42509:** insert offset `(0,4.5,5)`, identity. This is explicitly specified by `42509.dat`'s `!HELP` header. Pane main face is X=±56, Y=0…131.5, Z=−2. Studio's installed custom connector data instead use frame Y=4; use the explicit LDraw header's 4.5 when assembling LDraw geometry, and retain this 0.5-LDU discrepancy as a documented tolerance/version difference.

## File availability and remaining caveats

Most files are in `/Applications/Studio 2.0/ldraw/parts`; 40066, 42205 and 42509 are under `ldraw/UnOfficial/parts` in this installation. Despite that directory name, 42205's header is official UPDATE 2025-01 and 42509 is official UPDATE 2020-02. 40066's installed header is older unofficial geometry; the public library confirms official release 2022-01.

Do not use installed `UnOfficial/parts/60616.dat`: it is marked “Needs Work” and has different, irregular coordinates. Studio explicitly chooses `60616a.dat` as its canonical 60616 geometry. BrickLink groups square- and chamfered-handle variants under 60616; the exact minor surface details of element 6514119 are not independently established here. The connection, envelope, catalog identity, and canonical render mapping are verified. Similarly, newer 35318 glazing is represented by the catalog's canonical 86210 geometry; small molding differences are not separately modeled.

Research verified geometry and catalog compatibility; it did not perform a physical build or full-model collision test.
