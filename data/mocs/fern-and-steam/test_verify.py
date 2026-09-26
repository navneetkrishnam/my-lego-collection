import unittest
from verify import conservative_inventory, check_model


def piece(key, x=0, y=0, z=0, w=1, d=1, h=1, studded=True, step=1):
    return dict(key=key, element='A', x=x, y=y, z=z, w=w, d=d, h=h,
                studded=studded, step=step, kind='box')


class VerificationTests(unittest.TestCase):
    def test_duplicate_rows_do_not_create_pieces_but_two_boxes_do(self):
        inv, invalid = conservative_inventory({'10000': 2, '20000': 1},
            {'10000': [{'id': 'A'}, {'id': 'A'}, {'id': None}],
             '20000': [{'id': 'A'}, {'id': 'B'}]})
        self.assertEqual(inv['A']['minimum'], 3)
        self.assertEqual(inv['B']['minimum'], 1)
        self.assertEqual(invalid, 1)

    def test_shortage_and_unknown_identity_do_not_pass(self):
        ps = [piece('a'), piece('b', x=1)]
        result = check_model(ps, {'A': {'minimum': 1}}, (16, 16))
        self.assertEqual(result['shortages'], {'A': 1})
        ps[1]['element'] = 'unknown'
        self.assertEqual(check_model(ps, {'A': {'minimum': 1}}, (16, 16))['shortages'], {'unknown': 1})

    def test_collision_detected(self):
        self.assertEqual(len(check_model([piece('a'), piece('b')], {'A': {'minimum': 2}}, (16, 16))['overlaps']), 1)

    def test_floating_and_tile_supported_parts_fail(self):
        for bottom in [piece('a', studded=False), piece('a')]:
            top = piece('b', z=1 if not bottom['studded'] else 2)
            self.assertIn('b', check_model([bottom, top], {'A': {'minimum': 2}}, (16, 16))['unsupported'])

    def test_bridge_connects_foundation_and_is_supported(self):
        ps = [piece('a'), piece('b', x=1), piece('bridge', z=1, w=2, step=2)]
        result = check_model(ps, {'A': {'minimum': 3}}, (16, 16))
        self.assertEqual(result['components'], 1)
        self.assertEqual(result['unsupported'], [])
        self.assertEqual(result['overlaps'], [])

    def test_touching_side_faces_are_not_connections(self):
        result = check_model([piece('a'), piece('b', x=1)], {'A': {'minimum': 2}}, (16, 16))
        self.assertEqual(result['components'], 2)

    def test_overhead_piece_blocks_later_downward_insertion(self):
        ps = [piece('base', w=2), piece('post', x=1, z=1, h=2, step=2),
              piece('roof', z=3, w=2, step=3), piece('late', z=1, step=4)]
        result = check_model(ps, {'A': {'minimum': 4}}, (16, 16))
        self.assertIn(['late', 'roof'], result['blocked_insertions'])

    def test_out_of_bounds_is_reported(self):
        self.assertEqual(check_model([piece('a', x=16)], {'A': {'minimum': 1}}, (16, 16))['out_of_bounds'], ['a'])


if __name__ == '__main__':
    unittest.main()
