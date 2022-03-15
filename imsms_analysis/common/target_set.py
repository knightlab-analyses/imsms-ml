import pandas as pd
from itertools import chain, combinations


class TargetSet:
    def __init__(self, name, target_col, target_set):
        self.name = name
        self.target_col = target_col
        self.target_set = target_set

    def __str__(self):
        return self.name
