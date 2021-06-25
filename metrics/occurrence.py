class Occurrence:
    """
    A very light object that contains basic information about
    each ocurrence. 

    id of the occurrence
    item_id
    times of the occurrence
    level - warning, error, critical
    environment
    code_version
    """

    DEFAULT_ENVIRONMENT = 'none'
    DEFAULT_VERSION = 'not_defined'

    def __init__(self, occ_id, item_id, timestamp, level,
                 environment=DEFAULT_ENVIRONMENT,
                 code_version=DEFAULT_VERSION):

        self.id = occ_id
        self.item_id = item_id
        self.timestamp = timestamp
        self.level = level

        self.environment = \
            Occurrence.reformat_values(environment, Occurrence.DEFAULT_ENVIRONMENT)

        self.code_version = \
            Occurrence.reformat_values(code_version,  Occurrence.DEFAULT_VERSION)

    @staticmethod
    def reformat_values(value, default):

        if value is None:
            value = str(default)

        value = str(value)
        value = value.strip()
        if value == str(''):
            value = str(default)

        return value

    def __str__(self):

        msg = 'Occurrence id={} item_id={} '
        msg = msg + ' timestamp={} level={}'
        msg = msg + ' environment={} code_version={}'
        msg = msg.format(self.id, self.item_id, 
                         self.timestamp, self.level,
                         self.environment, self.code_version)
        
        return msg