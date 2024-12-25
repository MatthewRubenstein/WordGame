import streamlit as st
import random
from itertools import permutations
from collections import Counter


# Load the dictionary file
@st.cache
def load_scrabble_words(filename):
    with open(filename, "r") as file:
        return set(word.strip().lower() for word in file)


# Game logic (remains largely the same)
class AWordGame:
    def __init__(self):
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
        self.__init__()

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

    def submit_word(self, word):
        word = word.lower()
        if word in self.all_possible_words and word not in self.found_words:
            self.found_words.add(word)
            word_points = self.calculate_word_points(word)
            self.points += word_points
            if len(word) == self.max_word_size:
                self.level_completed = True

            return f"Correct! You've earned {word_points} points!"
        elif word in self.all_possible_words:
            return f"'{word.upper()}' has already been found."
        else:
            if (len(word) > self.max_word_size) or (len(word) < self.min_word_size):
                return f"'{word.upper()}' is not of a valid size."
            else:
                self.points -= 2
                return f"'{word.upper()}' is not a valid word."


# Initialize game
game = AWordGame()

# Streamlit UI
st.title("A Word Game")
st.sidebar.title("Game Controls")

if st.sidebar.button("Start New Game"):
    game.start_new_game()

if st.sidebar.button("Reset Game"):
    game.reset()

st.write(f"Level: {game.level}")
st.write(f"Points: {game.points}")
st.write(f"Letters: {', '.join(game.letters)}")

word = st.text_input("Enter a word:")
if st.button("Submit Word"):
    result = game.submit_word(word)
    st.write(result)

if st.sidebar.checkbox("Show Possible Words"):
    st.write(game.all_possible_words)
