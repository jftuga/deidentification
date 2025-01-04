from setuptools import setup, find_packages
import os
import sys

# Add the package directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'deidentification')))

from deidentification_constants import pgmVersion

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="text-deidentification",
    version=pgmVersion,
    author="John Taylor",
    author_email="",
    description="A Python module for de-identifying personally identifiable information in text",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jftuga/deidentification",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Legal Industry",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing",
        "Topic :: Security",
    ],
    python_requires=">=3.10",
    install_requires=[
        "spacy>=3.8.3,<4.0.0",
        "torch>=2.5.1,<3.0.0",
        "chardet>=5.2.0",
        "veryprettytable>=0.8.1",
    ],
    entry_points={
        "console_scripts": [
            "deidentify=deidentification.deidentify:main",
        ],
    },
)
