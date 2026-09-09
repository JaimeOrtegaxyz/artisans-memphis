# Memphis / model and fabrication notes

## Dimensions and mounting datums

Model coordinates are millimeters. Blender's metric unit scale is 0.001. The 18 × 18 mm skirts sit on a 19.05 mm switch-center pitch, tapering to 15 × 15 mm flat decks. Main exterior wall draft is approximately 7.6°.

The source scene's skirt bottom is Z = 0.25 mm and plain deck is Z = 10.05 mm: **9.8 mm of base height before decoration**. STL exports translate the skirt bottom to Z = 0 without scaling.

| Cap | Plain base | Total including relief |
| --- | --- | --- |
| Arch + dome | 9.8 mm | 12.30 mm |
| Zigzag + cylinder | 9.8 mm | 11.45 mm |
| Disc + rails | 9.8 mm | 11.30 mm |
| Stair silhouette | 9.8 mm | 11.45 mm |

### Cherry R1 reference

The target is informed by the owner's roughly 9–10 mm measurements and [KeyV2's GMK-based Cherry profile](https://github.com/rsheldiii/KeyV2/blob/19f0d2faadd4949634c93f38d1a66869d29e8f43/src/key_profiles/cherry.scad). That source defines R1 depth as `9.8 - extra_stem_inset_height + extra_height`, with `extra_stem_inset_height = max(0.6 - stem_inset, 0)`. Its default compensation can reduce the depth to 9.2 mm. Dish, tilt, row labels, and mounting conventions matter; **9.8 mm is our chosen physical flat-deck height, not a universal manufacturer specification**.

[Keycaps.info](https://www.keycaps.info/) is useful for comparing row silhouettes, not for manufacturing dimensions. The artisans deliberately retain a wide, flat deck instead of copying a Cherry dish or tilted top. Actual alignment on the owner's keyboard must be tested.

## Relief geometry

- **Arch:** the 5 mm hemisphere and curved arch share XY center (0, -4.15). Inner/outer radii are 3.35/7 mm, producing a nominal 0.85 mm radial gap in plan and a 3.65 mm band. Short straight legs extend 2.15 mm below the arc centerline. Rounded terminals reach Y = -6.3 mm, approximately -6.42 mm including the glazed foot. The dome reaches Y = -6.65 mm. Relief is 1.6 mm; the dome rises 2.5 mm above the deck.
- **Porcelain patches:** a warped 3D Voronoi material creates flush black patches across the deck, shoulders, and exterior walls. The cavity and socket stay cream. This is a material effect, not mesh geometry, and is absent from STL.
- **Zigzag:** 2.85 mm-wide beam, 1.55 mm relief, 0.28 mm inside/outside plan radii, and an independent 0.45 mm shoulder roll. Lilac cylinder diameter is 6.9 mm, centered at (3.45, 2.6). Nominal sharp-corner-to-circle clearance is about 0.96 mm; fillets alter local clearances.
- **Disc and rails:** 7.1 mm disc centered at (-3.8, 2.45), almost touching the first rail. Three 8.3 × 2.35 mm pill-shaped rails reach the deck's right edge, with their lower halves buried in the roof.
- **Stairs:** a 10.5 × 10.5 mm stair-shaped outline, centered within nominal 2.25 mm margins. Its top is one plane at Z = 11.70 mm, 1.65 mm above the deck. Plan radii are 0.28 mm; shoulder roll is 0.45 mm.

Rounded motifs use broad 0.6 mm shoulder rolls. Glazed relief has a subtle 0.12 mm flared foot. Colored parts remain separate in the editable scene; these visual junctions are not engineered press-fit inlays.

## Socket and structural ribs

- Open underside, tapered cavity, approximately 1.85 mm roof.
- Centered 5.6 mm-diameter boss. In source-scene coordinates, mouth Z = 0.4 mm and seating stop Z = 5.1 mm.
- Nominal cross engagement is 4.20 × 1.30 mm, with 4.70 mm total recess depth. A 0.10 mm / 45° lead-in opens the mouth to 4.40 × 1.50 mm before narrowing to the engagement section.
- Four 1.10 mm nominal-width radial ribs tie the boss into the roof and inner walls. Lower edges slope upward toward the walls; their lowest nominal Z is approximately 6.05 mm. Small 0.14 mm radii soften the braces.
- The ribs are permanent structural geometry, **not removable slicer supports**. They intentionally occupy the upper cavity to leave the lower housing space open.

These dimensions have not been physically validated for fit, full travel, fatigue, or strength. Test against the exact switch and printing/casting process.

## Printing and validation

`output/print/` contains four complete single-material caps and `00_BASE_FIT_TEST.stl`. The fit-test piece uses the same shell, socket, and reinforcement without decorative relief.

The exporter evaluates modifiers, boolean-unions the pieces, triangulates, and checks that each STL has one connected component, no non-manifold edges, no degenerate triangles, positive signed volume, and a skirt bottom at Z = 0. `Print_Check.json` records those results. `Geometry_Check.json` audits the separate source components and verifies base/socket dimensions and rib counts. Neither audit proves physical fit or successful printing.

1. Print the plain-base test first, using your intended material and calibration. Check that it mounts and removes without force.
2. Test the full switch stroke. Pay particular attention to housing contact with ribs, skirt clearance, and neighboring caps. Compare the plain deck—not the ornaments—to your keyboard's key heights.
3. Tune socket dimensions for the switch, printer accuracy, resin shrinkage, and curing. Use fine-detail printing suitable for small MX recesses. Avoid blindly scaling the whole cap: that also changes its footprint and height.
4. Choose orientation and temporary supports in the slicer. Protect the socket opening and top finish; ensure uncured resin can drain from the open cavity. Follow the resin/printer manufacturer's handling and curing instructions.
5. STL does not preserve colors or procedural patches. Paint a single-material print, or design a separate multi-part/multicolor process from the Blender scene. A press-fit colored assembly needs its own pockets, alignment features, and clearances.
6. If editing the model, regenerate exports and audit them again. Do not export the studio or mistake the editable overlapping parts for the already-joined print meshes.

## Files and regeneration

- `output/Memphis_Artisans.blend` — editable model, resin materials, camera, and studio.
- `output/Memphis_Artisans.png`, `Memphis_Top.png`, `Memphis_Underside.png` — three views.
- `output/drawings/` — four non-toleranced overview sheets and view metadata.
- `output/print/` — five joined STL prototypes and print audit.
- `build_memphis.py` — regenerates the scene and renders.
- `render_drawings.py` / `compose_drawings.py` — regenerate drawing sheets without saving changes to the source model.
- `export_prints.py` — regenerates joined print meshes without modifying the source model.

See the [README](README.md) for complete setup and validation commands. Regeneration overwrites outputs; save manual work elsewhere first.
