import random
import tkinter as tk
from itertools import permutations
from collections import Counter


# Load word list from nltk
# word_list = set(words.words())
BUTTON_FONT_SIZE = 24  # Increase the font size for larger buttons
BUTTON_WIDTH = 6  # Increase the width for larger buttons


class EveryWordGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Every Word Game")

        # Game variables
        self.max_word_size = 5
        self.min_word_size = 3
        self.max_num_words = 30
        self.min_num_words = 8
        self.letters = []

        self.level = 0
        self.max_level = 10
        self.level_label = tk.Label(
            root,
            text=f"Level: {self.level} of {self.max_level}",
            font=("Times New Roman", 18),
            anchor="e",
        )
        self.all_level_letters = []
        self.level_label.pack(side=tk.TOP, anchor="ne", padx=10, pady=10)

        self.all_possible_words = []
        self.found_words = set()
        self.current_word = []
        self.dictionary = self.load_scrabble_words("sowpodsDict.txt")

        self.points = 0  # Initialize points
        self.points_label = tk.Label(
            root,
            text=f"Points: {self.points}",
            font=("Times New Roman", 18),
            anchor="e",
        )
        self.points_label.pack(side=tk.TOP, anchor="ne", padx=10, pady=10)
        # GUI Components
        self.letters_label = tk.Label(root, text="", font=("Times New Roman", 24))
        self.letters_label.pack(pady=20)

        self.letter_buttons_frame = tk.Frame(root)
        self.letter_buttons_frame.pack(pady=10)

        self.proposed_word_frame = tk.Frame(root)
        self.proposed_word_frame.pack(pady=10)

        self.submit_button = tk.Button(
            root,
            text="Submit",
            font=("Times New Roman", BUTTON_FONT_SIZE),
            width=BUTTON_WIDTH * 2,
            command=self.submit_word,
        )
        self.submit_button.pack(pady=10)

        self.words_frame = tk.Frame(root)
        self.words_frame.pack(pady=20)

        self.new_game_button = tk.Button(
            root, text="Next Level", command=self.start_new_game
        )
        self.new_game_button.pack(pady=10)
        self.new_game_button.config(state=tk.DISABLED)

        self.error_label = tk.Label(
            root, text="", font=("Times New Roman", 14), fg="red"
        )
        self.error_label.pack(pady=5)

        self.start_up()

    def load_scrabble_words(self, filename):
        with open(filename, "r") as file:
            return set(word.strip().lower() for word in file)

    def define_level(self):
        self.level_label.config(text=f"Level: {self.level} of {self.max_level}")
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
            print(f"Finding level {levels}")
            self.level = levels
            self.define_level()

            while True:
                # self.letters = random.sample('abcdefghijklmnopqrstuvwxyz', counts=[2]*26, k=7)
                filtered_words = [
                    word for word in self.dictionary if len(word) == self.max_word_size
                ]
                # Randomly select a word from the filtered list and split it into letters
                selected_word = random.choice(filtered_words)
                self.letters = list(selected_word)
                random.shuffle(self.letters)
                self.find_possible_words()
                big_words = [
                    word
                    for word in self.all_possible_words
                    if ((len(word) >= self.max_word_size) and (len(word) <= 7))
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
        self.start_new_game()

    def start_new_game(self):
        self.new_game_button.config(state=tk.DISABLED)
        self.found_words.clear()
        self.current_word.clear()
        self.level += 1
        self.define_level()
        # Ensure 20 to 40 possible words and at least 2 seven-letter words
        self.letters = self.all_level_letters[self.level - 1]
        self.find_possible_words()

        while False:
            # self.letters = random.sample('abcdefghijklmnopqrstuvwxyz', counts=[2]*26, k=7)
            filtered_words = [
                word for word in self.dictionary if len(word) == self.max_word_size
            ]

            # Randomly select a word from the filtered list and split it into letters
            selected_word = random.choice(filtered_words)
            self.letters = list(selected_word)
            random.shuffle(self.letters)
            self.find_possible_words()
            big_words = [
                word
                for word in self.all_possible_words
                if ((len(word) >= self.max_word_size) and (len(word) <= 7))
            ]
            # print(len(big_words), len(self.all_possible_words))
            if (
                self.min_num_words <= len(self.all_possible_words) <= self.max_num_words
                and len(big_words) >= 1
            ):
                break

        # self.letters_label.config(text=" ".join(self.letters))

        # Clear previous display
        for widget in self.letter_buttons_frame.winfo_children():
            widget.destroy()
        for widget in self.proposed_word_frame.winfo_children():
            widget.destroy()
        for widget in self.words_frame.winfo_children():
            widget.destroy()

        # Create letter buttons
        for letter in self.letters:
            btn = tk.Button(
                self.letter_buttons_frame,
                text=letter.upper(),
                font=("Times New Roman", BUTTON_FONT_SIZE),
                width=BUTTON_WIDTH,
                command=lambda l=letter: self.add_letter(l),
            )
            btn.pack(side=tk.LEFT, padx=5)

        self.display_blanks()

    def find_possible_words(self):
        possible_words = set()

        # Generate permutations of all lengths from 4 to the length of the input letters
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

    def display_blanks(self):
        # Sort the possible words by length first, then alphabetically
        sorted_words = sorted(self.all_possible_words, key=lambda w: (len(w), w))

        columns = 3
        rows = len(sorted_words) // columns + (len(sorted_words) % columns > 0)

        for i in range(rows):
            row_frame = tk.Frame(self.words_frame)
            row_frame.pack(fill=tk.X)
            for j in range(columns):
                index = i + j * rows
                if index < len(sorted_words):
                    word = sorted_words[index]
                    blank_word = " ".join("_" for _ in word)
                    label = tk.Label(
                        row_frame,
                        text=blank_word,
                        font=("Times New Roman", 18),
                        anchor="w",
                        width=15,
                    )
                    label.word = word  # Attach the word to the label for reference
                    label.original_text = blank_word
                    label.pack(side=tk.LEFT, padx=10)

    def add_letter(self, letter):
        if len(self.current_word) < 7 and self.letters.count(
            letter
        ) > self.current_word.count(letter):
            self.current_word.append(letter)
            self.update_entry_display()

    def remove_letter(self, index):
        if index < len(self.current_word):
            del self.current_word[index]
            self.update_entry_display()

    def update_entry_display(self):
        # Clear proposed word frame
        for widget in self.proposed_word_frame.winfo_children():
            widget.destroy()

        points_by_length = [20, 20, 20, 30, 50, 80, 120]

        # Display the current word being formed with empty spaces showing point values
        # for i in range(len(points_by_length)):
        for i in range(self.max_word_size):
            if i < len(self.current_word):
                letter = self.current_word[i]
                btn = tk.Button(
                    self.proposed_word_frame,
                    text=letter.upper(),
                    font=("Times New Roman", BUTTON_FONT_SIZE),
                    width=BUTTON_WIDTH,
                    command=lambda idx=i: self.remove_letter(idx),
                )
            else:
                btn = tk.Button(
                    self.proposed_word_frame,
                    text=f"+{points_by_length[i]}",
                    font=("Times New Roman", BUTTON_FONT_SIZE),
                    width=BUTTON_WIDTH,
                    state=tk.DISABLED,
                )
            btn.pack(side=tk.LEFT, padx=5)  # Left-aligned with fixed spacing

        letter_count = Counter(self.letters)
        word_count = Counter(self.current_word)

        for num, letter, btn in zip(
            range(0, len(self.letters)),
            self.letters,
            self.letter_buttons_frame.winfo_children(),
        ):
            part_letter_count = Counter(self.letters[: num + 1])
            if (
                (word_count[letter] == 1)
                and (letter_count[letter] == 2)
                and (part_letter_count[letter] == 1)
            ):
                btn.config(state=tk.DISABLED, bg="darkgray")
            elif word_count[letter] >= letter_count[letter]:
                btn.config(state=tk.DISABLED, bg="darkgray")
            else:
                btn.config(state=tk.NORMAL, bg="white")
            btn.pack(side=tk.LEFT, padx=5)

    def calculate_word_points(self, word):
        points_by_length = [20, 20, 20, 30, 50, 80, 120]
        return sum(points_by_length[i] for i in range(len(word)))

    def submit_word(self):
        word = "".join(self.current_word).lower()
        if len(word) == 0:
            return
        if word in self.all_possible_words and word not in self.found_words:
            if len(word) >= self.max_word_size:
                self.new_game_button.config(state=tk.NORMAL)
            self.found_words.add(word)
            self.update_word_display(word)
            self.error_label.config(text="")  # Clear any previous error message

            # Update points
            word_points = self.calculate_word_points(word)
            self.points += word_points
            self.points_label.config(text=f"Points: {self.points}")
        else:
            if (len(word) > self.max_word_size) or (len(word) < self.min_word_size):
                self.error_label.config(
                    text=f"'{word.upper()}' is not of a valid size."
                )
            else:
                self.points -= 2
                self.points_label.config(text=f"Points: {self.points}")
                self.error_label.config(
                    text=f"'{word.upper()}' is not a valid word."
                )  # Show error message

        self.reset_word()
        self.proposed_word_frame.focus_set()
        if len(self.found_words) == len(self.all_possible_words):
            self.new_game_button.config(state=tk.NORMAL)

    def update_word_display(self, word):
        for row_frame in self.words_frame.winfo_children():
            for label in row_frame.winfo_children():
                if label.word == word:
                    label.config(text=" ".join(word.upper()))

    def reset_word(self):
        self.current_word.clear()
        self.update_entry_display()


if __name__ == "__main__":
    root = tk.Tk()
    game = EveryWordGame(root)
    root.mainloop()
