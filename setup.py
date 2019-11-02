"""PREDICT DEMO

This is meant to be a rough outline of how predict will function
"""

from setuptools import setup

setup(
    name="predict",
    packages=["predict", "predict.builtin"],
    install_requires=["bs4", "flask", "requests", "flask-login", "sqlalchemy"],
    entry_points={
        "console_scripts": ["predict=predict.cli:main"],
        "predict.plugins": [
            "csv=predict.builtin.csv:CSV",
            "majority=predict.builtin.majority:Majority",
            "current_user=predict.builtin.current_user:CurrentUser",
            "comments=predict.builtin.comments:Comments",
            "num_agree=predict.builtin.num_agree:NumAgree",
        ]
    },
    package_data={
        "predict": ["templates/*", "static/*"]
    }
)
