# Courtyard revision execution plan

Approved direction: [CONCEPT.md](CONCEPT.md). All owned sets are donors.

- [x] Author a 24 × 24 courtyard with the researched arches, compatible glazing,
  fixed pitched roof, restrained paving, furniture and grouped planting.
  `model.py` produces `model.json`, the LDraw model, an exact BOM and a frozen
  inventory snapshot. Coordinates are studs / plate heights; every instance
  retains its exact element ID and assembly step.
- [x] Render actual LDraw geometry with `render_model.py`, using the installed
  Studio part library and Mitsuba CPU rendering. Inspect front and rear views.
  Eyesight and POV-Ray remain unused because their startup probes failed.
- [x] Audit conservative inventory, catalog mappings, duplicate placements,
  solid-body intersections and attachment continuity. Keep special geometry
  checks separate from regular brick/plate checks. Record limitations; do not
  label a digitally reviewed model physically verified.
- [x] Review the complete model, fix evidenced problems, reproduce the exports,
  and supply the actual preview, editable model, picking list and build notes.

The existing v1 and the user's other MOCs remain intact. No tracker inventory
is changed. No commit or deployment is required for this artifact task.
