"""Regression checks for concrete accessory contacts found in geometry review."""
import math
import unittest
from model import author


def transform(p, vertex):
    x,down,front=vertex
    angle=math.radians(p['rotation'])
    return (p['x']+p['w']/2+(x*math.cos(angle)+front*math.sin(angle))/20,
            p['y']+p['d']/2+(-x*math.sin(angle)+front*math.cos(angle))/20,
            p['z']+p['h']-down/8)


class AccessoryRegressionTests(unittest.TestCase):
    def test_low_handle_point_clears_structural_bodies_and_studs(self):
        # Official s/3899s01.dat: front handle includes local (0,16,20).
        ps=author()
        for mug in (p for p in ps if p['kind']=='mug'):
            x,y,z=transform(mug,(0,16,20))
            for box in (p for p in ps if p['kind']=='box'):
                inside=box['x']<x<box['x']+box['w'] and box['y']<y<box['y']+box['d'] and box['z']<z<box['z']+box['h']
                self.assertFalse(inside,f"{mug['key']} handle intersects {box['key']}")
                if box['studded'] and box['z']+box['h']<z<box['z']+box['h']+.5:
                    for i in range(box['w']):
                        for j in range(box['d']):
                            distance=math.hypot(x-(box['x']+i+.5),y-(box['y']+j+.5))
                            self.assertGreaterEqual(distance,.3,f"{mug['key']} handle lies inside a stud on {box['key']}")

    def test_rear_leaf_vertex_clears_furniture(self):
        # A vertex in official 32607.dat that intersected the first bench draft.
        ps=author()
        for leaf in (p for p in ps if p['kind']=='leaf'):
            x,y,z=transform(leaf,(-.8,1.5,-25.8))
            for box in (p for p in ps if p['kind']=='box'):
                inside=box['x']<x<box['x']+box['w'] and box['y']<y<box['y']+box['d'] and box['z']<z<box['z']+box['h']
                self.assertFalse(inside,f"{leaf['key']} leaf intersects {box['key']}")


if __name__=='__main__':unittest.main()
