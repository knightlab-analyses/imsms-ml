class TrainTest:
    pass


class Passthrough(TrainTest):
    def __init__(self):
        pass


class PairedSplit(TrainTest):
    def __init__(self, train_ratio=.5):
        self.train_ratio = train_ratio

    def __str__(self):
        return "train" + str(int(self.train_ratio * 100)) + "_paired"


class UnpairedSplit(TrainTest):
    def __init__(self, train_ratio=.5):
        self.train_ratio = train_ratio


class SplitByMetadata(TrainTest):
    def __init__(self, meta_col, train_meta):
        self.meta_col = meta_col
        self.train_meta = train_meta

    def __str__(self):
        return self.meta_col + "_" + "_".join(self.train_meta)
