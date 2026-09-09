# Memphis / artisan cluster — revision 2

## Files
- `output/Memphis_Artisans.blend` — editable four-keycap scene, materials, lighting and camera.
- `output/Memphis_Artisans.png` — hero render.
- `output/Memphis_Underside.png` — socket/cavity inspection render.
- `output/Memphis_Top.png` — straight-down layout review.
- `output/v1/` — preserved original scene, renders, generator and notes.
- `build_memphis.py` — deterministic Blender 4.3+ scene generator.
- `validate_memphis.py` / `output/Geometry_Check.json` — evaluated-mesh topology audit. All 63 design meshes passed: no non-manifold edges and positive signed volumes. This tests individual parts, not an assembled printable union.

## Design
Revised from the user's visual corrections, prioritizing low, bold, softly glazed relief over tall sculptural solids. The palette and base/socket geometry are retained.

- **Arch:** true semicircular annulus without straight posts; 14.6 mm wide, 1.6 mm relief. Rounded terminals sit close to the front edge. The orange element is an actual closed hemisphere, diameter 5 mm, with its equator on the deck. Its frontmost point aligns with the yellow cap's black beam at Y = -7.15 mm. The arch's inner curve closely surrounds it. Larger irregular ink-like patches replace the tiny speckles.
- **Zigzag:** broader 2.5 mm beam, 1.55 mm relief, shifted left/down to roughly 0.7 mm nominal edge margins. The lilac element is a 6.2 mm diameter, 1.65 mm high rounded cylinder, closer to the right edge than to the top.
- **Disc and rails:** 6.8 mm porcelain disc almost meets the left deck edge. Three 8.9 × 2.15 mm pill-shaped rails reach the right edge, with a small bottom margin. The rails' lower halves are buried into the shell.
- **Stairs:** one planar stair-shaped icon at a constant Z = 10.65 mm; no rising terraces. Approximately 0.9 mm nominal margins to the four deck edges.

Most relief parts use explicit curved profiles: 0.6–0.65 mm upper edge rolls, rounded plan corners and a subtle 0.12 mm flared foot to suggest a glazed ceramic junction. The arch uses exact tangent circular fillets and quad-strip caps. Parts remain separately editable; this visual junction is not an engineered multi-material fit.

## Dimensions / assumptions
Model coordinates are millimeters (scene unit scale 0.001). Standard 19.05 mm switch-center pitch; 18 mm square skirt tapering to a 16 mm deck; deck 9 mm above the cap's bottom datum. The tallest point is the orange dome at Z = 11.5 mm; most relief tops are at Z = 10.5–10.65 mm. This is a custom uniform artisan profile, not an exact Cherry/OEM row reproduction.

Each shell has an open underside, tapered inner cavity and approximately 1.85 mm roof. The centered 5.6 mm diameter mounting boss has a nominal 4.20 × 1.30 mm cross recess, 4.70 mm deep. The boss meets the roof. These are unverified MX-style prototype dimensions, **not a guaranteed switch fit**. Confirm against your specific switch and process.

## Before fabrication
1. Print a socket coupon first. Tune cross width/depth for switch stems, resin shrinkage and printer calibration. Never force a tight socket onto a switch.
2. Check switch-top clearance, full travel, neighboring key clearance and wall strength on the actual keyboard. The decorative set is intentionally taller than ordinary typing caps.
3. Plan a multi-part colored assembly or painted single-material print. Colored pieces overlap or meet the deck deliberately (the hemisphere's flat underside sits on it); do not interpret them as engineered press-fit inlays. For separate casting/printing, design pockets, alignment features and glue clearances.
4. For a one-piece print, duplicate the chosen cap, apply modifiers, and boolean-union its shell, socket and ornaments; inspect manifoldness and minimum features before export. Tiny terrazzo details are best painted or material-masked rather than printed independently.
5. Choose print orientation/supports to preserve the top finish and prevent cured resin collecting in the socket. The open cavity is not a sealed hollow volume.

## Blender
Collections 01–04 hold one cap each. Collection 05 is the studio; hide it when inspecting or exporting. Objects have descriptive names, named resin materials, and non-destructive edge bevels where practical. Select a part and press numpad `.` to frame it. The saved scene opens in a material-preview three-quarter view.

Rebuild:
```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python build_memphis.py
```
The generator resets the scene, writes the `.blend` and produces three renders in `output/`. Set `MEMPHIS_DRAFT=1` for a quick 900 px preview. The archived v1 generator must be copied to the project root before rebuilding v1, since its output path is relative to the script.
