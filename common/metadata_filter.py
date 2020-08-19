class MetadataFilter:
    def __init__(self, filter_name, column_name, acceptable_values):
        self.filter_name = filter_name
        self.column_name = column_name
        self.acceptable_values = acceptable_values

    def __str__(self):
        return self.filter_name
