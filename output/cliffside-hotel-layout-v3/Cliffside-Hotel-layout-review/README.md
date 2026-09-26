# Cliffside Hotel — room-programmed layout

This revision develops the user's accepted L-shaped composition into a coherent hotel layout. The exterior, floor plates, partitions, room doors, windows and floor-plan drawings are authored from the same layout. These are architectural proxy volumes, not yet LEGO part instances.

## Hotel program

| Location | Arrangement |
|---|---|
| Main villa, courtyard level +40 | Lobby, front desk, back office, common WC, library/lounge, guest stair core, direct door to common side garden |
| Main villa, +54 | Room 101 without balcony; room 102 with balcony; larger suite 103 with its own balcony; private bathroom for each |
| Main villa, +68 | Same arrangement: rooms 201–203 |
| Garden cottage, +40 | One private room with bathroom, its own garden-facing entrance and porch/pergola garden |
| Service building, +40 | Restaurant/pool bar, kitchen/pantry, public corridor and stair core |
| Service building, +26 | Salon, quiet lounge and open arcade terrace |
| Service building, +12 | Two treatment rooms, changing/showers and spa relaxation |

**Total: six rooms in the main villa plus one cottage.** The ground floor of the main villa is communal space, not another guest-room floor. The service building has no guest bedrooms.

The two rooms in the villa's long arm sit one behind the other, with a common corridor along the inner edge. The front room has a balcony; the rear garden-facing room does not. The larger suite occupies the outer portion of the horizontal arm, beyond the shared stair core, with a balcony facing the courtyard. Each room has its own door from the corridor and its own external window openings. The L perimeter is authored once; complete rectangular building shells are no longer laid over one another at its junction.

## Access and usable outdoor space

Guests arrive up a straight central stair into the entrance court, then enter the lobby through the inner side of the L. The lobby has a separate door to the common side garden. The cottage entrance is reached from its own porch/garden. A shared promenade outside that garden connects the main court, pool terrace and restaurant entrance.

The service stair core opens onto shared corridors on all three levels. Reaching the salon or spa does not require crossing a kitchen or treatment room. The kitchen has a separate door from the upper corridor. This is a guest-flow scheme, not a completed deliveries, emergency-egress or accessibility design.

The pool is 22 × 12 studs inside a 38 × 34 stud deck. Between the coping and edge guards, the layout leaves 7 studs at either side, 9.5 behind, and 11 in front before furniture. Three lounger envelopes sit in the front band. A 4.5-stud strip between coping and loungers keeps the walking loop clear. The right guard ends at the restaurant frontage, leaving its doorway accessible.

## Stair and support geometry

Both exterior flights occupy exactly x=44..58: the same 14-stud width and centreline. There are 48 risers, each 0.8 stud high (two plate heights), with 1-stud treads. A 14 × 6 stud landing separates two flights of 24 steps. The stair descends from +40 to +1.6 with no lateral shift.

Each internal stair core reserves a 10 × 14 stud clear footprint. Upper floors have explicit shaft openings. The modeled U-stair uses 35 plate-height risers between 14-stud floor levels, split into flights of 18 and 17; these are still geometric stair envelopes, not a verified part arrangement.

The high plateau ends before the descending service building. That building starts on a low plinth at +12, preserving its exposed lower floors. The pool deck has support up to its underside around the pool cavity. Balcony support envelopes extend two studs inside the adjoining building and beneath the projecting deck. These show intended load paths; their LEGO connections, stiffness and carrying strength have not been tested.

## Review drawings

- `blockout-concept.png`: overall front-left view.
- `blockout-front.png`: straight stair alignment and the two floors below courtyard level.
- `blockout-plan.png`: overall roof and terrace arrangement.
- `blockout-rear.png`: rear geometry and openings.
- `plan-arrival.png` / `.svg`: lobby, gardens, cottage, shared routes, pool and restaurant.
- `plan-guest-floor.png` / `.svg`: the three guest rooms, individual bathrooms, corridor, stair core and two balconies.
- `plan-services.png` / `.svg`: all three service floors and public circulation.

## Verification scope

`check_layout.py` flood-fills the actual authored floor plates on a 0.5-stud grid. Walls remain barriers except at declared door gaps; floor holes, furniture and pergola posts are excluded. Vertical links join the landings of the modeled stair cores. All 48 review destinations are reachable. A second check blocks private/service rooms and the cottage garden; all six stair landings remain reachable via public circulation. The four clear pool-deck strips are also checked against these obstacles.

`verify.py` additionally checks the room program, stair dimensions, floor/shaft relationships, pool support volumes, deterministic export, and hashes tying the rendered views and plans to their sources. These checks are not a structural simulation, LEGO connection verification or a real-building certification. Door swings, detailed utilities, full service logistics, facade construction, roof assemblies and terrain cladding remain subsequent design work.

## Scale and next construction pass

The provisional base is **128 × 114 studs**, or **102.4 × 91.2 cm** at literal stud scale. The larger footprint accommodates usable stairs, circulation, room partitions and pool surrounds. No piece estimate is assigned at this proxy stage.

After this arrangement is accepted, the next construction pass should establish a modular LEGO frame beneath the three building footprints, removable guest-floor trays and roofs, aligned wall supports, actual balcony anchorage, and the two stair cores. Room walls and openings should be translated into a consistent LEGO grid before decorative arches, shutters, terracotta roofing and planted rockwork are developed. Hollow supported terrain should replace the solid cliff envelopes used for the study.

## Reproduce

Using `/private/tmp/fern-steam-py/bin/python`, run `build.py`, `plans.py`, `check_layout.py`, then `render.py --view concept --samples 128 --width 1600` and the other views (`front`, `plan`, `rear`). Finally run `verify.py`. `layout.py` is the source for the room and wall definitions; `layout.json` is its exported schedule. Prior revisions remain in the sibling `blockout/` and `blockout-v2/` directories.
