import unittest
from engine import Model
from audit import inspect

def fixture():
 p=dict(element='a',bl_part='3003',ldraw_color=15,kind='brick',w=2,d=2,h=3,studded=True,minimum=4)
 return dict(parts={'a':p},preferred={'3003:15':'a'})

class AuditTests(unittest.TestCase):
 def test_floating_piece_is_rejected(self):
  m=Model(fixture());m.put('a',0,0,0);m.put('a',0,0,4)
  self.assertFalse(inspect(m.pieces,m.snapshot)['digital_checks_pass'])
 def test_overlapping_bodies_are_rejected(self):
  m=Model(fixture());m.put('a',0,0,0);m.put('a',1,0,0)
  self.assertTrue(inspect(m.pieces,m.snapshot)['ordinary_body_overlaps'])
 def test_stacked_bricks_connect(self):
  m=Model(fixture());m.put('a',0,0,0);m.put('a',0,0,3)
  self.assertTrue(inspect(m.pieces,m.snapshot)['digital_checks_pass'])

if __name__=='__main__':unittest.main()
