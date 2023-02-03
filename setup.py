#!/usr/bin/env python3
"""
This module contains the setup script for installing the package.
"""
import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install

DESCRIPTION = """
Mimasa is a real-time multilingual face translator application that takes a video input,
detects the facial patterns and speech of the person, translates the speech to another language
and changes the facial expression of the person to match the output language. The final output
is a video with the translated speech and modified facial expression.
"""


class LintCommand(install):
    """Custom command to run linting on package installation."""

    def run(self):
        """Run linter."""
        subprocess.call(["pylint", "your_module"])
        install.run(self)


with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

os.environ["PYTHONPATH"] = os.path.join(os.getcwd(), "src")
author_list = ["Yellenki Ritheesh Baradwaj"]

setup(
    name="Mimasa",
    version="1.0.0",
    author=", ".join(author_list),
    author_email="ritheeshbaradwaj@gmail.com",
    description="A Real-time Multilingual Face Translator",
    long_description=DESCRIPTION,
    url="https://github.com/developers-cosmos/Mimasa",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    scripts=["src/main.py"],
    include_package_data=True,
    package_data={
        "": ["*.txt"],
    },
    entry_points={
        "console_scripts": [
            "myproject = src.main:main",
        ],
    },
    env={"PYTHONPATH": os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))},
    # NOTE: Disbale the following lines to avoid lint checking
    cmdclass={
        "install": LintCommand,
    },
)
