from occurrence import Occurrence

def get_occurrences_for_test():
        """
        returns: a list of Occurrence objects
        """

        lst = []

        # occ_id, item_id, time_msecs, level, environment, code_version
        lst.append(Occurrence(1001, 1,1614810103, 'error', 'dev', '1.0.1'))
        lst.append(Occurrence(1002, 1, 1615810103, 'error', 'dev', '1.0.2'))
        lst.append(Occurrence(1003, 1, 1615810103, 'error', 'dev', '1.0.2'))
        
        lst.append(Occurrence(1004, 2, 1614810103, 'warning', 'dev', '1.0.1'))
        lst.append(Occurrence(1005, 2, 1615810103, 'error', 'dev', '1.0.1'))
        lst.append(Occurrence(1006, 2, 1616810103, 'warning', 'dev', '1.0.3'))
        lst.append(Occurrence(1006, 2, 1616810103, 'critical', 'dev', '1.0.3'))

        lst.append(Occurrence(1104, 2, 1614810103, 'warning', 'prod', '1.0.1'))
        lst.append(Occurrence(1105, 2, 1615810103, 'error', 'prod', '1.0.1'))
        lst.append(Occurrence(1106, 2, 1616810103, 'warning', 'prod', '1.0.3'))

        lst.append(Occurrence(1007, 3, 1614810103, 'error', 'prod', '1.0.3'))
        lst.append(Occurrence(1008, 3, 1615810103, 'error', 'prod', '1.0.3'))
        lst.append(Occurrence(1009, 3, 1616810103, 'error', 'prod', '1.0.3'))

        lst.append(Occurrence(1010, 4, 1614810103, 'error', 'dev', '1.0.1'))
        lst.append(Occurrence(1011, 5, 1615810103, 'error', 'qa', '1.0.1'))
        lst.append(Occurrence(1012, 7, 1616810103, 'error', 'prod', '1.0.1'))

        lst.append(Occurrence(1013, 8,	1614810103, 'warning', 'dev', '1.0.1'))
        lst.append(Occurrence(1014, 8,	1615810103, 'warning', 'dev', '1.0.1'))
        lst.append(Occurrence(1015, 8,	1616810103, 'warning', 'dev', '1.0.1'))
  
        lst.append(Occurrence(1016, 9, 1614810103, 'critical', 'dev', '1.0.1'))
        lst.append(Occurrence(1017, 9, 1615810103, 'critical', 'dev', '1.0.2'))
        lst.append(Occurrence(1018, 9, 1616810103, 'critical', 'dev', '1.0.3'))

        lst.append(Occurrence(1019, 10, 1614810103, 'error', 'dev', '1.0.1'))

        return lst
