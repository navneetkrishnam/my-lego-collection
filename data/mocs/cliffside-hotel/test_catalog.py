import unittest
from catalog import apply_verified

class VerifiedQuantityTests(unittest.TestCase):
 def test_replaces_allowance_instead_of_adding(self):
  inv={'a':{'minimum':2,'sources':[{'set':'21341','copy':1,'quantity':1},{'set':'11111','copy':1,'quantity':1}]}}
  apply_verified(inv,{'21341':1},[{'element':'a','set':'21341','quantity':8,'printed_page':262}]);self.assertEqual(inv['a']['minimum'],9)
 def test_instruction_can_supply_missing_cached_membership(self):
  inv={'a':{'minimum':1,'sources':[{'set':'11111','copy':1,'quantity':1}]}}
  apply_verified(inv,{'21341':1},[{'element':'a','set':'21341','quantity':4,'printed_page':262}]);self.assertEqual(inv['a']['minimum'],5);self.assertEqual(len(inv['a']['sources']),2)
 def test_cannot_add_unowned_donor(self):
  self.assertRaises(ValueError,apply_verified,{'a':{'minimum':0,'sources':[]}},{},[{'element':'a','set':'21341','quantity':4,'printed_page':262}])
if __name__=='__main__':unittest.main()
