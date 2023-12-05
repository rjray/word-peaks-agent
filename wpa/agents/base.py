"""Base Class for all Agent Classes

This provides BaseAgent, the base class for other Agent implementations.
"""

from random import shuffle
import re
from statistics import mean

from ..shared.words import read_words


ALL_LETTERS = list(range(ord('a'), ord('z') + 1))


class BaseAgent():
    """The BaseAgent class is a common base-class for the different agents that
    will be developed. It only provides very basic operations."""

    def __init__(self, game, words=None, *, name, reward=5.0):
        """Base constructor, to handle basic parts like handling the word list
        and the game instance.

        Positional parameters:

            `game`: An instance of the wordle.game.Game class
            `words`: The allowed (guessable) words, a list or a file name. If
            not given, takes the list of words from the `game` parameter.

        Keyword parameters:

            `name`: An identifying string that will be incorporated into the
            string representation of the object
            `reward`: A value added to the score and the training when the
            word is correctly guessed
        """

        self.game = game
        self.name = name
        self.reward = reward
        self.ranges = [None, None, None, None, None]
        self.means = [0, 0, 0, 0, 0]
        self.lengths = [0, 0, 0, 0, 0]

        if words:
            if isinstance(words, str):
                self.words = read_words(words)
            else:
                self.words = words.copy()
        else:
            self.words = game.words.copy()

        shuffle(self.words)

    def __str__(self):
        """Provide a stringification of the object. If a `name` parameter
        was given at creation, include that."""

        if self.name:
            return f"{self.__class__.__name__}({self.name})"
        else:
            return self.__class__.__name__

    def reset(self):
        """Perform a reset of the agent. In the case of the base class, this
        calls the ``reset`` method on the game object."""

        shuffle(self.words)
        self.game.reset()

    def start_game(self):
        """Prepare the agent to start one game (a single word). Set/reset all
        internal state that the agent needs."""

        # Set up the internal state.
        for i in range(5):
            self.ranges[i] = ALL_LETTERS.copy()
            self.means[i] = mean(ALL_LETTERS)
            self.lengths[i] = 26

    def create_re_pattern(self):
        """Create a regular expression pattern using the ranges stored in the
        object state."""

        pieces = []
        for i in range(5):
            if self.lengths[i] == 1:
                pieces.append(chr(self.ranges[i][0]))
            else:
                a = chr(self.ranges[i][0])
                b = chr(self.ranges[i][-1])
                pieces.append(f"[{a}-{b}]")

        return re.compile(f"^{''.join(pieces)}$")

    def apply_guess(self, words_in, guess, score):
        """Filter a new list of viable words based on the rules of this agent.
        For this implementation, the list is winnowed down by applying simple
        logic around the letter scores from the guess.

        Parameters:

            `words_in`: A list of the current candidate words
            `guess`: The most-recent guess made by the agent
            `score`: The list of per-letter scores for the guess
        """

        words = words_in.copy()

        # Start by using the scores, along with the letters of `guess`, to
        # adjust the 5 values of `ranges`.
        for i, c in enumerate(guess):
            cv = ord(c)
            if score[i] > 0:
                # The guessed letter is "greater than" the correct one. The
                # range should be moved to be current-start..(c-1)
                self.ranges[i] = list(range(self.ranges[i][0], cv))
            elif score[i] < 0:
                # The guessed letter is "less than" the correct one. The range
                # should be moved to be (c+1)..current-end.
                self.ranges[i] = list(range(cv + 1, self.ranges[i][-1] + 1))
            else:
                # The score for the slot is zero, so this is the correct letter
                # for this slot.
                self.ranges[i] = [cv]

            self.lengths[i] = len(self.ranges[i])
            self.means[i] = mean(self.ranges[i])

        # Build a regular expression based on the ranges.
        pattern = self.create_re_pattern()

        # Filter the list of words based on the regexp.
        words = list(filter(lambda x: re.search(pattern, x), words))

        # In some cases, the actual guess-word can survive to this point. Make
        # sure it isn't in the new list.
        try:
            words.remove(guess)
        except:
            pass

        return words

    def play_once(self):
        """Placeholder to throw an exception if an implementation class fails
        to define this method."""

        raise NotImplementedError(
            f"Class {self.__class__.__name__} has not defined play_once()"
        )

    def play(self, n=0):
        """Play the full game. Will run all the words provided as answers in
        the game object (based on how it was instantiated), unless the ``n``
        parameter is passed and is non-zero. If ``n`` is passed, only the first
        ``n`` words will be played.

        Returns a data structure of all the words played and some metrics over
        the full set."""

        history = []
        count = 0

        while self.game.start():
            count += 1
            if n and n < count:
                break

            history.append(self.play_once())

        result_total = 0
        guess_total = 0
        score_total = 0.0
        for outcome in history:
            result_total += outcome["result"]
            guess_total += len(outcome["guesses"])
            score_total += outcome["score"]

        count = len(history)
        result = result_total / count
        guess_avg = guess_total / count
        score_avg = score_total / count

        return {
            "name": f"{self}",
            "history": history,
            "count": len(history),
            "guess_avg": guess_avg,
            "score_avg": score_avg,
            "result": result
        }
