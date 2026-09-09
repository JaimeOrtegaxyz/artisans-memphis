# Memphis / artisan cluster — revision 3

## Files
- `output/Memphis_Artisans.blend` — editable four-keycap scene, materials, lighting and camera.
- `output/Memphis_Artisans.png` — hero render.
- `output/Memphis_Underside.png` — socket/cavity inspection render.
- `output/Memphis_Top.png` — straight-down layout review.
- `output/drawings/01_*.png` through `04_*.png` — one overview sheet per keycap, with top/front/right/underside views and a few dimensions. Heights measure from the modeled skirt bottom (Z = 0.25), so the shell reads 8.75 mm and the tallest dome cap 11.25 mm overall. These are non-toleranced design references, not manufacturing drawings.
- `render_drawings.py` / `compose_drawings.py` — regenerate drawing sheets from the saved scene using Blender Workbench and Pillow. The drawing renderer does not save changes to the model.
- `output/v1/`, `output/v2/` — preserved earlier scenes, renders, generators and notes.
- `build_memphis.py` — deterministic Blender 4.3+ scene generator.
- `validate_memphis.py` / `output/Geometry_Check.json` — evaluated-mesh topology audit. All 17 design meshes passed: no non-manifold edges and positive signed volumes. This tests individual parts, not an assembled printable union.

## Design
Revision 3 tightens the compositions while restoring blocky corners to the angular motifs. Socket and cavity dimensions are retained; the exterior taper is increased.

- **Arch:** arch and 5 mm hemisphere share the same XY center, (0, -4.15). The nominal inner radius is 3.35 mm and outer radius 7 mm: a constant 0.85 mm radial gap in plan and a 3.65 mm band, wider than v2. Relief remains 1.6 mm. Following the latest correction, short straight legs extend 2.15 mm below the arc's centerline. Their rounded terminals reach Y = -6.3 mm (approximately -6.42 mm including the glazed foot), close to the dome's -6.65 mm bottom. The curved crown stays concentric; the straight extensions deliberately do not follow a constant radial distance. Teal is darker and more saturated. The dome's frontmost point aligns with the yellow beam at Y = -6.65 mm.
- **Porcelain pattern:** fewer, larger Dalmatian-like black patches replace separate fleck meshes. A warped 3D Voronoi material maps continuously across the deck, bevels and outer tapered walls. The underside cavity and socket remain clean cream. These are flush material markings, not geometry; bake/paint or use a color-capable fabrication process to reproduce them. They will not appear in STL.
- **Zigzag:** 2.85 mm beam (up from 2.5), 1.55 mm relief. Both convex and concave plan corners have a small 0.28 mm radius, independent of the 0.45 mm vertical shoulder roll. This avoids the previous overly rounded inside corners and pointed outside corners. The lilac cylinder grows to 6.9 mm diameter, centered at (3.45, 2.6), lower and closer to the beam. Nominal sharp-corner-to-circle clearance is 0.96 mm, about one-third of beam width; fillets and glazed feet alter local surface clearances.
- **Disc and rails:** porcelain disc grows to 7.1 mm diameter and moves down to (-3.8, 2.45), almost meeting the first rail. Rails are 8.3 × 2.35 mm (thicker than v2), cropped to reach the new right deck edge. Lower halves remain buried in the shell; small front margin is retained.
- **Stairs:** constant Z = 10.65 mm top; outline compacted to 10.5 × 10.5 mm, centered in the deck. Nominal margins are 2.25 mm, 2.5× the previous 0.9 mm. Matching 0.28 mm inner/outer plan corners give a squarer silhouette, with a separate 0.45 mm glazed shoulder roll.

The rounded motifs retain broad 0.6 mm shoulder rolls. All glazed relief has a subtle 0.12 mm flared foot. The arch uses exact tangent circular fillets and quad-strip caps. Parts remain separately editable; this visual junction is not an engineered multi-material fit.

## Dimensions / assumptions
Model coordinates are millimeters (scene unit scale 0.001). Standard 19.05 mm switch-center pitch; 18 mm square skirt tapering to a 15 mm deck (previously 16 mm); the main exterior wall draft increases from approximately 5° to 8.6°; deck 9 mm above the cap's bottom datum. The tallest point is the orange dome at Z = 11.5 mm; most relief tops are at Z = 10.5–10.65 mm. This is a custom uniform artisan profile, not an exact Cherry/OEM row reproduction.

Each shell has an open underside, tapered inner cavity and approximately 1.85 mm roof. The centered 5.6 mm diameter mounting boss has a nominal 4.20 × 1.30 mm cross recess, 4.70 mm deep. The boss meets the roof. These are unverified MX-style prototype dimensions, **not a guaranteed switch fit**. Confirm against your specific switch and process.

## Before fabrication
1. Print a socket coupon first. Tune cross width/depth for switch stems, resin shrinkage and printer calibration. Never force a tight socket onto a switch.
2. Check switch-top clearance, full travel, neighboring key clearance and wall strength on the actual keyboard. The decorative set is intentionally taller than ordinary typing caps.
3. Plan a multi-part colored assembly or painted single-material print. Colored pieces overlap or meet the deck deliberately (the hemisphere's flat underside sits on it); do not interpret them as engineered press-fit inlays. For separate casting/printing, design pockets, alignment features and glue clearances.
4. For a one-piece print, duplicate the chosen cap, apply modifiers, and boolean-union its shell, socket and ornaments; inspect manifoldness and minimum features before export. The black porcelain pattern is a material effect and must be painted, baked or separately color-fabricated.
5. Choose print orientation/supports to preserve the top finish and prevent cured resin collecting in the socket. The open cavity is not a sealed hollow volume.

## Blender
Collections 01–04 hold one cap each. Collection 05 is the studio; hide it when inspecting or exporting. Objects have descriptive names, named resin materials, and non-destructive edge bevels where practical. Select a part and press numpad `.` to frame it. The saved scene opens in a material-preview three-quarter view.

Rebuild:
```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python build_memphis.py
```
The generator resets the scene, writes the `.blend` and produces three renders in `output/`. Set `MEMPHIS_DRAFT=1` for a quick 900 px preview. Archived generators must be copied to the project root before rebuilding earlier versions, since output paths are relative to the script.
