# Copyright (c) 2025 Cecilia Zagni
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Cecilia Zagni
# Date: 2025-02-20
# Description: DECOS Webapp - Utility Module
# This module provides utility functions for loading and processing choice fields used throughout the Digital ECOSystem (DECOS) of PRP@CERIC.
# It dynamically loads predefined choice lists from a JSON file (choices.json) into a global dictionary and offers a helper function to convert
# these lists into Django-compatible choice tuples. This standardizes the management of choice fields across different DECOS models,
# ensuring consistency and reducing redundancy. The choices are primarily presented in the forms of the Home App.

from pathlib import Path
import json

# Loads predefined choice lists from 'choices.json' into a dictionary at runtime.
def initChoices():
    path = Path(__file__).parent / "choices.json"
    with path.open() as f:
        d = json.load(f)
        return d

# Global dictionary holding all choices for models.
choices = initChoices()

# Converts a list of [key, label] pairs into Django-compatible (key, label) tuples.
def tupleConvert(shortList):
    outlist = []
    for item in shortList:
        outlist.append((item[0], item[1]))
    return outlist
