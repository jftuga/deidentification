"""A Python module for de-identifying personally identifiable information in text."""

from .deidentification import Deidentification, DeidentificationConfig, DeidentificationOutputStyle
from .deidentification_constants import pgmName, pgmVersion, pgmUrl

__version__ = pgmVersion
__author__ = "John Taylor"
__all__ = [
    "Deidentification",
    "DeidentificationConfig",
    "DeidentificationOutputStyle",
    "pgmName",
    "pgmVersion",
    "pgmUrl",
]