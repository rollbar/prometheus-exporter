from occurrence import Occurrence

class ItemMetric:
    """
    Class to store the list of occurrences associated with a 
    single Rollbar Item
    Occurrences are
    """

    def __init__(self, item_id, occurrence_list):

        self.item_id = int(item_id)

        occ_list = [x for x in occurrence_list if x.item_id == self.item_id]
        self.occurrence_list = occ_list

        self.env_dict = {} 
        self.initialize_dict()

    def initialize_dict(self):

        # set just returns unique values in env_list
        env_list = [x.environment for x in self.occurrence_list]
        env_list = list(set(env_list))

        for env in env_list:
            self.env_dict[env] = None

    def process_item(self):

        # TODO FIXME - Confirm if levels will always be the 
        # TODO FIXME - same for all occurrences of an Item
        for env in self.env_dict:
            warning_list = [x for x in self.occurrence_list
                            if x.level == 'warning' if x.environment == env]

            error_list = [x for x in self.occurrence_list
                          if x.level == 'error' if x.environment == env]

            critical_list = [x for x in self.occurrence_list
                             if x.level == 'critical' if x.environment == env]

            level_dict  = {}
            level_dict['warning'] = len(warning_list)
            level_dict['error'] = len(error_list)
            level_dict['critical'] = len(critical_list)

            self.env_dict[env] = level_dict
