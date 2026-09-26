# Candidate donor reuse — retained interior strategy

The approved layout places the library in the main villa. This exterior pass retains the previous interior strategy and donor candidates; ownership and element-membership hashes are refreshed against local data.

Ownership is checked against `data/owned-sets.csv`, with names and images from the local catalog. One copy of each set below is recorded as owned. `public/data/parts/<set>.json` proves element membership, not quantity per set. These are candidates, not stock allocations.

| Hotel area | Owned candidate | Proposed reuse |
|---|---|---|
| Restaurant and kitchen | **42655 Restaurant and Cooking School** | Adapt the visible four-chair dining-table arrangement and kitchen counter/island idea. Locally listed mixer tap 6245261, cupboard 6404592, fork 6361354 and cup 6235083 are concrete candidates. |
| Dining, garden and spa details | **42691 Garden Restaurant** | Supplement dining/garden details; mixer tap 6245261 and tap 6146054 could form spa wash fittings. Flat tile 4560180 is a candidate furniture finish. |
| Salon | **42662 Hair Salon and Accessories Store** | Rebuild the styling-chair, mirror and counter arrangement visible in its interior photo. Scissors 6489198, brushes 6058368 / 4243668, tap 6146054 and cupboard 6313992 are locally listed. |
| Second salon station | **41743 Hair Salon** | Adapt another styling/wash arrangement and reuse scissors 6096993, brush 4243668 and tap 6146054. |
| Library and spa finishing | **10362 French Café** | Book elements 6174229 and 6523320 are candidates for library shelves; flat tile 6164288 can finish custom spa furniture. |

Restaurant/salon fittings should be rebuilt as small removable interior modules within the hotel, retaining recognizable functions and accessories. Their original multicolored building shells need not be reproduced. The current plans reserve two four-seat restaurant tables, two 4 × 4 salon-chair areas and one 4 × 4 wash-station area. The eight restaurant seats provide a small dining room; accommodating every possible hotel occupant simultaneously would require a later capacity revision.

For the spa, use two custom treatment beds, a tiled wash counter with taps, storage for rolled-towel representations, and lounge furniture. The treatment-bed envelopes are 4 × 7 studs each. These are proposed assemblies, not claims that an intact spa exists in the collection. Final tile colors, quantities, hinges and connections remain to be chosen against a part-level layout.

The same tap or flat-tile element may appear in multiple candidate rows or functions. That is intentionally an option list: it does not mean the same physical piece has been allocated twice. Actual consumption will be recorded once a bill of materials exists. No donor has been dismantled, reserved or modified in the tracker.

`donor-candidates.json` includes every named element, its exact local source record, the ownership/catalog hashes, and hashes for the reference photos used in the earlier donor review. `donors.py` regenerates the evidence report without network access.
