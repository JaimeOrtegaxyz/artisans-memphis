# Memphis / artisan cluster — revision 4

## Files
- `output/Memphis_Artisans.blend` — editable four-keycap scene, materials, lighting and camera.
- `output/Memphis_Artisans.png` — hero render.
- `output/Memphis_Underside.png` — socket/cavity inspection render.
- `output/Memphis_Top.png` — straight-down layout review.
- `output/drawings/01_*.png` through `04_*.png` — one overview sheet per keycap, with top/front/right/underside views and a few dimensions. Heights measure from the modeled skirt bottom (Z = 0.25), so the plain base reads **9.8 mm**, with the tallest dome cap **12.3 mm overall**. The current sheets are replaced in place, not duplicated. These are non-toleranced design references, not manufacturing drawings.
- `render_drawings.py` / `compose_drawings.py` — regenerate drawing sheets from the saved scene using Blender Workbench and Pillow. The drawing renderer does not save changes to the model.
- `output/v1/`, `output/v2/` — preserved earlier scenes, renders, generators and notes.
- `build_memphis.py` — deterministic Blender 4.3+ scene generator.
- `validate_memphis.py` / `output/Geometry_Check.json` — evaluated-mesh topology audit. All 33 design meshes passed: no non-manifold edges and positive signed volumes. Added checks confirm the 9.8 mm physical base height, unchanged socket mouth/seat levels, and four roof ribs per cap. This tests individual parts, not an assembled printable union.

## Design
Revision 4 raises the **plain base from 8.75 to 9.8 mm**; all ornaments move up 1.05 mm without scaling. Plan layouts, radii, relief heights, and colors are retained. The porcelain texture coordinates compensate for the taller body to preserve the stain layout. The taller roof is reinforced with four high-set buttresses per socket.

### Cherry R1 height reference
The owner's top-row/number-row Cherry caps measure roughly 9–10 mm. The [KeyV2 GMK-based Cherry profile](https://github.com/rsheldiii/KeyV2/blob/19f0d2faadd4949634c93f38d1a66869d29e8f43/src/key_profiles/cherry.scad) uses `9.8 - extra_stem_inset_height + extra_height` for R1, with `extra_stem_inset_height = max(0.6 - stem_inset, 0)`. Thus 9.8 mm is **not a universal manufacturer dimension**: its default inset compensation can reduce that model to 9.2 mm, and dish/row/mounting conventions matter. [Keycaps.info](https://www.keycaps.info/) also illustrates the differing Cherry/GMK row silhouettes, but is not a dimensional manufacturing specification.

We choose **9.8 mm physical skirt-to-flat-deck height** as a deliberate near-10 mm target consistent with the owner's measurement, not as an exact GMK copy. Our flat 15 mm deck has no Cherry dish or tilt. The cross recess seating stop remains at its previous Z, so this is a genuine mounted-height increase rather than merely moving the stem and body together. Actual alignment with the owner's keyboard still requires a fit/travel test.

### Retained compositions

- **Arch:** arch and 5 mm hemisphere share the same XY center, (0, -4.15). The nominal inner radius is 3.35 mm and outer radius 7 mm: a constant 0.85 mm radial gap in plan and a 3.65 mm band, wider than v2. Relief remains 1.6 mm. Following the latest correction, short straight legs extend 2.15 mm below the arc's centerline. Their rounded terminals reach Y = -6.3 mm (approximately -6.42 mm including the glazed foot), close to the dome's -6.65 mm bottom. The curved crown stays concentric; the straight extensions deliberately do not follow a constant radial distance. Teal is darker and more saturated. The dome's frontmost point aligns with the yellow beam at Y = -6.65 mm.
- **Porcelain pattern:** fewer, larger Dalmatian-like black patches replace separate fleck meshes. A warped 3D Voronoi material maps continuously across the deck, bevels and outer tapered walls. The underside cavity and socket remain clean cream. These are flush material markings, not geometry; bake/paint or use a color-capable fabrication process to reproduce them. They will not appear in STL.
- **Zigzag:** 2.85 mm beam (up from 2.5), 1.55 mm relief. Both convex and concave plan corners have a small 0.28 mm radius, independent of the 0.45 mm vertical shoulder roll. This avoids the previous overly rounded inside corners and pointed outside corners. The lilac cylinder grows to 6.9 mm diameter, centered at (3.45, 2.6), lower and closer to the beam. Nominal sharp-corner-to-circle clearance is 0.96 mm, about one-third of beam width; fillets and glazed feet alter local surface clearances.
- **Disc and rails:** porcelain disc grows to 7.1 mm diameter and moves down to (-3.8, 2.45), almost meeting the first rail. Rails are 8.3 × 2.35 mm (thicker than v2), cropped to reach the new right deck edge. Lower halves remain buried in the shell; small front margin is retained.
- **Stairs:** constant Z = 11.70 mm top (1.65 mm above the raised deck); outline compacted to 10.5 × 10.5 mm, centered in the deck. Nominal margins are 2.25 mm, 2.5× the previous 0.9 mm. Matching 0.28 mm inner/outer plan corners give a squarer silhouette, with a separate 0.45 mm glazed shoulder roll.

The rounded motifs retain broad 0.6 mm shoulder rolls. All glazed relief has a subtle 0.12 mm flared foot. The arch uses exact tangent circular fillets and quad-strip caps. Parts remain separately editable; this visual junction is not an engineered multi-material fit.

## Dimensions / assumptions
Model coordinates are millimeters (scene unit scale 0.001). Standard 19.05 mm switch-center pitch; 18 mm skirt and 15 mm deck remain unchanged. The physical skirt bottom is Z = 0.25 mm; the plain deck is now Z = 10.05 mm, giving **9.8 mm of base height before decoration**. Keeping those widths while raising the body changes the main wall draft from ~8.6° to ~7.6°.

| Cap | Plain base height | Total height including relief |
| --- | --- | --- |
| Arch + dome | 9.8 mm | 12.30 mm |
| Zigzag + cylinder | 9.8 mm | 11.45 mm |
| Disc + rails | 9.8 mm | 11.30 mm |
| Stair silhouette | 9.8 mm | 11.45 mm |

### Mount and reinforcement
- The cavity ceiling moves up with the deck, maintaining the approximately 1.85 mm roof. The lower cavity opening remains unchanged.
- The 5.6 mm diameter boss extends upward to meet the new ceiling. Its bottom stays at Z = 0.4 mm and its cross seating stop stays at Z = 5.1 mm.
- Cross engagement remains nominally 4.20 × 1.30 mm, with total recess depth 4.70 mm. A 0.10 mm / 45° entry lead-in opens the mouth to 4.40 × 1.50 mm before narrowing to the nominal section; it does not deepen the seating stop.
- Four 1.10 mm nominal-width radial ribs per cap join the boss to the roof and inner walls through intentional overlaps. Their lower edges slope upward toward the walls; the lowest rib surface starts around Z = 6.05 mm, keeping reinforcement above the socket seat and leaving the lower housing cavity open. Small 0.14 mm edge radii soften the braces.
- Ribs, bosses, and shells remain separate editable solids. They must be united into a continuous printable body before manufacturing; these ribs are permanent structural geometry, not removable slicer supports.

These are unverified MX-style prototype dimensions, **not a guaranteed switch fit or strength rating**. Housing clearance at full travel, polymer behavior, fatigue, and actual mounting height have not been physically tested.

## Before fabrication
1. Print a socket coupon first. Tune cross width/depth for switch stems, resin shrinkage and printer calibration. Never force a tight socket onto a switch.
2. Check switch-top clearance against the new ribs, full travel, neighboring key clearance and wall strength on the actual keyboard. The decorative set is intentionally taller than ordinary typing caps.
3. Plan a multi-part colored assembly or painted single-material print. Colored pieces overlap or meet the deck deliberately (the hemisphere's flat underside sits on it); do not interpret them as engineered press-fit inlays. For separate casting/printing, design pockets, alignment features and glue clearances.
4. For a one-piece print, duplicate the chosen cap, apply modifiers, and boolean-union its shell, socket, four structural ribs and ornaments; inspect manifoldness and minimum features before export. The black porcelain pattern is a material effect and must be painted, baked or separately color-fabricated.
5. Choose print orientation/supports to preserve the top finish and prevent cured resin collecting in the socket. The open cavity is not a sealed hollow volume.

## Blender
Collections 01–04 hold one cap each. Collection 05 is the studio; hide it when inspecting or exporting. Objects have descriptive names, named resin materials, and non-destructive edge bevels where practical. Select a part and press numpad `.` to frame it. The saved scene opens in a material-preview three-quarter view.

Rebuild:
```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python build_memphis.py
```
The generator resets the scene, writes the `.blend` and produces three renders in `output/`. Set `MEMPHIS_DRAFT=1` for a quick 900 px preview. Archived generators must be copied to the project root before rebuilding earlier versions, since output paths are relative to the script.
