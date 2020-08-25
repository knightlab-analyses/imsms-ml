from setuptools import setup

setup(
    name="imsms_analysis",
    entry_points={
        'q2_mlab.models': [
            'RandomForestPCA=imsms_analysis.custom_models:RandomForestPCA'
        ]
    },
    install_requires=["umap-learn"]
)