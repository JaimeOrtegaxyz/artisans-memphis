# Memphis Artisan Keycaps

A coordinated set of four Memphis-inspired artisan keycaps: bold colors, geometric relief, and soft glazed finishes for a keyboard’s isolated 2×2 navigation cluster.

![Memphis artisan keycaps — current render](output/Memphis_Artisans.png)

## The set

- **Arch / porcelain + teal** — a dark teal arch with short straight terminals, an orange hemisphere, and Dalmatian-like black patches continuing over the cream base’s sides.
- **Zigzag / mustard + lilac** — a chunky black stepped beam and a low lilac cylinder, with tight spacing and small, square-ish corner radii.
- **Disc / cobalt** — a broad cream disc next to three rounded black rails reaching the deck’s right edge.
- **Stairs / vermilion + lilac** — a compact stair-shaped silhouette with one flat top, blocky corners, and room around its edges.

The models combine low relief, rounded shoulders, and subtle flared junctions for a glazed-ceramic impression. Colored parts remain separately editable.

**Current revision: 04.** The plain base is now **9.8 mm tall**, targeting the owner's Cherry R1/top-row height; the decorative relief starts above that deck. Four roof-level ribs reinforce each socket boss, with a small lead-in at the cross opening. This is a custom artisan profile informed by a GMK-based reference, not an exact or certified GMK reproduction.

## Open in Blender

Download or clone the repository, then open **[output/Memphis_Artisans.blend](output/Memphis_Artisans.blend)** in Blender 4.3 or newer.

```sh
git clone https://github.com/JaimeOrtegaxyz/artisans-memphis.git
cd artisans-memphis
```

Collections **01–04** contain one keycap each. Collection **05** contains the studio, lights, and cameras; hide it when inspecting or preparing model exports.

### Views

[Three-quarter render](output/Memphis_Artisans.png) · [Straight-down view](output/Memphis_Top.png) · [Underside render](output/Memphis_Underside.png)

![Hollow shells and prototype MX-style sockets](output/Memphis_Underside.png)

## Per-keycap overview drawings

One 2400 × 1800 PNG per cap, with top, front, right-side, and underside views plus a few overall dimensions:

- [01 — Arch + dome](output/drawings/01_ARCH_DOME.png)
- [02 — Zigzag + cylinder](output/drawings/02_ZIGZAG_CYLINDER.png)
- [03 — Disc + rails](output/drawings/03_DISC_RAILS.png)
- [04 — Stair silhouette](output/drawings/04_STAIR_SILHOUETTE.png)

The four sheets are the **current revision only** and replace the earlier drawings in place. They explicitly distinguish the 9.8 mm plain base from total height including decoration. These are simple orthographic design references, **not manufacturing drawings**. Glaze patterns are omitted for clarity, and socket recesses use an illustrative darker tint. Height dimensions are measured from the lowest modeled skirt edge, not the scene's Z = 0 datum. Images carry 300 DPI metadata, but their displayed/printed scale is not fixed.

To regenerate from the saved `.blend` without modifying it:

```sh
blender --background output/Memphis_Artisans.blend --python render_drawings.py
python3 -m pip install Pillow
python3 compose_drawings.py
```

Blender produces intermediate views in `output/drawings/_views/` (git-ignored); Pillow composes the four final sheets. `output/drawings/dimensions.json` records the measured overall heights and view metadata.

## Dimensions and prototype status

| Feature | Nominal dimension |
| --- | --- |
| Switch-center pitch | 19.05 mm |
| Base footprint | 18 × 18 mm |
| Top deck | 15 × 15 mm |
| Plain base height, skirt to deck | **9.8 mm** (formerly 8.75 mm) |
| Deck Z coordinate | 10.05 mm; skirt bottom is Z = 0.25 mm |
| Main exterior wall draft | Approximately 7.6° |
| Total height, arch / zigzag / disc / stairs | 12.30 / 11.45 / 11.30 / 11.45 mm |
| MX-style cross recess | 4.20 × 1.30 mm, 4.70 mm total depth |
| Cross entry lead-in | 0.10 mm at 45° |
| Socket reinforcement | Four high-set 1.10 mm nominal roof ribs |

**These are design prototypes, not production-ready keycaps.** Socket fit, switch clearance, full travel, print shrinkage, and assembly tolerances have not been physically validated. Test-print a socket coupon before attempting a full set, and never force a tight socket onto a switch.

Individual component meshes pass the included manifold-edge and positive-volume checks. That does **not** establish that the intersecting assembly is ready for printing. Parts need appropriate union or assembly preparation before fabrication. The black porcelain patches are a procedural material, so they will not appear in an STL export.

See **[MODEL_NOTES.md](MODEL_NOTES.md)** for detailed dimensions, reinforcement design, revision decisions, and fabrication guidance. The height choice is informed by the owner's measurements and [KeyV2's GMK-based Cherry R1 definition](https://github.com/rsheldiii/KeyV2/blob/19f0d2faadd4949634c93f38d1a66869d29e8f43/src/key_profiles/cherry.scad), whose height depends on stem-inset compensation; 9.8 mm is our design target, not a universal Cherry specification.

## Rebuild the scene

The generator uses Blender’s Python API; no MCP or third-party Python packages are required.

```sh
blender --background --python build_memphis.py
```

On macOS with Blender installed in Applications:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python build_memphis.py
```

For a quick 900 px preview:

```sh
MEMPHIS_DRAFT=1 blender --background --python build_memphis.py
```

**Rebuilding replaces the generated `.blend` and renders in `output/`.** Save manual edits elsewhere first. The script resets the scene, builds the models, saves the editable scene, and renders the three-quarter, top, and underside views.

### Check geometry

```sh
blender --background output/Memphis_Artisans.blend --python validate_memphis.py
```

This writes `output/Geometry_Check.json`, reporting non-manifold edges and signed volumes for each evaluated design mesh. Revision 4 also checks the actual 9.8 mm base height, unchanged socket mouth/seat levels, and four ribs per cap. It does not simulate physical switch travel or material strength.

## Repository contents

```text
README.md                              Project overview
MODEL_NOTES.md                         Dimensions, revisions, fabrication guidance
artisans-memphis-creative-brief.md       Original written concept
artisans-memphis-render.png             Original visual reference
build_memphis.py                       Scene and render generator
validate_memphis.py                    Component topology audit
render_drawings.py                     Isolated orthographic view renderer
compose_drawings.py                    Per-keycap drawing sheet compositor
output/
  Memphis_Artisans.blend               Current editable Blender scene
  Memphis_Artisans.png                 Three-quarter render
  Memphis_Top.png                      Straight-down layout view
  Memphis_Underside.png                Underside inspection render
  Geometry_Check.json                 Geometry audit results
  drawings/                           Four overview sheets and dimension metadata
  v1/                                 First modeled iteration
  v2/                                 Second modeled iteration
```

The original creative brief is preserved as historical context; the current model incorporates later visual corrections, including the lilac cylinder and single-height staircase. Earlier scenes, renders, scripts, and notes are retained in `output/v1/` and `output/v2/`. Archived generators use paths relative to their own location; copy one to the project root before rebuilding that version.
