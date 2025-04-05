from setuptools import setup, find_packages

setup(
    name="bfc-reports",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "reportlab",
        "numpy",
        "matplotlib",
        "pandas"
    ],
)