# Cliffside Hotel implementation plan

> For agentic workers: use executing-plans to carry out the approved design.

**Goal:** Turn the approved cliffside-hotel concept into an approximately
2,500-piece, inventory-backed architectural model and review package.

**Architecture:** Freeze the collection and map exact elements to canonical
Studio geometry. Author separately budgeted building and landscape assemblies
against one shared allocator; export one LDraw model with assembly stages.

**Tech stack:** Python 3.12, local Studio catalog/LDraw, numpy, existing Mitsuba
renderer; ReportLab only after the model stabilizes.

**Spec:** `DESIGN.md` in this directory.

## Tasks

- [x] Inventory and geometry catalog: snapshot source hashes, conservative
  quantities, donor provenance and usable regular parts. Reject unknown geometry
  instead of substituting a visual proxy. Confirm slope and frame transforms.
- [x] Roof/facade feasibility: measure a warm pitched-roof solution and repeated
  window/door bays; document source-backed counts where they improve on the
  membership rule. Save any material concept deviations explicitly.
- [x] Author the base, cliff support, stairs, main building, connector, guest
  wing, terraces, pool, roof modules and interior details against one allocator.
  Record exact element, instance ID, step, transform and logical module.
- [x] Export BOM, allocation, model JSON, LDraw and placement schedule. Reject
  shortages and duplicate donor allocations; require identical deterministic
  outputs on a second run against the same inputs.
- [x] Check actual mesh dimensions and bottoms, regular-body overlaps, relevant
  special-part collisions and attachment graphs. Prototype fixtures must catch
  half-stud misalignment, rotated-part bounds and incorrect pane transforms.
- [x] Render front/rear views with actual geometry, inspect silhouette and
  details against the approved concept, and resolve visible deficiencies.
- [x] Generate a coordinate build draft and picking list, verify every instance
  is represented, test guide data, filters and pagination, then package with explicit limits.

No tracker changes, inventory reservations, app modifications, commit or
deployment are necessary for this artifact task. Keep the previous MOCs intact.

## Completed draft

Final model: 2,188 pieces, 218 exact elements, 18 stages. Actual front and rear
renders, offline HTML coordinate guide, picking list, donor allocations and
verification reports are provided. Browser UI inspection was unavailable;
guide logic and local links were checked. Physical prototype testing and a
conventional illustrated instruction book remain outside this digital draft.
