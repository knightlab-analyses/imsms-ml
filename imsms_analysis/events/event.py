class Event:
    def __init__(self):
        self.funcs = []

    def register(self, f):
        self.funcs.append(f)

    def __call__(self, *args, **kwargs):
        for f in self.funcs:
            f(*args, **kwargs)
