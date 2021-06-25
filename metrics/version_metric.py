
from occurrence import Occurrence
from item import Item

class VersionMetric:

    def __init__(self, code_version, occurrence_list):

        self.code_version = str(code_version)

        occ_list = [x for x in occurrence_list 
                    if x.code_version == self.code_version]
        self.occurrence_list = occ_list

        # groups occurrences by environment for a given version
        self.version_dict = {} 
        self.env_list = []
        self.env_dict = {}

        # groups occurrences by environment-item_id for a given version
        self.version_item_dict = {}

        self.initialize()


    def initialize(self):

        env_list = [x.environment for x in self.occurrence_list]
        self.env_list = list(set(env_list))

        for env in self.env_list:
            self.env_dict[env] = None


    def process_version(self):
        """
        adds all occurrences for a a particular for version to 
        self.versions_dict key=code_version, value=list of occurrences
        """

        for env in self.env_list:
            occs_in_env = [x for x in self.occurrence_list if x.environment == env]
            self.env_dict[env] = self.process_occurrence_list(occs_in_env)

        for env in self.env_list:
            occs_in_env = [x for x in self.occurrence_list if x.environment == env]
            item_id_list = self.get_unique_item_list(occs_in_env)

            self.version_item_dict = {}
            for item_id in item_id_list:
                occs_for_item = [x for x in occs_in_env if x.item_id == item_id]

                item = self.create_item(occs_for_item)
                key = '{}_{}'.format(item.environment, item_id)
                self.version_item_dict[key] = item


    def create_item(self, occs_for_item):
        """
        capture interesting information about the occurrences of an item
        """

        if len(occs_for_item) == 0:
            return {}

        # assumes the level is the same for all occurrences
        first_occ: Occurrence
        first_occ = occs_for_item[0]


        item = Item(first_occ.item_id, first_occ.level, len(occs_for_item),
                    first_occ.environment, first_occ.code_version)
        
        return item
        

    def process_occurrence_list(self, occ_list_for_env):
        """
        for a given occurrence list return a dictionary with the following

        returns: warning_occurrences list
                 error_occurrences list
                 critical occurrences list

                 warning_items count
                 error_items count
                 critical_items count
        """

        values_dict = {}
        warning_list = [x for x in occ_list_for_env
                        if x.level == 'warning']
        if len(warning_list) > 0:
            values_dict['warning_occurrences'] = len(warning_list)

        error_list = [x for x in occ_list_for_env
                        if x.level == 'error']
        if len(error_list) > 0:
            values_dict['error_occurrences'] = len(error_list)

        critical_list = [x for x in occ_list_for_env
                            if x.level == 'critical']
        if len(critical_list) > 0:
            values_dict['critical_occurrences'] = len(critical_list)

        # capture item counts for warning, error, critical
        warning_items = [x.item_id for x in warning_list]
        num_items = len(list(set(warning_items)))
        if num_items > 0:
            values_dict['warning_items'] = num_items

        error_items = [x.item_id for x in error_list]
        num_items = len(list(set(error_items)))
        if num_items > 0:
            values_dict['error_items'] = num_items

        critical_items = [x.item_id for x in critical_list]
        num_items = len(list(set(critical_items)))
        if num_items > 0:
            values_dict['critical_items'] = num_items

        return values_dict


    def get_unique_item_list(self, occ_list):

        item_list = [x.item_id for x in occ_list]
        item_list = list(set(item_list))

        return item_list

