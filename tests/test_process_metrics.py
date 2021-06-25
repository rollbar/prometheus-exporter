import unittest
import os
import sys

import tests_helper as th
from process_metrics import ProcessMetrics

class ProcessMetricsTest(unittest.TestCase):

    def __init__(self, methodName):
        super().__init__(methodName)
        return

    def setUp(self):
        return

    def tearDown(self):
        return
    
    def test_get_project_file(self):

        pm = ProcessMetrics()

        item_dict = {}
        version_dict = {}
        pm.self.get_metrics_for_project('abc', item_dict, version_dict)
        metrics = pm.generate_latest_metrics()


        print(metrics)

        self.assertEqual(1, 1)

if __name__ == '__main__':
    unittest.main()