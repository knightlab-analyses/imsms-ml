from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import TruncatedSVD


class RandomForestSVD:

    # Set estimator type for this class as one of either:
    # "classifier" or "regressor"
    _estimator_type = "classifier"

    def __init__(self, memory=None, **kwargs):
        # Define your pipeline here
        self.model = Pipeline(
            [
                ('dim_reduction', TruncatedSVD(n_components=10)), 
                ('rf', RandomForestClassifier()),
            ],
        )

        # Assumes the estimator is the final step of the pipeline, 
        # as given in the user documentation: 
        # https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html
        # Adds the prefix of that last step to our param dict's keys
        # so we can access that step's parameters.
        prefix = list(self.model.named_steps)[-1] + "__"
        newparams = {prefix + key: val for key, val in kwargs.items()}
        self.model.set_params(**newparams)

    def fit(self, X, y):
        return self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    # Defined only for certain classifier estimators
    def predict_proba(self, X):
        return self.model.predict_proba(X)
