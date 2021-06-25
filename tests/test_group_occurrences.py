import unittest
import os
import group_occurrences as go
import tests_helper as th
from item_metric import ItemMetric


class GroupOccurrencesTest(unittest.TestCase):

    def __init__(self, methodName):
        super().__init__(methodName)

        self.SLUG = 'unit_test'
        self.TEST_OCCURRENCE_ID = '155711003766'

    def setUp(self):
        self.remove_slug_file()

        file_path = go.get_project_file(self.SLUG) 
        with open(file_path, mode='w') as f:
            f.write(self.TEST_OCCURRENCE_ID)

    def tearDown(self):
        self.remove_slug_file()

    def remove_slug_file(self):
        """
        delete ../metrics/unit_test.txt file if it exists
        """
        file_path = go.get_project_file(self.SLUG)

        if os.path.isfile(file_path):
            os.remove(file_path)

    def test_get_project_file(self):
        file_path = go.get_project_file(self.SLUG)

        path = os.path.dirname(os.path.realpath(__file__))
        if not path.endswith('/tests'):
            raise ValueError('File path expected to end with "/tests"')

        expected_file_path = path.replace('/tests', '/metrics/unit_test.txt')
        self.assertEqual(file_path, expected_file_path)

    def test_read_starting_occ_from_file(self):

        starting_occ_id  = go.read_starting_occ_from_file(self.SLUG)
        self.assertEqual(str(starting_occ_id), self.TEST_OCCURRENCE_ID)

    def test_get_item_occurrences(self):

        occ_list = th.get_occurrences_for_test()
        metrics_dict = go.get_item_metrics_for_occurrences(occ_list)
        self.assertEqual(len(metrics_dict.keys()), 9)

        metric: ItemMetric
        metric = metrics_dict['3']
        self.assertEqual(len(metric.env_dict.keys()), 1)
        self.assertEqual(metric.env_dict['prod']['error'], 3)

    
    def test_occurrences_in_versions(self):

        occ_list = th.get_occurrences_for_test()
        versions_dict = go.group_occurrences_into_versions(occ_list)

        lst = versions_dict.keys()

        self.assertEqual(len(lst), 3)
        self.assertEqual(len(lst), 3)

    def test_item_grouping(self):

        occ_list = th.get_occurrences_for_test()
        items = go.group_occurrences_into_items(occ_list)

        item_ids = items.keys()

        self.assertEqual(len(item_ids), 9)

        item_metric = items['7']
        self.assertEqual(item_metric.env_dict['prod']['error'], 1)
        self.assertEqual(item_metric.env_dict['prod']['warning'], 0)
        self.assertEqual(item_metric.env_dict['prod']['critical'], 0)


if __name__ == '__main__':
    unittest.main()