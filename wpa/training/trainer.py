"""Trainer Module

This module contains the functions used to generate data for use in training
learning agents.
"""

from collections import Counter
import json
import os.path


def load_json(file):
    """A simple helper-function to load JSON data from the parameter ``file``
    and return the data/structure that was read."""
    with open(file, "r") as f:
        data = json.load(f)

    return data


def save_json(file, data):
    """A simple helper-function to save ``data`` as JSON to the parameter
    ``file``."""
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

    return


class Trainer():
    def __init__(self, game, base="."):
        """Class constructor. Takes two positional arguments:

            game: An instance of wordle.game.Game that is used for the word
                  lists.
            base: A string specifying the path into which the various files
                  are written to and read from."""
        self.game = game
        self.base = base

    def local_file(self, file):
        return file if os.path.isabs(file) else os.path.join(self.base, file)

    def create_letter_pos(self, file=None):
        answers = self.game.answers
        ans_count = len(answers)
        base = ord("a")
        counters = [Counter() for _ in range(5)]

        for word in answers:
            for i, c in enumerate(word):
                counters[i][c] += 1

        probabilities = [[0] * 5 for _ in range(26)]
        for i, counter in enumerate(counters):
            for ch, count in counter.items():
                probabilities[ord(ch) - base][i] = count / ans_count

        if file:
            fname = self.local_file(file)
            save_json(fname, probabilities)

        return probabilities

    def load_letter_pos(self, file):
        return load_json(self.local_file(file))

    def create_tclp_table(self, correct_probabilities, file=None):
        tclp = {}
        base = ord("a")

        for word in self.game.words:
            total = 0.0
            for i, ch in enumerate(word):
                total += correct_probabilities[ord(ch) - base][i]

            tclp[word] = total

        if file:
            fname = self.local_file(file)
            save_json(fname, tclp)

        return tclp

    def load_tclp_table(self, file):
        return load_json(self.local_file(file))

    def create_all_files(self):
        letter_pos = self.create_letter_pos("letter_pos.json")
        self.create_tclp_table(letter_pos, "tclp_table.json")

        return

    def load_all_files(self):
        files = {}

        files["letter_pos"] = self.load_letter_pos("letter_pos.json")
        files["tglp_table"] = self.load_tclp_table("tglp_table.json")

        return files


def main():
    import sys
    from wpa.game import Game

    game = Game(
        answers="data/targets-filtered.json",
        words="data/dictionary-filtered.json"
    )
    base = sys.argv[1] if len(sys.argv) > 1 else "data/training/common"

    trainer = Trainer(game, base)
    trainer.create_all_files()

    return


if __name__ == '__main__':
    main()
