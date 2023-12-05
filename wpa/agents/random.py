"""Random Agent Module

This module implements a very simple agent that has no learning. It simply
chooses words based on letter frequency from a list that is shortened by
filtering each iteration. It then randomly selects a guess from the pool of
candidates.
"""

from random import Random

from .simple import SimpleAgent


class RandomAgent(SimpleAgent):
    """The RandomAgent is a learning-free agent that plays based on a
    heuristic of always applying the result from the latest guess to reduce the
    pool of viable guesses. Unlike ``SimpleAgent``, it then selects a new guess
    completely randomly from the pool of new candidate words."""

    def __init__(self, game, words=None, *, name=None, seed=None, reward=5.0):
        """Constructor for RandomAgent. Handles the specific parameter ``seed``
        which is not recognized by ``SimpleAgent``.

        Positional parameters:

            `game`: An instance of the wordle.game.Game class
            `words`: The allowed (guessable) words, a list or a file name. If
            not given, the superclass constructor takes the list of words
            from the ``game`` parameter.

        Keyword parameters:

            `seed`: A specific seed value to use for the localized random
            number generator
            `name`: An identifying string to use in stringification of this
            instance, to discern it from other instances
            `reward`: A value added to the score and the training when the
            word is correctly guessed
        """

        super().__init__(game, words, name=name, reward=reward)
        self.rng = Random(seed)

    def select_guess(self, guesses):
        """Return a selected word from the list of possible guesses. For this
        agent, this is a completely random selection."""
        return self.rng.choice(guesses)

    def reset(self):
        super().reset()
        self.rng.seed()
