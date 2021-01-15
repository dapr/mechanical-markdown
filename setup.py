
"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

from setuptools import setup, find_packages
from mechanical_markdown import __version__ as version

# The text of the README file
README = ""

try:
    with open("README.md", "r") as fh:
        README = fh.read()
except FileNotFoundError:
    pass

# This call to setup() does all the work
setup(
    name="mechanical-markdown",
    version=version,
    description="Run markdown recipes as shell scripts",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/dapr/mechanical-markdown",
    author="Charlie Stanley",
    author_email="Charlie.Stanley@microsoft.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7"
    ],
    packages=find_packages(exclude='tests'),
    include_package_data=True,
    install_requires=["termcolor", "pyyaml", "mistune"],
    entry_points={
        "console_scripts": [
            "mm.py = mechanical_markdown.__main__:main"
        ]
    },
)
