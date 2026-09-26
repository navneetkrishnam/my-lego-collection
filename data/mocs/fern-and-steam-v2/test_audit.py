import unittest
from audit import inspect_model


def box(key, x=0, y=0, z=0, w=2, d=2, h=1, studded=True):
    return dict(key=key, element='a', kind='box', x=x, y=y, z=z,
                w=w, d=d, h=h, studded=studded, step=1)


class ConstructionChecks(unittest.TestCase):
    def test_separated_component_is_reported(self):
        result=inspect_model([box('base'),box('floating',z=3)],{'a':2})
        self.assertEqual(result['connected_components'],2)

    def test_unsupported_tile_cannot_supply_studs(self):
        result=inspect_model([box('tile',studded=False),box('above',z=1)],{'a':2})
        self.assertEqual(result['connected_components'],2)

    def test_bridge_connects_two_foundation_plates(self):
        result=inspect_model([box('left'),box('right',x=2),box('bridge',x=1,z=1)],{'a':3})
        self.assertEqual(result['connected_components'],1)
        self.assertFalse(result['solid_body_overlaps'])

    def test_collision_and_shortage_fail_independently(self):
        result=inspect_model([box('one'),box('two',x=1)],{'a':1})
        self.assertEqual(result['shortages'],{'a':1})
        self.assertEqual(result['solid_body_overlaps'],[['one','two']])

    def test_half_stud_offset_is_not_a_stud_connection(self):
        result=inspect_model([box('base'),box('above',x=.5,z=1)],{'a':2})
        self.assertEqual(result['connected_components'],2)

    def test_declared_insert_offset_must_match_actual_pose(self):
        frame=box('frame');frame.update(element='4530590',kind='frame',matrix=[1,0,0,0,1,0,0,0,1],origin=[40,-72,10])
        pane=dict(key='pane',element='6514142',kind='insert',parent='frame',offset=[0,8,4],matrix=frame['matrix'],origin=[40,-64,14])
        self.assertFalse(inspect_model([frame,pane],{'4530590':1,'6514142':1})['invalid_inserts'])
        pane['origin'][2]+=1
        self.assertEqual(inspect_model([frame,pane],{'4530590':1,'6514142':1})['invalid_inserts'],['pane'])


if __name__=='__main__': unittest.main()
