"""Check the distributed files and independently inspect their binary STL meshes."""
import ast
from collections import Counter
import json
import math
from pathlib import Path
import re
import struct
import unittest
from urllib.parse import unquote
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'
HEIGHTS={'00_BASE_FIT_TEST.stl':9.8,'01_ARCH_DOME.stl':12.3,'02_ZIGZAG_CYLINDER.stl':11.45,'03_DISC_RAILS.stl':11.3,'04_STAIR_SILHOUETTE.stl':11.45}


class ReleaseTests(unittest.TestCase):
    def test_source_syntax(self):
        for path in ROOT.glob('*.py'):
            with self.subTest(path=path.name): ast.parse(path.read_text(),filename=str(path))

    def test_source_geometry_report(self):
        report=json.loads((OUT/'Geometry_Check.json').read_text())
        self.assertTrue(report['pass'])
        self.assertEqual(len(report['objects']),33)
        self.assertEqual(len(report['engineering_checks']),4)
        for check in report['engineering_checks']:
            self.assertTrue(check['pass'])
            self.assertAlmostEqual(check['base_height_mm'],9.8,places=3)
            self.assertEqual(check['roof_rib_count'],4)
            self.assertAlmostEqual(check['socket_seat_z_mm'],5.1,places=3)
            self.assertAlmostEqual(check['socket_mouth_z_mm'],.4,places=3)

    def test_current_drawing_set(self):
        rows=json.loads((OUT/'drawings'/'dimensions.json').read_text())
        self.assertEqual(len(rows),4)
        paths=list((OUT/'drawings').glob('[0-9][0-9]_*.png'))
        self.assertEqual(len(paths),4)
        for row in rows:
            self.assertAlmostEqual(row['shell_height_mm'],9.8,places=3)
            path=OUT/'drawings'/(row['number']+'_'+row['slug']+'.png')
            with Image.open(path) as im:
                self.assertEqual(im.size,(2400,1800)); im.verify()
        self.assertLessEqual({p.name for p in OUT.iterdir() if p.is_dir()},{'drawings','print'})

    def test_renders_and_scene(self):
        for name in ('Memphis_Artisans.png','Memphis_Top.png','Memphis_Underside.png'):
            with Image.open(OUT/name) as im:
                self.assertGreaterEqual(min(im.size),900); im.verify()
        data=(OUT/'Memphis_Artisans.blend').read_bytes()
        self.assertTrue(data.startswith(b'BLENDER'))
        self.assertIsNone(re.search(rb'/Users/[A-Za-z0-9._-]+|/home/(?!runner\b)[A-Za-z0-9._-]+',data))

    def test_print_report(self):
        report=json.loads((OUT/'print'/'Print_Check.json').read_text())
        self.assertTrue(report['pass']); self.assertFalse(report['physical_fit_validated'])
        self.assertEqual(report['units'],'mm')
        self.assertEqual({r['file'] for r in report['files']},set(HEIGHTS))
        for row in report['files']:
            self.assertTrue(row['pass']); self.assertEqual(row['connected_components'],1)
            self.assertEqual(row['non_manifold_edges'],0); self.assertEqual(row['degenerate_triangles'],0)

    def test_stl_files_independently(self):
        self.assertEqual({p.name for p in (OUT/'print').glob('*.stl')},set(HEIGHTS))
        for filename,height in HEIGHTS.items():
            with self.subTest(file=filename):
                data=(OUT/'print'/filename).read_bytes()
                count=struct.unpack('<I',data[80:84])[0]
                self.assertGreater(count,100)
                self.assertEqual(len(data),84+50*count)
                edges=Counter(); oriented=Counter(); points=set(); volume=0.0
                for row in struct.iter_unpack('<12fH',data[84:]):
                    self.assertTrue(all(math.isfinite(v) for v in row[:12]))
                    a,b,c=(tuple(row[i:i+3]) for i in (3,6,9))
                    self.assertEqual(len({a,b,c}),3)
                    points.update((a,b,c))
                    ab=[b[i]-a[i] for i in range(3)]; ac=[c[i]-a[i] for i in range(3)]
                    cross=(ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0])
                    self.assertGreater(sum(v*v for v in cross),0)
                    volume+=a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0])
                    for p,q in ((a,b),(b,c),(c,a)):
                        edges[tuple(sorted((p,q)))]+=1; oriented[(p,q)]+=1
                self.assertTrue(all(n==2 for n in edges.values()))
                self.assertTrue(all(oriented[(q,p)]==n for (p,q),n in oriented.items()))
                self.assertGreater(volume/6,0)
                mins=[min(p[i] for p in points) for i in range(3)]
                maxs=[max(p[i] for p in points) for i in range(3)]
                for actual,expected in zip([b-a for a,b in zip(mins,maxs)],[18,18,height]):
                    self.assertAlmostEqual(actual,expected,places=3)
                self.assertAlmostEqual(mins[2],0,places=4)

    def test_document_links(self):
        docs=list(ROOT.glob('*.md'))+list((ROOT/'.github').glob('*.md'))
        for path in docs:
            for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',path.read_text()):
                if '://' in target or target.startswith(('#','mailto:')): continue
                local=unquote(target.split('#',1)[0])
                with self.subTest(document=path.name,link=local):
                    self.assertTrue((path.parent/local).exists())


if __name__=='__main__': unittest.main()
