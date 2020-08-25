class NamedFunctor:
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __str__(self):
        return "Functor("+self.name+")"

    def __repr__(self):
        return "Functor("+self.name+")"
