import numpy as np
import pandas as pd

# Author: Daniel Hakim


class SetJoiner:
    """
    SetJoiner is responsible for creating sets by joining pairs
    It should be a familiar implementation of the merge step in Kruskal's
    algorithm.
    """
    def __init__(self, initial_groups):
        self.group_pointers = {g: g for g in initial_groups}

    def top(self, group):
        cur = group
        while self.group_pointers[cur] != cur:
            cur = self.group_pointers[cur]
        return cur

    def merge(self, a, b):
        top_a = self.top(a)
        top_b = self.top(b)
        new_top = top_a if top_a < top_b else top_b
        for cur in [a, b]:
            curs = [cur]
            while self.group_pointers[cur] != cur:
                cur = self.group_pointers[cur]
                curs.append(cur)
            for g in curs:
                self.group_pointers[g] = new_top

    def get_sets(self):
        sets = {}
        for g in self.group_pointers:
            rep = self.top(g)
            if rep not in sets:
                sets[rep] = set()
            sets[rep].add(g)
        return sets


# Sort df's columns so that set representatives are the gotu with highest
# total read count, then run pairwise_pearson.
def pairwise_pearson(df, thresh=0.95):
    col_sums = df.sum()
    col_sums.name = 'total'
    col_sums = col_sums.sort_values(ascending=False)
    df = df[col_sums.index]
    return _pairwise_pearson(df, thresh)


# Apply pairwise pearson- this finds highly correlated columns and merges them.
# name of the merged column is assigned as the leftmost of the merged columns.
def _pairwise_pearson(filtered_df, thresh=0.95):
    # Make a correlation matrix (slowest step)
    corr_mat = filtered_df.corr()

    # Take lower triangle
    corr_mat = corr_mat.where((np.tril(np.ones(corr_mat.shape)) -
                               np.identity(corr_mat.shape[0])).astype(np.bool))

    # Find cells above threshold
    to_collapse = (corr_mat.max(axis=1) > thresh)

    # Of cells above threshold, find highest
    to_collapse_to = corr_mat.idxmax(axis=1)
    to_collapse_to = to_collapse_to.where(to_collapse)

    # Number columns from 1 to n
    converter = {}
    for i in range(len(to_collapse_to.index)):
        converter[to_collapse_to.index[i]] = i

    # For cells above threshold, merge row and column, merge towards leftmost
    # column
    merger = SetJoiner(range(len(to_collapse_to.index)))
    for col1, col2 in to_collapse_to.items():
        if isinstance(col2, str):
            c1 = converter[col1]
            c2 = converter[col2]
            merger.merge(c1, c2)

    # Grab the result sets indexed by their set representatives
    conv_sets = merger.get_sets()

    # rename sets
    sets = {}
    for conv_rep in conv_sets:
        rep = to_collapse_to.index[conv_rep]
        conv_rep_set = conv_sets[conv_rep]
        rep_set = set([to_collapse_to.index[r] for r in conv_rep_set])
        sets[rep] = rep_set

    # Collapse gotus in each set to their set representative
    out_cols = {}
    for rep in sets:
        out_col = filtered_df[list(sets[rep])].sum(axis=1)
        out_col.name = rep
        out_cols[rep] = out_col
    return pd.DataFrame(out_cols), sets
