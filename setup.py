from setuptools import setup, find_packages
import os
import sys

# Add the package directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'deidentification')))

from deidentification_constants import pgmVersion

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="deidentification",
    version=pgmVersion,
    author="John Taylor",
    author_email="",
    description="A Python module for de-identifying personally identifiable information in text",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jftuga/deidentification",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing",
        "Topic :: Security",
    ],
    python_requires=">=3.7",
    install_requires=[
        "spacy>=3.0.0",
        "torch",
    ],
    entry_points={
        "console_scripts": [
            "deidentify=deidentification.deidentify:main",
        ],
    },
)
