from flask import Flask, render_template, request, jsonify
import random
from itertools import permutations
from collections import Counter

app = Flask(__name__)


# Load the dictionary file
def load_scrabble_words(filename):
    with open(filename, "r") as file:
        return set(word.strip().lower() for word in file)


# Game logic moved to the server side
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
        # self.start_new_game()

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

            return {
                "valid": True,
                "points": self.points,
                "error_mess": "",
                "correct_word": word,
                "level_completed": self.level_completed,
            }
        elif word in self.all_possible_words:
            return {
                "valid": False,
                "points": self.points,
                "error_mess": f"'{word.upper()}' has already been found.",
                "level_completed": self.level_completed,
            }
        else:
            if (len(word) > self.max_word_size) or (len(word) < self.min_word_size):
                return {
                    "valid": False,
                    "points": self.points,
                    "error_mess": f"'{word.upper()}' is not of a valid size.",
                    "level_completed": self.level_completed,
                }
            else:
                self.points -= 2
                return {
                    "valid": False,
                    "points": self.points,
                    "error_mess": f"'{word.upper()}' is not a valid word.",
                    "level_completed": self.level_completed,
                }


game = AWordGame()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get_letters", methods=["GET"])
def get_letters():
    game.start_new_game()
    return jsonify(
        {
            "letters": game.letters,
            "points": game.points,
            "level": game.level,
            "possible_words": game.all_possible_words,
        }
    )


@app.route("/reload_game", methods=["GET"])
def reload_game():
    game.all_level_letters = []
    game.start_up()
    game.level = 0
    game.points = 0
    return jsonify(
        {
            "points": game.points,
            "level": game.level,
        }
    )


@app.route("/reset_game", methods=["POST"])
def reset_game():
    game.reset()
    return jsonify(
        {
            "ok": True,
        }
    )


@app.route("/submit_word", methods=["POST"])
def submit_word():
    word = request.form["word"]
    result = game.submit_word(word)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
