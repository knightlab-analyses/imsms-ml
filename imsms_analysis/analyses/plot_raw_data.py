from imsms_analysis.analysis_runner import SerialRunner
from imsms_analysis.common.analysis_factory import AnalysisFactory, MultiFactory
from imsms_analysis.common.normalization import Normalization
from imsms_analysis.common.table_info import BiomTable
from imsms_analysis.events.plot_raw import RawScatterPlot

def configure():
    metadata_filepath = "./dataset/metadata/iMSMS_1140samples_metadata.tsv"
    woltka_transforms = AnalysisFactory(
        [BiomTable("none")],
        metadata_filepath
    ).with_pair_strategy("unpaired")\
     .with_normalization(Normalization.NONE)

    return MultiFactory([woltka_transforms])


if __name__ == "__main__":
    # Pretend all scripts are run from root of repo for file paths.
    import os
    os.chdir("..")
    runner = SerialRunner()

    Bacteroides_coprophilus = 'G000157915'
    Prevotella_stercorea = 'G000235885'

    Bacteroides_vulgatus = 'G000012825'
    Alistipes_finegoldii = 'G000265365'
    Anaerostipes_hadrus = 'G000332875'

    Faecalibacterium_prausnitzii = 'G000162015'
    Fusicatenibacter_sacchirivorans = 'G001406335'

    Bacteroidales_bacterium_K10 = "G001689655"
    Synergistes_sp_Zagget9 = "G001941205"

    ecoli = [
        "G000008865",
        "G000026325",
        "G000026345",
        "G000183345",
        "G000299455",
        "G001283625",
    ]
    Klebsiella_pneumoniae = "G000240185"
    Yersinia = [
        "G001122605",
        "G000009345",
        "G000253175",
        "G000009065",
        "G000168835"
    ]
    Yersinia_pestis = [
        "G000009065",
        "G000168835"
    ]

    akk = [
        # ("G001683795", "Akkermansia glycaniphila (WoL:G001683795)"),
        # ("G900097105", "Akkermansia glycaniphila (WoL:G900097105)"),
        ("G000020225", "Akkermansia muciniphila (NCBI:txid349741)"),
        ("G000723745", "Akkermansia muciniphila (NCBI:txid239935)"),
        ("G000436395", "Akkermansia muciniphila CAG:154"),
        ("G001917295", "Akkermansia sp. 54_46"),
        ("G000437075", "Akkermansia sp. CAG:344"),
        # ("G001647615", "Akkermansia sp. KLE1605"),
        # ("G001578645", "Akkermansia sp. KLE1797"),
        # ("G001580195", "Akkermansia sp. KLE1798"),
        ("G001940945", "Akkermansia sp. Phil8"),
        ("G000980515", "Akkermansia sp. UNK.MGS-1"),
    ]

    plots = []

    plots.append((Yersinia_pestis[0], Yersinia_pestis[1], "Yersinia pestis", "Yersinia pestis\n" + Yersinia_pestis[0], "Yersinia pestis\n" + Yersinia_pestis[1]))

    plots.append((ecoli[0], Yersinia_pestis[1], "E. coli and Yersinia pestis", "Escherichia coli", "Yersinia pestis"))
    plots.append((ecoli[1], Yersinia_pestis[1], "E. coli and Yersinia pestis", "Escherichia coli", "Yersinia pestis"))
    plots.append((ecoli[2], Yersinia_pestis[1], "E. coli and Yersinia pestis", "Escherichia coli", "Yersinia pestis"))
    plots.append((ecoli[3], Yersinia_pestis[1], "E. coli and Yersinia pestis", "Escherichia coli", "Yersinia pestis"))
    plots.append((ecoli[4], Yersinia_pestis[1], "E. coli and Yersinia pestis", "Escherichia coli", "Yersinia pestis"))
    plots.append((ecoli[5], Yersinia_pestis[1], "E. coli and Yersinia pestis", "Escherichia coli", "Yersinia pestis"))
    plots.append((Klebsiella_pneumoniae, Yersinia_pestis[1], "Klebsiella pneumoniae and Yersinia pestis", "Klebsiella pneumoniae", "Yersinia pestis"))
    # plots.append(("G000431035", "G001940855", "Overlapping References", "Clostridium sp. CAG:226", "Christensenellaceae bacterium Phil1"))
    # plots.append(("G000432875", "G000436155", "Overlapping References", "Firmicutes bacterium CAG:466", "Clostridium sp. CAG:505"))
    # plots.append((Bacteroides_coprophilus, Prevotella_stercorea, "Overlapping References", "Bacteroides coprophilus", "Prevotella stercorea"))
    # plots.append((Bacteroides_vulgatus, Faecalibacterium_prausnitzii, "Unrelated References", "Bacteroides vulgatus", "Faecalibacterium prausnitzii"))
    # plots.append((Bacteroidales_bacterium_K10, Synergistes_sp_Zagget9, "Effectively Identical References", "Bacteroidales bacterium K10", "Synergistes_sp_Zagget9"))

    # for i in range(len(akk)):
    #     for j in range(i+1, len(akk)):
    #         plots.append((akk[i][0], akk[j][0], "", akk[i][1], akk[j][1]))

    evt = RawScatterPlot(plots)
    evt.hook_events(runner)
    runner.run(configure())

