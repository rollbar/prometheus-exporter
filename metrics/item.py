class Item:

    def __init__(self, item_id, level, count,
                 environment='none', code_version='not_defined'):
        
        self.id = int(item_id)
        self.level = level
        self.count = count
        self.environment = environment
        self.code_version = code_version