# Contributing

Small, focused design or tooling improvements are welcome. Open an issue before a substantial geometry change so we can agree on intent and manufacturing tradeoffs.

## Setup and checks

Follow the [README](../README.md) to install Blender 4.3.2 and the pinned Pillow dependency. After changing geometry:

```sh
MEMPHIS_DRAFT=1 blender -b --python build_memphis.py
blender -b output/Memphis_Artisans.blend --python validate_memphis.py
blender -b output/Memphis_Artisans.blend --python render_drawings.py
python compose_drawings.py
blender -b output/Memphis_Artisans.blend --python export_prints.py
python -m unittest discover -s tests -v
```

On headless Linux, use `xvfb-run -a` for the drawing renderer. Use full-size renders for visual deliverables. Include updated audit reports and drawing/STL outputs when a geometry change affects them. Do not commit local paths, credentials, backup scenes, virtual environments, or intermediate drawing views.

## Fit reports and pull requests

For print/fit feedback, include the exact switch, printer, material, layer height, curing/shrinkage settings, and whether the cap completed the full switch stroke. Never claim production fit or strength based only on a clean mesh audit.

Keep pull requests focused and explain changed dimensions. Submit against `main`; CI should pass. Please be constructive when reviewing artistic choices and test findings.

## Rights and sign-off

Only submit work you created or have the right to share under the project's MIT license. Third-party material must retain its required attribution and license. Sign off commits with `git commit -s` to certify the [Developer Certificate of Origin](https://developercertificate.org/).
