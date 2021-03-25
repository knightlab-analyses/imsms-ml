from imsms_analysis.common.named_functor import NamedFunctor

# ARGH.  I need to pass seeds in the darn configs!!!
# _DOWNSAMPLE_SEED = 887969681  # This was the seed used for downsample 50
_DOWNSAMPLE_SEED = 1227215452  # This was the seed used for downsample 25


def build(num_training_samples):
    return NamedFunctor("Downsample Train Set: " + str(num_training_samples),
                        lambda state, mode: _downsample(state,mode,num_training_samples))


def _downsample(state, mode, num_samples):
    if mode != "train":
        return state
    # I would like to get the same subset every time I rerun the code with same
    # dataframe and number of samples, but I don't want the 100 set to be a
    # superset of the 50 set, so I change the random_state depending on number
    # of samples.
    df = state.df.sample(n=num_samples,
                         replace=False,
                         random_state=_DOWNSAMPLE_SEED + num_samples)
    return state.update_df(df)
