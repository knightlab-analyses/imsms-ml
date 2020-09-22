import csv
from collections import defaultdict
import pandas as pd
import numpy as np


class FeatureTransformer:
    def __init__(self, name, transform_file):
        self.genome_to_mimics = defaultdict(list)
        self.name = name
        self.all_mimics = set([])
        with open(transform_file) as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                ncbi_id, genome_id, mimics = row
                mimics = mimics.split(';')
                self.genome_to_mimics[genome_id] = mimics
                for mimic in mimics:
                    self.all_mimics.add(mimic)

        self.all_mimics = sorted(list(self.all_mimics))
        self.mimic_to_pos = {}
        for i in range(len(self.all_mimics)):
            self.mimic_to_pos[self.all_mimics[i]] = i

    def _map_genome_id(self, genome_id):
        mimics = self.genome_to_mimics[genome_id]
        data = np.zeros(len(self.all_mimics))
        for m in mimics:
            data[self.mimic_to_pos[m]] = 1
        return data

    def _build_transform_mat(self, genome_ids):
        rows = []
        for genome_id in genome_ids:
            row = self._map_genome_id(genome_id)
            rows.append(row)

        transform_mat = pd.DataFrame(
            np.array(rows),
            index=genome_ids,
            columns=self.all_mimics
        )

        return transform_mat

    def transform_df(self, df):
        # df has rows corresponding to samples, and columns corresponding to
        # genome IDs.
        # We will build a matrix with rows of genome IDs and columns of mimics
        # Then we multiply

        transform_mat = self._build_transform_mat(df.columns)
        return df.dot(transform_mat)

    def __str__(self):
        return self.name
