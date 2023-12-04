"""Words Module

Any code/functions common to multiple classes, that deal with the words.
"""

from collections import Counter
import json
from typing import List


def read_words(file: str):
    """Read a specified words file into a list of words. The file is in JSON
    format. Return the list."""
    with open(file, "r") as f:
        words = json.load(f)

    return words


def letter_freq(words: List[str]):
    """Compute the frequency of letters across the given list of words.
    Returns a ``Counter`` instance containing the counts."""
    c = Counter()

    for w in words:
        c += Counter(w)

    return c
