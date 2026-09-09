# External tools and references

## Runtime / build tools

| Tool | License | Use |
| --- | --- | --- |
| [Blender 4.3.2](https://www.blender.org/about/license/) | GPL-3.0-or-later | External model/render/CSG tool, including its bundled Python API. Blender itself is not vendored or redistributed here. |
| [Pillow 12.3.0](https://pillow.readthedocs.io/en/stable/about.html#license) | MIT-CMU | Drawing-sheet composition. Installed from PyPI, not vendored. No optional extras are required. |
| [Python](https://docs.python.org/3/license.html) | PSF-2.0 and associated notices | External interpreter and standard library. |

The drawing compositor uses a system Arial/Courier font when available and falls back to DejaVu or Pillow's default font. Font binaries are not included. CI uses the operating system's DejaVu fonts. Generated Blender artwork is not automatically covered by Blender's GPL merely because Blender produced it; distribution of Blender or a combined GPL work would have its own obligations.

The runtime Python dependency inventory contains only Pillow; its optional dependency groups are not installed. Development/security scanners and GitHub Actions are external tooling, not shipped inside the model assets.

## Dimensional references

- [KeyV2 GMK-based Cherry profile](https://github.com/rsheldiii/KeyV2/blob/19f0d2faadd4949634c93f38d1a66869d29e8f43/src/key_profiles/cherry.scad): consulted for the R1 height expression and stem-inset caveat. No upstream source file or upstream mesh is included. Dimensions inform a custom design, not a certified replica.
- [Keycaps.info](https://www.keycaps.info/): visual comparison of keycap row silhouettes, not a manufacturing specification.

The project brief and visual reference are project-supplied design inputs. Cherry and GMK names identify the dimensional inspiration only; no affiliation, endorsement, or trademark rights are implied.
