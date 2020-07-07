import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def simple_swarm(df: pd.DataFrame,
                 meta_df: pd.DataFrame,
                 value_column,
                 color_column):
    data = df[value_column].to_frame().join(meta_df[color_column])
    ax = sns.swarmplot(x=data[value_column],
                       y=data[color_column],
                       hue=data[color_column])
    plt.show()
