from setuptools import setup

setup(
    name="imsms_analysis",
    entry_points={
        'q2_mlab.models': [
            'RandomForestSVD=imsms_analysis.custom_models:RandomForestSVD'
        ]
    },
    install_requires=["umap-learn"]
)