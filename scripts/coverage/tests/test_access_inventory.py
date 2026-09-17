import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('inventory', Path(__file__).resolve().parents[1] / 'audit_access_inventory.py')
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)

class InventorySafetyTests(unittest.TestCase):
    def point(self, **tags):
        return {'lat': 43.15, 'lng': -2.75, 'tags': tags}

    def test_no_road_does_not_imply_free_or_private(self):
        self.assertIsNone(inventory.explicit_exclusion(self.point(barrier='toll_booth'), []))

    def test_a_parking_lane_does_not_hide_a_public_incident_road(self):
        ways = [{'tags': {'service': 'parking_aisle'}}, {'tags': {'highway': 'primary'}}]
        self.assertIsNone(inventory.explicit_exclusion(self.point(), ways))

    def test_specific_motorcar_permission_wins_over_generic_access(self):
        self.assertIsNone(inventory.explicit_exclusion(self.point(access='private', motorcar='yes'), []))

    def test_heavy_goods_tag_alone_is_not_car_exemption(self):
        self.assertIsNone(inventory.explicit_exclusion(self.point(), [{'tags': {'ref': 'AP-8', 'toll:hgv': 'yes'}}]))

    def test_documented_n240_scope_excludes_light_cars(self):
        self.assertEqual(inventory.explicit_exclusion(self.point(), [{'tags': {'ref': 'N-240'}}])[0], 'heavy_goods_only')

    def test_provenance_never_mistakes_way_ids_or_fares_for_nodes(self):
        self.assertEqual(list(inventory.source_nodes({'way': 42, 'cents': 100, 'node': 7, 'gates': [{'booths': [8, '9']}]})), [7, 8, 9])

    def test_crossing_does_not_match_parallel_or_disjoint_lines(self):
        self.assertTrue(inventory.intersects([0,0], [0,1], [-1,.5], [1,.5]))
        self.assertFalse(inventory.intersects([0,0], [0,1], [0,2], [0,3]))
        self.assertFalse(inventory.intersects([0,0], [0,1], [-1,2], [1,2]))

if __name__ == '__main__':
    unittest.main()
