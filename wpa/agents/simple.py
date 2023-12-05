"""Simple Agent Module

This module implements a very simple agent that has no learning. It simply
chooses words based on a scoring of each letters' position relative to the
median for each position's range.
"""

from operator import itemgetter, neg

from .base import BaseAgent


class SimpleAgent(BaseAgent):
    """The ``SimpleAgent`` is a learning-free agent that plays based on a
    heuristic of selecting guesses that are closest to the median letters in
    the ranges currently known, based on previous guesses."""

    def __init__(self, game, words=None, *, name=None, reward=5.0):
        """Constructor for SimpleAgent. Just passes through to the superclass.

        Positional parameters:

            `game`: An instance of the wordle.game.Game class
            `words`: The allowed (guessable) words, a list or a file name. If
            not given, the superclass constructor takes the list of words
            from the `game` parameter.

        Keyword parameters:

            `name`: An identifying string to use in stringification of this
            instance, to discern it from other instances
            `reward`: A value added to the score and the training when the
            word is correctly guessed
        """

        super().__init__(game, words, name=name, reward=reward)

    def score(self, word):
        """Score an individual word for the sake of selecting it as a guess. A
        score closer to 0.0 is better, with all scores being negative. A score
        is the sum of the distance of a letter from that position's mean, over
        all five letter."""

        score = 0.0
        for i, c in enumerate(word):
            score += abs(self.means[i] - ord(c)) / self.lengths[i]

        return -score

    def select_guess(self, guesses):
        """Return a selected word from the list of possible `guesses`."""

        weighted = [(x, self.score(x)) for x in guesses]
        weighted.sort(key=itemgetter(1), reverse=True)

        return weighted[0][0]

    def play_once(self):
        """Play a single word, creating and returning some data from the
        process (including the result)."""

        # Start by making a local copy of the words list.
        words = self.words.copy()
        result = {"guesses": [], "responses": [], "word": None,
                  "result": 0, "score": 0.0}
        
        # Prep internal state
        self.start_game()
        
        for _ in range(6):
            # For each of the 6 potential guesses, a word is selected from the
            # current list of words. Each word is scored based on how close to
            # the middle each letter is, for its corresponding position/range.
            # Each round, this call should be considerably faster.
            guess = self.select_guess(words)

            # Have the game score our guess against the current word.
            raw_score = self.game.score_guess(guess)
            result["responses"].append(raw_score)
            score = list(map(neg, map(abs, raw_score)))
            result["guesses"].append((guess, sum(score)))
            result["score"] += sum(score)

            # Have we found the word? A sum of 0 will mean that we have.
            if sum(score) == 0:
                result["result"] = 1
                result["word"] = guess
                # Apply the reward that was configured on the object:
                result["score"] += self.reward
                break
            else:
                # If we haven't found the word, trim the list down based on
                # our guess and its score. Use `raw_score` here, since it
                # encapsulates the high/low information for each letter.
                words = self.apply_guess(words, guess, raw_score)

        if not result["word"]:
            # If we didn't find it within the given number of tries, mark it as
            # a "loss".
            result["word"] = self.game.word

        return result
