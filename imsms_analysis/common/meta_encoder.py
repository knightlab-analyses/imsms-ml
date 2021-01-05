class MetaEncoder:
    def __init__(self, col_name, encoder):
        self.col_name = col_name
        self.encoder = encoder

    def __str__(self):
        return "Meta(" + self.col_name + ")"
