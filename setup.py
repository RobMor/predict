"""PREDICT DEMO

This is meant to be a rough outline of how predict will function
"""

from setuptools import setup

setup(
    name="predict",
    packages=["predict"],
    install_requires=["bs4", "flask", "requests", "flask-login", "flask-sqlalchemy"],
    entry_points={
        "console_scripts": ["predict=predict.cli:main"]
    },
    package_data={
        "predict": ["templates/*", "static/*"]
    }
)
