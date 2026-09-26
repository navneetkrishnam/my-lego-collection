import unittest
from engine import Model

def fixture():
 p=dict(element='a',bl_part='3020',ldraw='3020.dat',ldraw_color=0,kind='plate',w=4,d=2,h=1,studded=True,minimum=1,sources=[dict(set='12345',copy=1,quantity=1)])
 return {'parts':{'a':p},'preferred':{'3020:0':'a'}}

class PlacementTests(unittest.TestCase):
 def test_single_course_fill_excludes_tall_bricks(self):
  s=fixture();s['parts']['a'].update(kind='brick',h=9)
  m=Model(s);self.assertRaises(ValueError,m.fill,{(x,y) for x in range(4) for y in range(2)},0,['brick'],[0])
  self.assertEqual(m.pieces,[])
 def test_wall_preserves_singles_when_larger_palette_piece_fits(self):
  s=fixture();s['parts']={}
  for e,w,c,n in [('a',1,15,4),('b',4,19,1)]:
   s['parts'][e]=dict(element=e,ldraw_color=c,kind='brick',w=w,d=1,h=3,studded=True,minimum=n)
  s['preferred']={'single:15':'a','long:19':'b'}
  m=Model(s);m.wall(0,0,4,0,6,holes=[(0,0,4,1)],panels=False)
  self.assertEqual([q['element'] for q in m.pieces],['b'])
 def test_rejects_shortage_without_consuming_or_adding(self):
  m=Model(fixture());m.put('a',0,0,0);self.assertRaises(ValueError,m.put,'a',4,0,0);self.assertEqual(len(m.pieces),1);self.assertEqual(m.remaining['a'],0)
 def test_turn_rotates_footprint_and_keeps_bottom(self):
  p=Model(fixture()).put('a',3,5,2,turn=True);self.assertEqual((p['w'],p['d']),(2,4));self.assertEqual(p['origin'],[80,-24,140]);self.assertEqual(p['matrix'],[0,0,1,0,1,0,-1,0,0])
 def test_fill_never_crosses_hole(self):
  m=Model(fixture());self.assertRaises(ValueError,m.fill,{(0,0),(1,0),(2,0)},0,['plate'],[0]);self.assertEqual(len(m.pieces),0)

if __name__=='__main__':unittest.main()
