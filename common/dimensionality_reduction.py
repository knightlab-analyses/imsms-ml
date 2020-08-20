class DimensionalityReduction:
    def __init__(self, filter_name, transform, **kwargs):
        self.filter_name = filter_name
        self.transform = transform
        self.kwargs = kwargs

    def __str__(self):
        return self.filter_name
