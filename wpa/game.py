"""Game Module

This module provides the basic game interface, stripped of most user-oriented
features. The idea is that the game-umpire is an instantiable class that will
play as many games as there are answer words.
"""

from random import Random

from .shared.words import read_words


class Game():
    """The Game class encapsulates the "umpire" of the game: an entity that
    governs the playing of the game and rules on each inputted word with
    regards to the game's current word. One instance of the Game class will
    play all 2005 game-words in sequence (or randomly), signalling when the
    list of game-words has been exhausted."""

    def __init__(self, *, answers, words, randomize=False, seed=None):
        """Constructor. Build the basic Game object and set it up for immediate
        use. Stores the word-lists and initializes internal values.

        Keyword parameters:

            answers: A filename of answer-words or a list of words
            words: A filename of acceptable guess-words or a list of words
            randomize: A Boolean flag (default False) that tells whether to
                       shuffle the list of answer-words before starting a new
                       game sequence
            seed: An integer value (default None) that is used as the seed for
                  the internal random.Random instance used to shuffle the words
        """

        # Keep a separate RNG, so that it doesn't perturb any randomness in
        # agent classes.
        self.randomize = randomize
        if self.randomize:
            self.rng = Random(seed)

        if isinstance(words, str):
            self.words = read_words(words)
        else:
            self.words = words.copy()

        if isinstance(answers, str):
            self.answers = read_words(answers)
        else:
            self.answers = answers.copy()

        if self.randomize:
            self.rng.shuffle(self.answers)

        self.index = 0
        self.word = None

    def start(self):
        """Start a game on the next word in the list of answer-words. Returns a
        False value if there are no more words in the list."""

        if self.index == len(self.answers):
            return False

        self.word = self.answers[self.index]
        self.index += 1

        return True

    def score_guess(self, guess):
        """Score the agent's guess, per Word Peak rules. Returns a 5-element
        list of values in the range [-0.5, 0.0, 0.5], where:

            -0.5: The guess letter is "below" the word letter
            0.0: The guess letter is correct
            0.5: The guess letter is "above" the word letter

        This differs from the scoring in Wordle, in which a completely-missing
        letter was a higher penalty that right-letter-wrong-place. This type of
        scoring is necessary for the play of the game.

        Throws an error if not in an active game or if the guess is not in
        the list of allowed words."""

        if not self.word:
            raise Exception("score_guess(): called with no active word")
        if len(guess) != 5:
            raise Exception(f"score_guess(): {guess} is not 5 letters")
        if guess not in self.words:
            raise Exception(f"score_guess(): {guess} is not an allowed guess")

        rtn = [0.0] * 5

        for i, c in enumerate(self.word):
            if c < guess[i]:
                rtn[i] = -0.5
            elif c > guess[i]:
                rtn[i] = 0.5

        # If this guess is correct, move the object to a not-playing state:
        if sum(map(abs, rtn)) == 0:
            self.word = None

        # Return the score.
        return rtn

    def reset(self):
        """Reset the game object so that it can be used for another run. If the
        ``randomize`` attribute was set to True at creation, the list of words
        will be re-shuffled."""
        self.index = 0
        self.word = None
        if self.randomize:
            self.rng.shuffle(self.answers)
