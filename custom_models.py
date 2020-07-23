from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA

class RandomForestPCA:
    def __init__(self, memory=None, **kwargs):
        # Define your pipeline here
        self.model = Pipeline(
            [
                ('pca', PCA(n_components=10)), 
                ('rf', RandomForestClassifier()),
            ],
        )

        # Assumes the algorithm is the final step the pipeline
        prefix = list(self.model.named_steps)[-1] + "__"
        # Adds the prefix of that last step to our param dict's keys
        # so we can access that step's parameters.
        newparams = {prefix + key: val for key, val in kwargs.items()}
        self.model.set_params(**newparams)

    def fit(self, X, y):
        return self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)
    