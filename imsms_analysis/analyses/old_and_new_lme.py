from imsms_analysis.analysis_runner import SerialRunner, DryRunner, TableRunner
from imsms_analysis.common.PairwisePearson import pairwise_pearson
from imsms_analysis.common.analysis_factory import AnalysisFactory, \
    MultiFactory
from imsms_analysis.common.metadata_filter import MetadataFilter
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable, CSVTable
from imsms_analysis.common.train_test import SplitByMetadata, \
    PairedSplit, Passthrough
from imsms_analysis.common.woltka_metadata import filter_and_sort_df
from imsms_analysis.dataset.feature_transforms.feature_transformer import \
    ChainedTransform, RelativeAbundanceFilter, PairwisePearsonTransform
import seaborn as sns
from matplotlib import pyplot as plt
import statsmodels.api as sm
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("TkAgg")

# Reproducing xiaoyuan's models:
# Differential microbiome features by mixed linear regression analysis
# Global metabolite intensity and SCFA concentration were normalized by log transformation. Mixed linear regression model was applied
# on transformed data to identify differential features (species, pathways and metabolites) by adjusting random effects of house and
# recruitment site, and fixed effects of age, sex and BMI. The linear regression was performed using lmer function from R package
# ‘‘lme4’’ as lmer(y  disease + age + BMI + sex + (1|site) + (1|house)). To reduce the effect of zero-inflation in microbiome data, a variance
# filtering step was applied to remove species features with very low variance (<1 3 105
# ). The contribution of individual species in a specific pathway was visualized in a bar plot using HUMAnN2
# ‘‘humann2_barplot’’ function. Altered metabolites were linked to gut microbes through reactions
# (MetaCyc and KEGG) mediated by microbial gene families screened in our WGMS data using
# HUMANnN2. Functional KEGG enrichment analysis of metabolites was performed using MetaboAnalyst 5.0 (Pang et al., 2021).
# To identify species associated with disease severity, the updated global Multiple Sclerosis Severity Score (uGMSSS) was calcu-
# lated by combining the EDSS and disease duration using global_msss function from R package ‘‘ms.sev’’. We focused on the species
# with prevalence in more than 50% samples, spearman correlations were calculated and tested adjusting for age and BMI using
# pcor.test function from R package ‘‘ppcor’’.

old_metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
new_metadata_filepath = "./dataset/metadata/qiita_metadata_filtered.tsv"
combined_metadata_filepath = "./dataset/metadata/combined_iMSMS_metadata.tsv"


def get_species(woltka_meta_df, gotu):
    return woltka_meta_df[woltka_meta_df["#genome"] == gotu]["species"].iloc[0]

def get_genome_ids_for_species(woltka_meta_df, species):
    return woltka_meta_df[woltka_meta_df["species"] == species]["#genome"].values

def get_xiaoyuan_top_hits(woltka_meta_df):
    xz_species = \
        [
            "Firmicutes bacterium CAG:65",
            "FIrmicutes bacterium CAG:270",
            "Fusicatenibacter saccharivorans",
            "Blautia sp. CAG:37",
            "Blautia sp. CAG:37_48_57",
            "Blautia obeum",
            "Clostridium sp. CAG:91",
            "Faecalibacterium prausnitzii",
            "Akkermansia muciniphila",
            "Ruthenibacterium lactatiformans",
            "Akkermansia sp. 54_46",
            "Akkermansia sp. UNK.MGS-1",
            "[Ruminococcus] torques",
            "Ruminococcus torques CAG:61",
            "Akkermansia muciniphila CAG:154",
            "Akkermansia sp. Phil8",
            "Hungatella hathewayi",
            "Eisenbergiella tayi",
            "Lachnospiraceae bacterium NLAE-zl-G231",
            "Tissierellia bacterium S7-1-4",
            "Coprobacillus sp. D6",
            "Porphyromonas bennonis",
            "Peptoniphilus grossensis",
            "Varibaculum cambriense"
        ]
    xz_species = sorted(xz_species)
    genome_ids = []
    for s in xz_species:
        for g_id in get_genome_ids_for_species(woltka_meta_df, s):
            genome_ids.append(g_id)
    return genome_ids


def configure_both():
    def set_factory_params(fact):
        df_processing = ChainedTransform(
            [
                RelativeAbundanceFilter(1/10000),
                # PairwisePearsonTransform(.95)
            ]
        )
        return fact.with_pair_strategy(["unpaired"]) \
            .with_normalization(Normalization.FRACTION) \
            .with_metadata_filter(MetadataFilter("Only Valid Disease States", "disease", ["MS", "Control"])) \
            .with_train_test(
            [
                Passthrough()
            ]) \
            .with_feature_transform(df_processing)

    old_fact = AnalysisFactory(
        BiomTable("none", biom_filepath=[
            "./dataset/biom/combined-none.biom"
        ]),
        "./dataset/metadata/iMSMS_1140samples_metadata.tsv",
        "old"
    )
    old_fact = set_factory_params(old_fact)

    new_fact = AnalysisFactory(
        BiomTable("none", biom_filepath=[
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-1of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-2of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-3of3.biom"
        ]),
        "./dataset/metadata/qiita_metadata_filtered.tsv",
        "new"
    )
    new_fact = set_factory_params(new_fact)

    both_fact = AnalysisFactory(
        BiomTable("none", biom_filepath=[
            "./dataset/biom/combined-none.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-1of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-2of3.biom",
            "./dataset/biom/qiita_bioms/imsms-none-Sep2-2022-3of3.biom"
        ]),
        combined_metadata_filepath,
        "combined_data"
    )
    # both_fact needs extra train_test splits
    both_fact = set_factory_params(both_fact).with_train_test(
        [
            SplitByMetadata(meta_col="prep", train_meta=["old"]),
            SplitByMetadata(meta_col="prep", train_meta=["new"]),
            PairedSplit()
        ]
    )

    # return old_fact
    return MultiFactory([old_fact, new_fact])
    # return MultiFactory([old_fact, new_fact, both_fact])
    # return new_fact


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")

    results = TableRunner().run(configure_both())
    woltka_meta_df = CSVTable("dataset/metadata/woltka_metadata.tsv", delimiter="\t").load_dataframe()

    for config, train, test in results:
        # xz_top_hits = get_xiaoyuan_top_hits(woltka_meta_df)
        # xz_top_hits = [r for r in xz_top_hits if r in train.df.columns]
        # Print what gets collapsed where
        # df, sets = pairwise_pearson(train.df, thresh=0.95)
        # for g_id in xz_top_hits:
        #     for rep in sets:
        #         if g_id in sets[rep]:
        #             if g_id != rep:
        #                 print(get_species(woltka_meta_df, g_id), "->", get_species(woltka_meta_df, rep))

        # Show correlation matrix
        # corr_mat = train.df[xz_top_hits].corr()
        # corr_mat.index = [get_species(woltka_meta_df, r) for r in xz_top_hits]
        # ax = sns.heatmap(corr_mat, xticklabels=True, yticklabels=True)
        # ax.tick_params(axis='both', which='major', labelsize=8)
        # plt.title("After Pearson Correlation")
        # plt.tight_layout()
        # plt.show()

        print(train.df["G001717135"])

        train.df["MS"] = train.df.index.map(lambda x: x[4])
        print(train.df["MS"])
        print(train.meta_df.columns)
        train.df["household"] = train.meta_df["household"]
        train.df = train.df[["G001717135", "MS", "household"]]

        plt.scatter(x=train.df["MS"], y=train.df["G001717135"])
        for household in train.df["household"]:
            hh_df = train.df[train.df["household"] == household]
            plt.plot(hh_df["MS"], hh_df["G001717135"], c="gray")
            # hh_df_1 = hh_df[hh_df["MS"] == "1"]
            # hh_df_2 = hh_df[hh_df["MS"] == "2"]
            # plt.plot([1, hh_df_1["G001717135"].iloc[0]], [2, hh_df_2["G001717135"].iloc[0]])

        plt.xticks(ticks=["1", "2"], labels=["MS", "Control"])
        plt.xlabel("Disease")
        plt.ylabel("Relative Abundance: " + "G001717135")
        plt.title("Sanity Check " + config.analysis_name)
        plt.show()







        # print(config.analysis_name, train.df.shape, train.meta_df.shape, test.df.shape)
        # train_meta = train.meta_df
        # data = pd.concat([train.df, train.meta_df], axis=1, sort=True)
        #
        # # ‘‘lme4’’ as lmer(y  disease + age + BMI + sex + (1|site) + (1|house)
        # # Fix inconsistencies in new metadata
        # if "collection_site" in data.columns:
        #     # Dammit, collection site metadata is missing.  Parse a site out of the sample ids.
        #     # data["site"] = data["collection_site"]
        #     data["site"] = data.index.map(lambda x: x[:3])
        # if "host_age" in data.columns:
        #     data["age"] = pd.to_numeric(data["host_age"])
        # if "host_body_mass_index" in data.columns:
        #     data["bmi"] = pd.to_numeric(data["host_body_mass_index"])
        # # Fix any necessary non numeric columns to be numeric
        # data["disease"] = data["disease"].map({"MS": 1, "Control": 0})
        # data["sex"] = data["sex"].map({"M": 1, "F": 0})
        # lme_results = []
        # for genome_id in train.df.columns:
        #     # print(data[[genome_id, "disease", "age", "bmi", "sex", "household", "site"]])
        #     md = smf.mixedlm(genome_id + " ~ disease + age + bmi + sex", data, groups=data["site"], re_formula="~age")
        #     mdf = md.fit(method=["lbfgs"])
        #     summary = mdf.summary()
        #     convergence = summary.tables[0].iloc[4,3]
        #     disease_coef = summary.tables[1].loc["disease", "Coef."]
        #     disease_pval = summary.tables[1].loc["disease", "P>|z|"]
        #     lme_results.append([genome_id, get_species(woltka_meta_df, genome_id), convergence, disease_coef, disease_pval])
        #
        # lme_results.sort(key=lambda x: x[4], reverse=True)
        # print("--------------------------------")
        # for res in lme_results:
        #     print(res[1], res[4])
        # print("--------------------------------")
        # print("Old Top Hits")
        # for g_id in get_xiaoyuan_top_hits(woltka_meta_df):
        #     for lme_r in lme_results:
        #         if lme_r[0] == g_id:
        #             print(lme_r)
