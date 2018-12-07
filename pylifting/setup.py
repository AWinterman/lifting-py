import os
from setuptools import setup, find_packages


setup(
    name = "lift",
    version = "1.0",
    author = "Andrew Winterman",
    description = ("Lifting stats and stuff"),
    long_description='lifting log tracking via a postgres/cli/',
    author_email = "anywinterman@gmail.com",
    license = "BSD",
    keywords = "lifting cli records",
    url = "http://packages.python.org/an_example_pypi_project",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],

    entry_points={'console_scripts': ['lift=pylifting.cli:cli']},
    packages=['lift'],
    package_dir={'lift': 'src/lift'},
)
