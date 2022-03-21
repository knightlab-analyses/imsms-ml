class TrainTest:
    pass


class Passthrough(TrainTest):
    def __init__(self):
        pass


class UnpairedSplit(TrainTest):
    def __init__(self, train_ratio=.5):
        self.train_ratio=train_ratio


