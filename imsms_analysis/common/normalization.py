class Normalization:
    def __init__(self, filter_name, method, **kwargs):
        self.filter_name = filter_name
        self.method = method
        self.kwargs = kwargs

    def __str__(self):
        return self.filter_name


Normalization.DEFAULT = Normalization("Divide10000",
                                      "divide_total",
                                      target_count=10000)

Normalization.FRACTION = Normalization("Divide1",
                                       "divide_total",
                                       target_count=1)

Normalization.ASIN_SQRT = Normalization("Asin(Sqrt(Rel_ab))",
                                        "asin_sqrt")

Normalization.CLR = Normalization("CLR", "CLR")

Normalization.NONE = Normalization("None", "none")
