import unittest
import os
import sys

import tests_helper as th
from occurrence import Occurrence

class OccurrenceTest(unittest.TestCase):

    def test_properties_not_set(self):

        time_stamp = 1615809234
        occ = Occurrence(1, 1, time_stamp, 'error')
        self.assertEqual(occ.id, 1)
        self.assertEqual(occ.item_id, 1)
        self.assertEqual(occ.timestamp, time_stamp)
        self.assertEqual(occ.level, 'error')
        self.assertEqual(occ.environment, Occurrence.DEFAULT_ENVIRONMENT)
        self.assertEqual(occ.code_version, Occurrence.DEFAULT_VERSION)


    def test_empty_environment(self):

        time_stamp = 1615809234
        occ_a = Occurrence(1, 1, time_stamp, 'error', environment=' ')
        self.assertEqual(occ_a.environment, Occurrence.DEFAULT_ENVIRONMENT)

        occ_b = Occurrence(1, 1, time_stamp, 'error', environment='')
        self.assertEqual(occ_b.environment, Occurrence.DEFAULT_ENVIRONMENT)

        occ_c = Occurrence(1, 1, time_stamp, 'error', environment=None)
        self.assertEqual(occ_c.environment, Occurrence.DEFAULT_ENVIRONMENT)

        occ_d = Occurrence(1, 1, time_stamp, 'error', environment='dev')
        self.assertEqual(occ_d.environment, 'dev')

        occ_e = Occurrence(1, 1, time_stamp, 'error', environment=' dev ')
        self.assertEqual(occ_e.environment, 'dev')

    
    def test_empty_code_version(self):

        time_stamp = 1615809234
        occ_a = Occurrence(1, 1, time_stamp, 'error', code_version=' ')
        self.assertEqual(occ_a.code_version, Occurrence.DEFAULT_VERSION)

        occ_b = Occurrence(1, 1, time_stamp, 'error', code_version='')
        self.assertEqual(occ_b.code_version, Occurrence.DEFAULT_VERSION)

        occ_c = Occurrence(1, 1, time_stamp, 'error', code_version=None)
        self.assertEqual(occ_c.code_version, Occurrence.DEFAULT_VERSION)

        occ_d = Occurrence(1, 1, time_stamp, 'error', code_version='1.0.1')
        self.assertEqual(occ_d.code_version, '1.0.1')

        occ_e = Occurrence(1, 1, time_stamp, 'error', code_version=' 1.0.1 ')
        self.assertEqual(occ_e.code_version, '1.0.1')


if __name__ == '__main__':
    unittest.main()