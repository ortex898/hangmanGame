# Hangman-Python
A simple hangman game made with python and pygame.

# Requirements
- Python 3.x
- pygame


# Algorithms

• Candidate Word Filtering Algorithm: At each guess, the AI applies a pattern-
matching approach:

• If the revealed pattern is something like _ A _ E, then:
- Only words of the same length are considered.
- These words must have 'A' in the second position and 'E' in the fourth
position.
- Any known-wrong letters must not appear in these candidate words.
    This step is critical for narrowing down the solution space from potentially
    thousands of words to a much smaller subset.
- Frequency Analysis Algorithm: Once a candidate list is generated, the AI:
- Iterates through all candidate words.
- Counts the occurrences of each letter not yet guessed.
- Selects the letter with the highest frequency count to maximize the
likelihood of a correct guess.
- Minimax (Fallback): The code includes a minimax function to evaluate the
future potential of guesses. Although minimized in the final approach, minimax
was originally considered to project outcomes of multiple guesses ahead. However,
because the improved frequency-based filtering generally yields good results,
minimax acts more as a fallback strategy now.
- Simple Probability-Based Improvement: By maintaining letter statistics, the
code attempts to pick letters that historically have a higher probability of being
correct. This isn't a complex probability model—just a running record of correct
vs. total guesses—but it can help the AI avoid persistently poor-performing letters
over time.
