# Memphis / artisan cluster

## Files
- `output/Memphis_Artisans.blend` — editable four-keycap scene, materials, lighting and camera.
- `output/Memphis_Artisans.png` — hero render.
- `output/Memphis_Underside.png` — socket/cavity inspection render.
- `build_memphis.py` — deterministic Blender 4.3+ scene generator.
- `validate_memphis.py` / `output/Geometry_Check.json` — evaluated-mesh topology audit. All 65 design meshes passed: no non-manifold edges and positive signed volumes. This tests individual parts, not an assembled printable union.

## Design
The supplied reference is interpreted as a coordinated 2×2 set: porcelain/teal arch and orange bead; ochre/black zigzag and violet bead; ultramarine disc and rails; vermilion/lilac staircase. All decoration is actual geometry, including the fine terrazzo flecks. Relief pieces and shells remain separate for easy recoloring and fabrication planning. The staircase adds a modest physical rise to its stepped plan silhouette.

## Dimensions / assumptions
Model coordinates are millimeters (scene unit scale 0.001). Standard 19.05 mm switch-center pitch; 18 mm square skirt tapering to a 16 mm deck; deck 9 mm above the cap's bottom datum. Sculptures bring overall height to approximately 12.7 mm. This is a custom uniform artisan profile, not an exact Cherry/OEM row reproduction.

Each shell has an open underside, tapered inner cavity and approximately 1.85 mm roof. The centered 5.6 mm diameter mounting boss has a nominal 4.20 × 1.30 mm cross recess, 4.70 mm deep. The boss meets the roof. These are unverified MX-style prototype dimensions, **not a guaranteed switch fit**. Confirm against your specific switch and process.

## Before fabrication
1. Print a socket coupon first. Tune cross width/depth for switch stems, resin shrinkage and printer calibration. Never force a tight socket onto a switch.
2. Check switch-top clearance, full travel, neighboring key clearance and wall strength on the actual keyboard. The decorative set is intentionally taller than ordinary typing caps.
3. Plan a multi-part colored assembly or painted single-material print. Current colored pieces overlap shells deliberately; do not interpret them as engineered press-fit inlays. For separate casting/printing, design pockets, alignment features and glue clearances.
4. For a one-piece print, duplicate the chosen cap, apply modifiers, and boolean-union its shell, socket and ornaments; inspect manifoldness and minimum features before export. Tiny terrazzo details are best painted or material-masked rather than printed independently.
5. Choose print orientation/supports to preserve the top finish and prevent cured resin collecting in the socket. The open cavity is not a sealed hollow volume.

## Blender
Collections 01–04 hold one cap each. Collection 05 is the studio; hide it when inspecting or exporting. Objects have descriptive names, named resin materials, and non-destructive edge bevels where practical. Select a part and press numpad `.` to frame it. The saved scene opens in a material-preview three-quarter view.

Rebuild:
```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python build_memphis.py
```
The generator resets the scene, writes the `.blend` and produces both renders in `output/`.
