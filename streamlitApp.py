import streamlit as st
import random
from itertools import permutations
from collections import Counter


# Load the dictionary file
@st.cache_data
def load_scrabble_words(filename):
    with open(filename, "r") as file:
        return set(word.strip().lower() for word in file)


# Game logic (remains largely the same)
class AWordGame:
    def __init__(self, dictionary):
        self.level = 0
        self.max_level = 10
        self.points = 0
        self.max_word_size = 5
        self.min_word_size = 3
        self.max_num_words = 30
        self.min_num_words = 8
        self.dictionary = load_scrabble_words("sowpodsDict.txt")
        self.all_level_letters = []
        self.all_possible_words = []
        self.found_words = set()
        self.current_word = []
        self.letters = []
        self.level_completed = False
        self.start_up()
        self.start_new_game()

    def reset(self):
        self.__init__(dictionary)

    def define_level(self):
        if self.level == 1:
            self.max_word_size = 5
            self.min_word_size = 3
            self.max_num_words = 30
            self.min_num_words = 8
        if self.level == 2:
            self.min_num_words = 15
        if self.level == 3:
            self.max_word_size = 6
            self.max_num_words = 35
        if self.level == 4:
            self.min_word_size = 4
            self.max_num_words = 40
        if self.level == 5:
            self.max_word_size = 7
            self.min_num_words = 20
        if self.level == 7:
            self.min_num_words = 25
        if self.level == 8:
            self.min_word_size = 5

    def start_up(self):
        for levels in range(1, 11):
            self.level = levels
            self.define_level()
            while True:
                filtered_words = [
                    word for word in self.dictionary if len(word) == self.max_word_size
                ]
                selected_word = random.choice(filtered_words)
                self.letters = list(selected_word)
                random.shuffle(self.letters)
                self.find_possible_words()
                big_words = [
                    word
                    for word in self.all_possible_words
                    if self.min_word_size <= len(word) <= 7
                ]
                if (
                    self.min_num_words
                    <= len(self.all_possible_words)
                    <= self.max_num_words
                    and len(big_words) >= 1
                ):
                    self.all_level_letters.append(self.letters)
                    break
        self.level = 0

    def start_new_game(self):
        self.found_words.clear()
        self.current_word.clear()
        self.level += 1
        if self.level > 10:
            st.write("You've completed the game! There are only 10 levels.")
            return
        self.level_completed = False
        self.define_level()
        self.letters = self.all_level_letters[self.level - 1]
        self.find_possible_words()

    def find_possible_words(self):
        possible_words = set()
        for length in range(self.min_word_size, self.max_word_size + 1):
            for perm in permutations(self.letters, length):
                word = "".join(perm)
                if word.lower() in self.dictionary:
                    possible_words.add(word)
        self.all_possible_words = [
            word
            for word in possible_words
            if self.min_word_size <= len(word) <= self.max_word_size
            and set(word).issubset(self.letters)
            and self.can_form_word(word)
        ]

    def can_form_word(self, word):
        letters_copy = self.letters.copy()
        for letter in word:
            if letter in letters_copy:
                letters_copy.remove(letter)
            else:
                return False
        return True

    def calculate_word_points(self, word):
        points_by_length = [20, 20, 20, 30, 50, 80, 120]
        return sum(points_by_length[i] for i in range(len(word)))

    def submit_word(self, word=None):
        if word == None:
            word = st.session_state.input_word
        word = word.lower()
        if word in self.all_possible_words and word not in self.found_words:
            self.found_words.add(word)
            word_points = self.calculate_word_points(word)
            self.points += word_points
            if len(word) == self.max_word_size:
                self.level_completed = True
            result = f"Correct! You've earned {word_points} points!"
        elif word in self.all_possible_words:
            result = f"'{word.upper()}' has already been found."
        else:
            if (len(word) > self.max_word_size) or (len(word) < self.min_word_size):
                # st.write("Found Words:", self.found_words)
                result = f"'{word.upper()}' is not of a valid size."
            else:
                self.points -= 2
                print(self.all_possible_words)
                result = f"'{word.upper()}' is not a valid word."
        st.session_state.input_word = ""
        st.write(result)


def display_blanks(all_possible_words):
    # Sort the possible words by length first, then alphabetically
    sorted_words = sorted(all_possible_words, key=lambda w: (len(w), w))

    # Set the number of columns
    columns = 3
    rows = len(sorted_words) // columns + (len(sorted_words) % columns > 0)

    # Create a grid for displaying blanks
    grid = [["" for _ in range(columns)] for _ in range(rows)]
    for idx, word in enumerate(sorted_words):
        row, col = divmod(idx, rows)
        grid[col][row] = " ".join("_" for _ in word)

    # Render the grid in Streamlit
    for row in grid:
        row_text = "    ".join(row)
        st.text(row_text)


def update_word_display(all_possible_words, found_words):
    # Sort the possible words by length first, then alphabetically
    sorted_words = sorted(all_possible_words, key=lambda w: (len(w), w))
    longest_words = get_longest_words(all_possible_words)
    # Set the number of columns
    columns = 3
    rows = len(sorted_words) // columns + (len(sorted_words) % columns > 0)

    # Create a grid for displaying the words
    grid = [["\t" for _ in range(columns)] for _ in range(rows)]
    for idx, word in enumerate(sorted_words):
        row, col = divmod(idx, rows)
        ender = ""
        if word in longest_words:
            ender = "\u2605"
        if word in found_words:
            grid[col][row] = " ".join(word.upper()) + ender  # Show the actual word
        else:
            grid[col][row] = " ".join("_" for _ in word) + ender  # Show blanks

    # Render the grid in Streamlit
    for row in grid:
        cols = st.columns(columns)
        for col_idx, word in enumerate(row):
            if word:  # Ensure we only render non-empty slots
                cols[col_idx].text(word)


def get_longest_words(all_possible_words):
    # Sort words by length in descending order to get the longest ones
    max_length = max(len(word) for word in all_possible_words)

    # Get all words that have the maximum length
    longest_words = [word for word in all_possible_words if len(word) == max_length]
    return longest_words


def select_letter(letter):
    print(letter)


def display_letters(self):
    # Create columns based on the number of available letters
    num_columns = len(
        self.letters
    )  # You can adjust this based on your layout preference
    num_letters = len(self.letters)
    columns = st.columns(num_columns)

    # Create a box or button for each letter
    for i, letter in enumerate(self.letters):
        col = columns[i]  # Distribute letters across the columns
        with col:
            # Display each letter as a button inside a box
            if st.button(letter.upper(), key=f"letter_{i}_{letter.upper()}"):
                # Add logic when the letter button is clicked, like adding it to a word
                select_letter(letter.upper())


# Load the dictionary
dictionary = load_scrabble_words("sowpodsDict.txt")


# Initialize game state in session state
if "game" not in st.session_state:
    st.session_state.game = AWordGame(dictionary)


# if "all_possible_words" not in st.session_state:
#     # Example data for demonstration
#     st.session_state.all_possible_words = AWordGame.find_possible_words(dictionary)
# Show letters and score
game = st.session_state.game

# Streamlit UI
st.title("A Word Game")
st.sidebar.title("Game Controls")

if st.sidebar.button("Start Next Level"):
    longest_words = get_longest_words(game.all_possible_words)
    found_longest_word = any(word in game.found_words for word in longest_words)
    if found_longest_word:
        game.start_new_game()
    else:
        st.write(
            "Cannot start next level until one of the longest words has been found"
        )


# if st.sidebar.button("Start New Game"):
#     game.start_new_game()


if st.sidebar.button("Reset Game"):
    game.reset()

st.write(f"Level: {game.level}")
st.write(f"Points: {game.points}")
display_letters(game)
# st.write(f"Letters: {', '.join(game.letters.upper())}")


def secSubmitWord():
    game.submit_word(st.session_state.input_word)


word = st.text_input("Enter a word:", on_change=game.submit_word, key="input_word")
# if st.button("Submit Word"):
#    result = game.submit_word(word)
#    st.write(result)

update_word_display(game.all_possible_words, game.found_words)

# if st.sidebar.checkbox("Show Possible Words"):
#     st.write(game.all_possible_words)
