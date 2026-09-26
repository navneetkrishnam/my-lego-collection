# Continuous roof study

Call `roof(m, x=1, y=1, w=26, d=16, base=68)` from `roof_study.py`.
The caller supplies a complete studded deck whose top is plate height 68.
Reserve this roof before spending reddish-brown 3039 slopes elsewhere.

Three courses occupy 26×16, 22×12, and 18×8 studs, starting at heights
68, 71, and 74. Their front and rear faces use 26 + 22 + 18 = **66 exact
4211202 slopes**. The final 14×4 ridge is tiled at height 77; its top is 78.
The chimney occupies 2×2 studs from height 77 through 84 and mounts directly
to the interior plateau, through a deliberate opening in the ridge tiles.

The code uses canonical 3039 geometry and checks its catalog origin offset
is `[0, 0, 10]`. Front slopes use angle 0 and rear slopes use 180 degrees.
There are no pitched plates, custom meshes, hinge gaps, or detached panels.
Every next course stands on the full studded plateau inside the preceding
course. Side ends are warm tiled terraces, each comprising two plate layers
and a tile. This is a stepped hip profile, not a smooth hip made from scarce
corner slopes. The concealed solid supports may use other colors.

Stock is allocated through the supplied Model. No quantities are invented.
All exterior packing prefers reddish brown, with dark brown, dark orange,
medium nougat, and dark tan as warm fallbacks. The cream chimney uses tan
then white. The function returns the actual exact-element usage and restores
the model if any allocation fails, so shortages can be reported without a
partially built roof. The roof uses no 85984 parts and does not require that
shape to be added to the catalog.

Validation results will be recorded below after the standalone allocation
and connection checks run. Physical assembly and rendering remain separate
review steps for the integrated facade model.
