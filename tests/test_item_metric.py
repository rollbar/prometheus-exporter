import unittest
import os
import sys

import tests_helper as th

from item_metric import ItemMetric
from occurrence import Occurrence


class ItemMetricTest(unittest.TestCase):

    def test_environments(self):

        occ_list = th.get_occurrences_for_test()

        item_id = 2
        im = ItemMetric(item_id, occ_list)
        im.process_item()

        env_list = list(im.env_dict.keys())
        env_list.sort(reverse=True)
        self.assertEqual(len(env_list), 2, 'There should be 2 environments')
        self.assertEqual(env_list[0], 'prod', 'The environment should be prod')
        self.assertEqual(env_list[1], 'dev', 'The environment should be dev')
        
    def test_levels(self):

        occ_list = th.get_occurrences_for_test()

        im = ItemMetric(2, occ_list)
        im.process_item()

        levels = im.env_dict['dev']
        self.assertEqual(levels['warning'], 2, 'There should be 2 warnings')
        self.assertEqual(levels['error'], 1, 'There should be 1 error')
        self.assertEqual(levels['critical'], 1, 'There should be 1 critical')

if __name__ == '__main__':
    unittest.main()