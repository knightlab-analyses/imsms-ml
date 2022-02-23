import csv
from collections import defaultdict
import pandas as pd
import numpy as np
import sqlite3


class FeatureTransformer:
    def __init__(self, name, transform_file, shuffle_seed=None):
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

        self.shuffle_seed = shuffle_seed

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

        # To enable permutation testing, if shuffle_seed is set, we will
        # shuffle rows in our transform matrix.
        if self.shuffle_seed:
            rand = np.random.default_rng(self.shuffle_seed)
            indices = transform_mat.index.tolist()
            rand.shuffle(indices)
            transform_mat.index = indices

        return df.dot(transform_mat)

    def __str__(self):
        return self.name


class NetworkTransformer:
    def __init__(self, name, transform_file, shuffle_seed=None):
        conn = sqlite3.connect("mimics.db")
        c = conn.cursor()

        self.genome_to_target = defaultdict()
        self.name = name
        self.all_targets = set([])
        with open(transform_file) as f:
            reader = csv.reader(f, delimiter='\t')
            header = True
            for row in reader:
                if header:
                    header = False
                    continue
                species_name, target = row
                c.execute("SELECT ncbi_id, genome_id, genus, species FROM genome WHERE species=?", (species_name,))
                ncbi_ids = c.fetchall()
                for rr in ncbi_ids:
                    ncbi_id = rr[0]
                    self.genome_to_target[ncbi_id] = target
                    self.all_targets.add(target)

        self.all_targets = sorted(list(self.all_targets))
        self.target_to_pos = {}
        for i in range(len(self.all_targets)):
            self.target_to_pos[self.all_targets[i]] = i
        self.shuffle_seed = shuffle_seed

    def _map_genome_id(self, genome_id):
        data = np.zeros(len(self.all_targets))
        if genome_id in self.genome_to_target:
            target = self.genome_to_target[genome_id]
            data[self.target_to_pos[target]] = 1
        return data

    def _build_transform_mat(self, genome_ids):
        rows = []
        index = []
        for genome_id in genome_ids:
            index.append(genome_id)
            row = self._map_genome_id(genome_id)
            rows.append(row)

        transform_mat = pd.DataFrame(
            np.array(rows),
            index=genome_ids,
            columns=self.all_targets
        )

        return transform_mat

    def transform_df(self, df):
        # df has rows corresponding to samples, and columns corresponding to
        # genome IDs.
        # We will build a matrix with rows of genome IDs and columns of mimics
        # Then we multiply

        transform_mat = self._build_transform_mat(df.columns)

        # To enable permutation testing, if shuffle_seed is set, we will
        # shuffle rows in our transform matrix.
        if self.shuffle_seed:
            rand = np.random.default_rng(self.shuffle_seed)
            indices = transform_mat.index.tolist()
            rand.shuffle(indices)
            transform_mat.index = indices

        return df.dot(transform_mat)

    def __str__(self):
        return self.name
