# Hotel exterior study — cottage and services

This appearance pass adds detail to Cottage 01 and the service wing using the main villa's existing cream masonry, green shutters, terracotta tiles and dark metalwork. The approved layout v6 is the spatial baseline: all floor definitions, building positions, rooms, stairs, doors, gardens, pool dimensions and furniture placements are unchanged.

## Cottage 01

Both storeys now have stone window surrounds, recessed glazing-colored panels, timber frames and green louvered shutters wherever the available wall width permits. Fine masonry joints, corner stones, floor cornices and upper dentils give the long elevation the same vocabulary as the villa. The existing hip roof receives individual barrel-tile surfaces and ridge and hip covers without changing its footprint.

A planted window box sits below the first-floor bedroom window overlooking the private garden. The ground-floor foyer and private garden doors remain in their approved locations. The cottage remains one private suite over two floors; the shared lounge/library remains in the main villa.

## Service wing

The dining and spa levels receive matching window surrounds, shutters and masonry details. At salon level, stone rings, jambs and imposts emphasize the two existing open arches. The arcade remains unglazed. Its terrace keeps the original footprint and support envelopes; the coarse placeholder rails are replaced by slender dark spindles, top and bottom rails, a fascia and a small corner planter. The service hip roof receives matching tile surfaces and ridge and hip covers.

The dining, salon and spa room arrangements remain as approved. Five locally owned donor sets remain documented as candidates in `donor-candidates.json` and `donor-reuse.md`; this exterior pass does not claim an intact donor module fits, infer quantities, or reserve inventory.

## Review files

- `blockout-concept.png`: full hotel appearance.
- `blockout-front.png`: elevations, cottage garden window, service arcade and aligned stair.
- `blockout-plan.png`: roof detail and unchanged building, garden and pool arrangement.
- `blockout-rear.png`: rear and side treatments.
- `plan-arrival`, `plan-guest-floor`, `plan-services`, `plan-cottage`: unchanged spatial plans, each in PNG and native SVG.
- `blockout.ldr`: actual triangle-mesh geometry used in the renders; not LEGO part instances.
- `layout.json`: floor program and named geometry objects.
- `verification.json`: deterministic export, layout preservation, circulation and provenance checks.

The original image concept is included in the review ZIP as `reference-concept.png`. The architectural language follows it; the approved room program has since evolved. Cliff rockwork, planted pergolas, paving and landscaping remain for the next appearance step.

## Verification and limits

Checks compare the entire floor program and layout source with layout v6. Every named baseline object is retained exactly except the seven placeholder service-terrace rail objects explicitly replaced in this pass. New named objects belong to the cottage or service exteriors. The main-villa geometry extract is byte-identical to v6. Checks also cover the open service arcade, the cottage window box below its sill, both roof tile fields, the unchanged 57-destination circulation model, pool walking loop, furniture envelopes and export/render/plan hashes.

Navigation operates on the existing floor layout with declared stair connections and operable doors. It does not simulate door swings or every decorative projection. The glazing and lanterns are colored, opaque render surfaces. This is an architectural proxy: LEGO part availability, exact quantities, connections, loads, stair headroom and physical assembly remain unverified.

## Reproduce

Use `/private/tmp/fern-steam-py/bin/python` to run `donors.py`, `build.py`, `plans.py` and `check_layout.py`. Run `render.py --view concept --samples 128 --width 1600`, then render `front`, `plan` and `rear` at 48 samples / 1200 px. Finally run `verify.py`.

Requires Mitsuba CPU, the repository helper `data/mocs/fern-and-steam-v2/render_model.py`, local donor source data, and the preserved `layout-v6` baseline. `villa-detail.ldr` is a deterministic auxiliary extract for preservation checks. All review images are rendered from the exported model.
