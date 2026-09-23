"""Math Racer: a tkinter racing game in which maths questions drive the bike.

The program is written in two layers. Everything above ``MathRacerApp`` holds
the rules of the game and the saved files and never imports a widget, so that
logic can be read and tested on its own. Everything from ``MathRacerApp``
downwards draws the screens and calls into that logic.

The window follows the stacked frame pattern taught by GeeksforGeeks and Real
Python: a single ``tk.Tk`` subclass acts as the controller, every screen is a
``tk.Frame`` subclass gridded into the same cell, and ``tkraise`` lifts the
wanted screen to the top of the stacking order.
"""

import hashlib
import math
import os
import random
import secrets
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from PIL import Image, ImageTk

# winsound ships only with Windows, so the beep is skipped on any other system.
try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False


# Every saved file and image sits beside this script rather than in whatever
# folder the program happens to be launched from.
FOLDER = os.path.dirname(os.path.abspath(__file__))

ACCOUNTS_FILE = os.path.join(FOLDER, "accounts.txt")
SETTINGS_FILE = os.path.join(FOLDER, "settings.txt")
RECORDS_FILE = os.path.join(FOLDER, "records.txt")
BIKE_FILE = os.path.join(FOLDER, "Bike.png")
BACK_FILE = os.path.join(FOLDER, "Back.png")

# The two typefaces the game uses, named once so they can be swapped easily.
TITLE_TYPEFACE = "Impact"
BODY_TYPEFACE = "Segoe UI"

# Every size of text in the game, so nothing is sized by a loose number.
TITLE_FONT = (TITLE_TYPEFACE, 58)
HEADING_FONT = (TITLE_TYPEFACE, 38)
BAND_FONT = (TITLE_TYPEFACE, 24)
SCORE_BIG_FONT = (TITLE_TYPEFACE, 64)
STAT_FONT = (BODY_TYPEFACE, 19, "bold")
SUBHEADING_FONT = (BODY_TYPEFACE, 15, "bold")
QUESTION_FONT = (BODY_TYPEFACE, 15, "bold")
GATE_FONT = (BODY_TYPEFACE, 21, "bold")
SCORE_FONT = (BODY_TYPEFACE, 10, "bold")
LABEL_FONT = (BODY_TYPEFACE, 12, "bold")
ENTRY_FONT = (BODY_TYPEFACE, 13)
BUTTON_FONT = (BODY_TYPEFACE, 11, "bold")
PLAY_FONT = (BODY_TYPEFACE, 16, "bold")
SMALL_FONT = (BODY_TYPEFACE, 9)

# The colours the whole game is painted in. The dark background and yellow
# highlight come from the concept sketches, and dark on light was swapped for
# light on dark because white writing on yellow was very hard to read.
BACKGROUND = "#12141c"
PANEL = "#1c2030"
PANEL_EDGE = "#2e3446"
SHADOW = "#05060a"
ACCENT = "#ffd23f"
ACCENT_DEEP = "#e0a800"
TEXT = "#f2f4f8"
TEXT_DIM = "#9aa1b4"
BUTTON_BG = "#2a3040"
BUTTON_ACTIVE = "#3b435a"

# The window, and the canvas every screen is drawn on inside it.
WINDOW_SIZE = "700x700"
CANVAS_WIDTH = 650
CANVAS_HEIGHT = 650
CANVAS_PAD = 5

# The speed shown on the dial for each difficulty, which is also how fast the
# bike drives up the road once it is divided by DRIVE_DIVISOR.
SPEEDS = {"Easy": 20, "Medium": 30, "Hard": 40}

# The speedometer that the difficulty screen is drawn as.
GAUGE_X = 325
GAUGE_Y = 395
GAUGE_RADIUS = 170
GAUGE_BAND = 24
NEEDLE_LENGTH = 132

# Where the needle points for each difficulty, in degrees round the gauge.
# 180 is due left and 0 is due right, so Easy sits low and Hard sits high.
NEEDLE_ANGLES = {"Easy": 150, "Medium": 90, "Hard": 30}

# Bright shades, which read well against the dark background and still look
# like the green through to red of a real rev counter.
ZONE_COLOURS = {"Easy": "#3ddc84", "Medium": "#ffb020", "Hard": "#ff5c5c"}

# Where each band's wording sits, placed by hand so it clears the dial.
LABEL_SPOTS = {"Easy": (132, 282, tk.E), "Medium": (325, 166, tk.S), "Hard": (518, 282, tk.W)}

# How far the needle turns each frame, and how long it waits between frames.
NEEDLE_STEP = 4
NEEDLE_DELAY = 12

# The rules a username and a password have to follow.
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 12
PASSWORD_MIN_LENGTH = 5

# Bytes of randomness per salt. token_hex returns two characters per byte.
SALT_LENGTH = 8

# Built from PASSWORD_MIN_LENGTH so the message cannot drift from the check.
PASSWORD_RULES = (
    "Your password must be at least " + str(PASSWORD_MIN_LENGTH)
    + " characters long, and include at least 1 number and 1 capital letter."
)

# How many drivers each difficulty shows on the leaderboard.
LEADERBOARD_ROWS = 10

# Where the three boards sit, and where each column of a row lines up inside them.
BOARD_TOP = 128
BOARD_BOTTOM = 556
BOARD_WIDTH = 190
BOARD_GAP = 20
NAME_OFFSET = 12
SCORE_OFFSET = 132
TIME_OFFSET = 180
ROW_TOP = 228
ROW_HEIGHT = 33

# The number of questions a race can be set to.
QUESTIONS_MIN = 5
QUESTIONS_MAX = 50

# The settings the game falls back on until settings.txt has been read.
DEFAULT_SOUND = True
DEFAULT_QUESTIONS = 10

# The pitch and length of the beep that plays when an error box appears.
BEEP_HERTZ = 700
BEEP_MILLISECONDS = 150

# The topics each difficulty draws from. Easy is plain arithmetic, Medium adds
# powers, fractions, percentages and number theory, and Hard moves on to
# algebra, geometry, statistics and basic calculus, so every level teaches
# something the one below it does not.
TOPICS = {
    "Easy": ["Addition", "Subtraction", "Multiplication", "Division"],
    "Medium": ["Exponents", "Square Roots", "Fractions", "Percentages",
               "Prime Numbers", "Highest Common Factor", "Lowest Common Multiple"],
    "Hard": ["Algebra", "Area", "Perimeter", "Volume", "Mean", "Median",
             "Mode", "Differentiation", "Integration"],
}

# Points won for a right answer at each difficulty, so harder is worth more.
POINTS = {"Easy": 10, "Medium": 20, "Hard": 30}

# Points lost for a wrong answer, whatever the difficulty.
WRONG_PENALTY = 5

# What to say at the end, listed worst last so the first match wins. Each pair
# is the lowest accuracy that earns that wording.
RESULT_MESSAGES = [
    (90, "Superb driving. Almost everything right."),
    (70, "A strong race, with only a few slips."),
    (50, "A steady run. Worth another lap."),
    (25, "Getting there. Keep practising these topics."),
    (0, "A tough race. Try an easier level to build up."),
]

# The three lanes the bike drives between, and where the middle of each one is.
LANE_COUNT = 3
LANE_X = [108, 325, 542]

# Where everything sits on the race track.
QUESTION_Y = 50
SCOREBOARD_Y = 105
INSTRUCTION_Y = 133
HEADER_BOTTOM = 152
PROGRESS_TOP = 152
PROGRESS_BOTTOM = 158
PROGRESS_LEFT = 60
PROGRESS_RIGHT = 590
ROAD_TOP = 164
ROAD_BOTTOM = 600
GATE_Y = 228
BIKE_Y = 540
BOTTOM_ROW_Y = 624

# The gates pull up just short of the bike rather than landing on top of it,
# so the number the bike chose stays readable.
GATE_STOP_Y = 462

# How far in from each side the solid road edge is painted.
ROAD_EDGE = 14

# What the player has to do, spelled out so nobody has to guess.
DRIVING_HELP = "Left and right arrows to pick a lane, then Space or Enter to drive through it."

# The size of the answer gates the bike has to drive through.
GATE_WIDTH = 168
GATE_HEIGHT = 54

# The dash pattern of the lane markings, and the length of one whole repeat,
# which the scrolling wraps around so the markings never jump.
LANE_DASH = (26, 24)
DASH_CYCLE = 50

# How long the screen waits between frames, and how the dial speed becomes
# pixels moved per frame. Dividing keeps the dial numbers looking like a
# speedometer while the gates still reach the bike in about a second.
FRAME_DELAY = 40
DRIVE_DIVISOR = 3

# How long the right or wrong message stays up before the next question.
FEEDBACK_PAUSE = 950

# The race is drawn on a road, a shade lighter than the menus so it reads as
# tarmac rather than as another screen.
ROAD_COLOUR = "#262a35"
LANE_LINE_COLOUR = "#e9ecf3"
EDGE_COLOUR = "#4a5163"
GATE_COLOUR = "#12141c"
CORRECT_COLOUR = "#4ade80"
WRONG_COLOUR = "#f87171"

# The sizes the two pictures are shrunk to before they are shown.
BIKE_SIZE = (100, 100)
BACK_SIZE = (25, 25)

# The tick box on the settings screen. The clam theme draws a very small box by
# default, so it is sized here to match the writing sitting beside it.
CHECK_BOX_SIZE = 15
CHECK_BOX_MARGIN = 4


def highest_common_factor(first, second):
    """Return the highest common factor of two numbers using Euclid's method.

    The pair is replaced over and over by the smaller number and the remainder
    until nothing is left over, which leaves the factor in ``first``.
    """
    while second != 0:
        first, second = second, first % second
    return first


def simplify_fraction(top, bottom):
    """Return a fraction in its simplest form, or a whole number when it divides exactly."""
    divisor = highest_common_factor(top, bottom)
    top = top // divisor
    bottom = bottom // divisor

    if bottom == 1:
        return str(top)

    return str(top) + "/" + str(bottom)


def is_prime(number):
    """Return True when a number is prime.

    Only factors up to the square root are tried, because a factor above it
    would already have been found paired with one below it.
    """
    if number < 2:
        return False

    checker = 2
    while checker * checker <= number:
        if number % checker == 0:
            return False
        checker = checker + 1

    return True


def format_time(seconds):
    """Return a number of seconds written as minutes and seconds, for example 2:05."""
    minutes = seconds // 60
    rest = seconds % 60
    return str(minutes) + ":" + str(rest).zfill(2)


def result_message(accuracy):
    """Return the closing wording that matches how accurate the race was."""
    for lowest, message in RESULT_MESSAGES:
        if accuracy >= lowest:
            return message

    return RESULT_MESSAGES[-1][1]


class Validator:
    """Checks typed input against the rules of the game.

    Every method returns the reason the input is rejected, or an empty string
    when it passes, so a caller can test the result and show the reason in the
    same two lines. The messages say what to do about the problem rather than
    only naming it.
    """

    @staticmethod
    def check_username(username):
        """Return the reason a username is rejected, or an empty string if it passes."""
        if username == "":
            return "You have not typed a username. Please type one into the username box."

        if len(username) < USERNAME_MIN_LENGTH:
            return ("Your username is only " + str(len(username))
                    + " characters long. Please make it at least "
                    + str(USERNAME_MIN_LENGTH) + " characters.")

        if len(username) > USERNAME_MAX_LENGTH:
            return ("Your username is " + str(len(username))
                    + " characters long, which is too long. Please shorten it to "
                    + str(USERNAME_MAX_LENGTH) + " characters or fewer.")

        if " " in username:
            return ("Your username has a space in it. Please use an underscore "
                    "instead, for example math_racer.")

        if "," in username:
            return ("Your username has a comma in it. Commas separate the details "
                    "inside the accounts file, so please use a different character.")

        return ""

    @staticmethod
    def check_password(password):
        """Return the reason a password is rejected, or an empty string if it passes."""
        if password == "":
            return "You have not typed a password. Please type one into the password box."

        if len(password) < PASSWORD_MIN_LENGTH:
            short_by = PASSWORD_MIN_LENGTH - len(password)
            return ("Your password is only " + str(len(password))
                    + " characters long. Please add " + str(short_by)
                    + " more so it is at least " + str(PASSWORD_MIN_LENGTH) + " characters.")

        # One pass over the password, checking for both requirements at once.
        has_number = False
        has_capital = False
        for letter in password:
            if letter.isdigit():
                has_number = True
            if letter.isupper():
                has_capital = True

        if not has_number:
            return ("Your password does not contain a number. Please add at least "
                    "1 number, for example 4 or 9.")

        if not has_capital:
            return ("Your password does not contain a capital letter. Please add at "
                    "least 1 capital letter, for example A or M.")

        if "," in password:
            return ("Your password has a comma in it. Commas separate the details "
                    "inside the accounts file, so please use a different character.")

        return ""

    @staticmethod
    def check_questions(typed):
        """Return the reason a questions per race entry is rejected, or an empty string."""
        if typed == "":
            return ("You have not typed how many questions each race should have. "
                    "Please type a whole number between " + str(QUESTIONS_MIN)
                    + " and " + str(QUESTIONS_MAX) + ".")

        # Checking every character rejects decimals, minus signs, spaces and symbols.
        for letter in typed:
            if letter not in "0123456789":
                return ("Questions per race must be a whole number, but you typed "
                        + typed + ". Please use digits only, with no spaces, decimal "
                        "points or symbols, for example 10.")

        number = int(typed)

        if number < QUESTIONS_MIN:
            return ("A race of " + typed + " questions is too short. Please choose at least "
                    + str(QUESTIONS_MIN) + ".")

        if number > QUESTIONS_MAX:
            return ("A race of " + typed + " questions is too long. Please choose "
                    + str(QUESTIONS_MAX) + " or fewer.")

        return ""


class AccountStore:
    """Reads and writes the accounts file, and checks passwords against it.

    A password is never written down. Each account keeps a random salt and the
    SHA-256 hash of that salt joined to the password, which is the salting and
    hashing method the GeeksforGeeks password tutorial describes. Signing in
    hashes what was typed the same way and compares the two hashes.
    """

    def __init__(self, path=ACCOUNTS_FILE):
        self.path = path

    @staticmethod
    def hash_password(password, salt):
        """Return the SHA-256 hash of a salt joined to a password."""
        return hashlib.sha256((salt + password).encode()).hexdigest()

    def load(self):
        """Return every saved account as a dictionary of username to salt and hash."""
        accounts = {}

        try:
            with open(self.path) as accounts_file:
                for line in accounts_file:

                    # Split each line into the username, the salt and the hash.
                    parts = line.strip().split(",")

                    # Ignore malformed rows rather than letting one bad line
                    # break the whole load.
                    if len(parts) == 3 and parts[0] != "" and parts[1] != "" and parts[2] != "":
                        accounts[parts[0]] = (parts[1], parts[2])

        # No file exists until the first account is saved.
        except FileNotFoundError:
            pass

        return accounts

    def exists(self, username):
        """Return True when an account is already saved under this username."""
        return username in self.load()

    def add(self, username, password):
        """Save a new account, storing a fresh salt and hash instead of the password."""
        salt = secrets.token_hex(SALT_LENGTH)
        hashed = self.hash_password(password, salt)

        with open(self.path, "a") as accounts_file:
            accounts_file.write(username + "," + salt + "," + hashed + "\n")

    def check(self, username, password):
        """Return True when this password matches the one saved for this username."""
        accounts = self.load()

        if username not in accounts:
            return False

        salt, hashed = accounts[username]
        return self.hash_password(password, salt) == hashed


class SettingsStore:
    """Holds the two preferences and keeps them in the settings file.

    Each line is stored as name=value, for example questions=20. A value that
    is missing or damaged is ignored so the setting keeps its default rather
    than stopping the program.
    """

    def __init__(self, path=SETTINGS_FILE):
        self.path = path
        self.sound_on = DEFAULT_SOUND
        self.questions_per_race = DEFAULT_QUESTIONS

    def load(self):
        """Read the saved settings, ignoring any value that is missing or damaged."""
        try:
            with open(self.path) as settings_file:
                for line in settings_file:

                    parts = line.strip().split("=")
                    if len(parts) != 2:
                        continue

                    name = parts[0]
                    value = parts[1]

                    if name == "sound" and value in ("on", "off"):
                        self.sound_on = value == "on"

                    elif name == "questions" and Validator.check_questions(value) == "":
                        self.questions_per_race = int(value)

        # No file exists until the settings are saved for the first time.
        except FileNotFoundError:
            pass

    def save(self):
        """Write both settings back out, replacing whatever was there before."""
        if self.sound_on:
            sound_value = "on"
        else:
            sound_value = "off"

        with open(self.path, "w") as settings_file:
            settings_file.write("sound=" + sound_value + "\n")
            settings_file.write("questions=" + str(self.questions_per_race) + "\n")


class RecordStore:
    """Reads and writes the finished races that the leaderboard is built from.

    Each line is difficulty,username,score,seconds. A row is only trusted when
    the level is a real one and both numbers are actually numbers, so one bad
    line cannot break the board.
    """

    def __init__(self, path=RECORDS_FILE):
        self.path = path

    def add(self, difficulty, username, score, seconds):
        """Add one finished race onto the end of the records file."""
        with open(self.path, "a") as records_file:
            records_file.write(difficulty + "," + username + "," + str(score)
                               + "," + str(seconds) + "\n")

    def load(self):
        """Return every saved race as a list of tuples, skipping damaged rows."""
        records = []

        try:
            with open(self.path) as records_file:
                for line in records_file:

                    parts = line.strip().split(",")

                    if len(parts) != 4:
                        continue

                    if (parts[0] in TOPICS and parts[1] != ""
                            and parts[2].isdigit() and parts[3].isdigit()):
                        records.append((parts[0], parts[1], int(parts[2]), int(parts[3])))

        # No file exists until somebody has finished a race.
        except FileNotFoundError:
            pass

        return records

    @staticmethod
    def rank(record):
        """Return the sort key that puts the highest score first, then the quickest time.

        The score is negated because sorting counts upwards, so the largest
        score ends up at the front of the list.
        """
        return (-record[2], record[3])

    def best(self, difficulty, how_many):
        """Return the best runs for one difficulty, one row per driver."""
        best = {}

        for record in self.load():
            if record[0] != difficulty:
                continue

            # Only a driver's best run is kept, so nobody can fill the whole board.
            name = record[1]
            if name not in best or self.rank(record) < self.rank(best[name]):
                best[name] = record

        ranked = list(best.values())
        ranked.sort(key=self.rank)
        return ranked[:how_many]


class Question:
    """One question, the answer it expects, and the topic it came from."""

    def __init__(self, wording, answer, topic):
        self.wording = wording
        self.answer = answer
        self.topic = topic

    def is_correct(self, typed):
        """Return True when a given answer matches the right one, ignoring stray spaces."""
        return typed.strip() == self.answer

    def wrong_answers(self):
        """Return two believable wrong answers to sit in the other two lanes."""
        wrongs = []

        # A fraction needs fraction decoys, or the right one would stand out.
        if "/" in self.answer:
            top, bottom = self.answer.split("/")
            top = int(top)
            bottom = int(bottom)
            guesses = [str(top + 1) + "/" + str(bottom),
                       str(top) + "/" + str(bottom + 2),
                       str(bottom) + "/" + str(top),
                       str(top + 2) + "/" + str(bottom)]
            random.shuffle(guesses)

            for guess in guesses:
                if guess != self.answer and guess not in wrongs:
                    wrongs.append(guess)
                if len(wrongs) == 2:
                    break

            return wrongs

        # Whole number answers get decoys a little either side of the truth.
        number = int(self.answer)
        guesses = [number - 2, number - 1, number + 1, number + 2, number + 10]
        random.shuffle(guesses)

        for guess in guesses:
            # Never offer a negative decoy when the real answer is positive.
            if guess > 0 and str(guess) != self.answer and str(guess) not in wrongs:
                wrongs.append(str(guess))
            if len(wrongs) == 2:
                break

        # Widen the gap until two decoys are found, however small the answer.
        gap = 3
        while len(wrongs) < 2:
            guess = str(number + gap)
            if guess != self.answer and guess not in wrongs:
                wrongs.append(guess)
            gap = gap + 1

        return wrongs

    def choices(self):
        """Return all three choices in a random order, ready to fill the lanes."""
        options = self.wrong_answers()
        options.append(self.answer)
        random.shuffle(options)
        return options


class QuestionFactory:
    """Builds a random question for a difficulty.

    Every topic name is matched to the method that builds that kind of
    question, so ``make`` can look the right one up in a dictionary instead of
    working through a long if else chain.
    """

    def __init__(self):
        self.builders = {"Addition": self.make_addition,
                         "Subtraction": self.make_subtraction,
                         "Multiplication": self.make_multiplication,
                         "Division": self.make_division,
                         "Exponents": self.make_exponents,
                         "Square Roots": self.make_square_root,
                         "Fractions": self.make_fraction,
                         "Percentages": self.make_percentage,
                         "Prime Numbers": self.make_prime,
                         "Highest Common Factor": self.make_factor,
                         "Lowest Common Multiple": self.make_multiple,
                         "Algebra": self.make_algebra,
                         "Area": self.make_area,
                         "Perimeter": self.make_perimeter,
                         "Volume": self.make_volume,
                         "Mean": self.make_mean,
                         "Median": self.make_median,
                         "Mode": self.make_mode,
                         "Differentiation": self.make_differentiation,
                         "Integration": self.make_integration}

    def make(self, difficulty):
        """Build one random question from the topics that difficulty uses."""
        topic = random.choice(TOPICS[difficulty])
        return self.builders[topic]()

    def make_addition(self):
        """Build an addition question."""
        first = random.randint(2, 50)
        second = random.randint(2, 50)
        return Question("What is " + str(first) + " + " + str(second) + "?",
                        str(first + second), "Addition")

    def make_subtraction(self):
        """Build a subtraction question, larger number first so it is never negative."""
        first = random.randint(20, 60)
        second = random.randint(2, 19)
        return Question("What is " + str(first) + " - " + str(second) + "?",
                        str(first - second), "Subtraction")

    def make_multiplication(self):
        """Build a times table question."""
        first = random.randint(2, 12)
        second = random.randint(2, 12)
        return Question("What is " + str(first) + " x " + str(second) + "?",
                        str(first * second), "Multiplication")

    def make_division(self):
        """Build a division question from the answer, which keeps it exact."""
        divisor = random.randint(2, 12)
        answer = random.randint(2, 12)
        return Question("What is " + str(divisor * answer) + " / " + str(divisor) + "?",
                        str(answer), "Division")

    def make_exponents(self):
        """Build a power question.

        Squares can use bigger numbers than cubes and still be worth doing in
        your head, so the range depends on the power.
        """
        power = random.randint(2, 3)

        if power == 2:
            base = random.randint(2, 20)
        else:
            base = random.randint(2, 10)

        return Question("What is " + str(base) + " to the power of " + str(power) + "?",
                        str(base ** power), "Exponents")

    def make_square_root(self):
        """Build a square root question by squaring the answer first."""
        answer = random.randint(2, 30)
        return Question("What is the square root of " + str(answer * answer) + "?",
                        str(answer), "Square Roots")

    def make_fraction(self):
        """Build an addition of two fractions that share a denominator."""
        bottom = random.choice([4, 6, 8, 10, 12])
        first = random.randint(1, bottom - 2)
        second = random.randint(1, bottom - first - 1)
        wording = ("What is " + str(first) + "/" + str(bottom) + " + " + str(second)
                   + "/" + str(bottom) + "? Give your answer as a fraction in its "
                   "simplest form.")
        return Question(wording, simplify_fraction(first + second, bottom), "Fractions")

    def make_percentage(self):
        """Build a percentage question that always works out to a whole number.

        The amount is a multiple of 20 and the percentage is a simple one,
        which together guarantee the answer divides exactly.
        """
        percent = random.choice([10, 20, 25, 50, 75])
        amount = random.randint(1, 20) * 20
        return Question("What is " + str(percent) + "% of " + str(amount) + "?",
                        str(percent * amount // 100), "Percentages")

    def make_prime(self):
        """Build a question asking for the next prime number after a starting point."""
        start = random.randint(5, 150)
        answer = start + 1
        while not is_prime(answer):
            answer = answer + 1
        return Question("What is the next prime number after " + str(start) + "?",
                        str(answer), "Prime Numbers")

    def make_factor(self):
        """Build a highest common factor question.

        Both numbers are built from a shared factor, so the answer is rarely
        just 1 and the question is actually worth working out.
        """
        shared = random.randint(2, 12)
        first = shared * random.randint(2, 9)
        second = first

        # Asking for the factor of a number and itself looks like a mistake,
        # so keep drawing until the two numbers are actually different.
        while second == first:
            second = shared * random.randint(2, 9)

        return Question("What is the highest common factor of " + str(first) + " and "
                        + str(second) + "?", str(highest_common_factor(first, second)),
                        "Highest Common Factor")

    def make_multiple(self):
        """Build a lowest common multiple question.

        Two numbers multiplied together, divided by their highest common
        factor, always gives their lowest common multiple.
        """
        first = random.randint(3, 20)
        second = first

        # Two identical numbers would make the question trivial.
        while second == first:
            second = random.randint(3, 20)

        answer = first * second // highest_common_factor(first, second)
        return Question("What is the lowest common multiple of " + str(first) + " and "
                        + str(second) + "?", str(answer), "Lowest Common Multiple")

    def make_algebra(self):
        """Build a one step equation, working backwards from a chosen whole number x."""
        answer = random.randint(2, 12)
        times = random.randint(2, 9)
        plus = random.randint(1, 20)
        wording = ("Solve for x:   " + str(times) + "x + " + str(plus) + " = "
                   + str(times * answer + plus))
        return Question(wording, str(answer), "Algebra")

    def make_area(self):
        """Build a rectangle area question."""
        width = random.randint(3, 15)
        height = random.randint(3, 15)
        wording = ("A rectangle is " + str(width) + " cm wide and " + str(height)
                   + " cm tall. What is its area in square cm?")
        return Question(wording, str(width * height), "Area")

    def make_perimeter(self):
        """Build a rectangle perimeter question."""
        width = random.randint(3, 15)
        height = random.randint(3, 15)
        wording = ("A rectangle is " + str(width) + " cm wide and " + str(height)
                   + " cm tall. What is its perimeter in cm?")
        return Question(wording, str(2 * (width + height)), "Perimeter")

    def make_volume(self):
        """Build a cuboid volume question."""
        length = random.randint(2, 12)
        width = random.randint(2, 12)
        height = random.randint(2, 12)
        wording = ("A box is " + str(length) + " cm long, " + str(width) + " cm wide and "
                   + str(height) + " cm tall. What is its volume in cubic cm?")
        return Question(wording, str(length * width * height), "Volume")

    def make_mean(self):
        """Build a mean question whose numbers happen to divide exactly.

        Ordinary numbers are drawn until their total divides by how many there
        are. Forcing every number to be a multiple of the count would work too,
        but it makes the numbers look obviously picked.
        """
        count = random.choice([3, 4, 5])

        numbers = []
        while len(numbers) == 0 or sum(numbers) % count != 0:
            numbers = []
            for spare in range(count):
                numbers.append(random.randint(2, 30))

        total = sum(numbers)
        wording = "What is the mean of " + ", ".join(str(number) for number in numbers) + "?"
        return Question(wording, str(total // count), "Mean")

    def make_median(self):
        """Build a median question with an odd count, so the middle is a single value."""
        count = random.choice([3, 5, 7])
        numbers = random.sample(range(1, 60), count)
        middle = sorted(numbers)[count // 2]
        wording = "What is the median of " + ", ".join(str(number) for number in numbers) + "?"
        return Question(wording, str(middle), "Median")

    def make_mode(self):
        """Build a mode question with exactly one most common value.

        One value is planted three times, and nothing else is allowed to appear
        more than twice, so only one number can be the mode.
        """
        common = random.randint(1, 20)
        numbers = [common, common, common]

        while len(numbers) < 7:
            spare = random.randint(1, 20)
            if spare != common and numbers.count(spare) < 2:
                numbers.append(spare)

        random.shuffle(numbers)
        wording = "What is the mode of " + ", ".join(str(number) for number in numbers) + "?"
        return Question(wording, str(common), "Mode")

    def make_differentiation(self):
        """Build a differentiation question answered at a point.

        The power rule says the derivative of a x^n is n a x^(n-1). Asking for
        its value at a point keeps the answer a plain number, so the gates
        never have to hold letters.
        """
        coefficient = random.randint(2, 9)
        power = random.randint(2, 4)
        at = random.randint(1, 5)
        gradient = power * coefficient * (at ** (power - 1))
        wording = ("y = " + str(coefficient) + "x^" + str(power)
                   + ".   What is dy/dx when x = " + str(at) + "?")
        return Question(wording, str(gradient), "Differentiation")

    def make_integration(self):
        """Build a definite integral question that divides exactly.

        Integrating a x^n from 0 to b gives a b^(n+1) / (n+1), so the
        coefficient is chosen as a multiple of n+1.
        """
        power = random.randint(1, 3)
        coefficient = (power + 1) * random.randint(1, 5)
        upper = random.randint(2, 5)
        area = coefficient * (upper ** (power + 1)) // (power + 1)

        # Nobody writes x^1, so the power is left off when it is one.
        if power == 1:
            equation = str(coefficient) + "x"
        else:
            equation = str(coefficient) + "x^" + str(power)

        wording = ("What is the area under y = " + equation + " between x = 0 and x = "
                   + str(upper) + "?")
        return Question(wording, str(area), "Integration")


class Race:
    """One race: the questions asked, the score won, and the clock.

    The clock starts as soon as the race is built and is stopped the moment the
    last question has been marked, so the time saved to the leaderboard cannot
    keep growing while the results are being read.
    """

    def __init__(self, difficulty, total):
        self.difficulty = difficulty
        self.total = total
        self.factory = QuestionFactory()
        self.question = self.factory.make(difficulty)
        self.asked = 0
        self.correct = 0
        self.score = 0
        self.started = time.time()
        self.taken = 0

    def mark(self, typed):
        """Mark the given answer, move the score, and return True when it was right."""
        self.asked = self.asked + 1

        # Stop the clock the moment the last question has been answered.
        if self.is_finished():
            self.taken = int(time.time() - self.started)

        if self.question.is_correct(typed):
            self.correct = self.correct + 1
            self.score = self.score + POINTS[self.difficulty]
            return True

        # A wrong answer costs points, but the score never drops below zero.
        self.score = self.score - WRONG_PENALTY
        if self.score < 0:
            self.score = 0

        return False

    def next_question(self):
        """Move on to a new question, unless the race has already finished."""
        if not self.is_finished():
            self.question = self.factory.make(self.difficulty)

    def is_finished(self):
        """Return True once every question has been asked."""
        return self.asked >= self.total

    def accuracy(self):
        """Return the percentage answered correctly so far."""
        if self.asked == 0:
            return 0
        return round(100 * self.correct / self.asked)

    def seconds(self):
        """Return how long the race took, or how long it has been running so far."""
        if self.is_finished():
            return self.taken

        return int(time.time() - self.started)


class MathRacerApp(tk.Tk):
    """The main window, which owns the saved data and swaps between screens.

    Every screen is built once and gridded into the same cell of one container,
    so they sit stacked on top of each other. ``show_frame`` lifts the wanted
    screen with ``tkraise`` rather than destroying and rebuilding widgets, which
    is the pattern the GeeksforGeeks multi page tutorial uses.
    """

    def __init__(self):
        super().__init__()
        self.title("Math Racer")
        self.geometry(WINDOW_SIZE)
        self.configure(bg=BACKGROUND)

        # The saved data, loaded once and shared with every screen.
        self.settings = SettingsStore()
        self.settings.load()
        self.accounts = AccountStore()
        self.records = RecordStore()

        # What the player has chosen so far, and the race they are running.
        self.username = ""
        self.difficulty = "Easy"
        self.race = None

        self.build_styles()
        self.load_images()

        # One container holding every screen, stretched to fill the window.
        container = tk.Frame(self, bg=BACKGROUND)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Build each screen and stack it in the same cell as all the others.
        self.frames = {}
        self.current = None
        for screen in (LoginPage, MenuPage, DifficultyPage, SettingsPage,
                       LeaderboardPage, RacePage, ResultsPage):
            frame = screen(container, self)
            self.frames[screen] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage)

    def build_styles(self):
        """Set up the ttk styles the whole game is painted with.

        The clam theme is chosen because the Windows themes draw their buttons
        through the native visual styles API and quietly ignore a background
        colour, which would lose the dark look entirely.
        """
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TButton", font=BUTTON_FONT, background=BUTTON_BG, foreground=TEXT,
                        borderwidth=0, focuscolor=BUTTON_BG, padding=(8, 10))
        style.map("TButton", background=[("active", BUTTON_ACTIVE)],
                  foreground=[("active", ACCENT)])

        style.configure("Menu.TButton", width=15, padding=(8, 12))
        style.map("Menu.TButton", background=[("active", BUTTON_ACTIVE)],
                  foreground=[("active", ACCENT)])

        # The one button on each screen that carries the main action.
        style.configure("Accent.TButton", background=ACCENT, foreground=BACKGROUND,
                        focuscolor=ACCENT, padding=(8, 12))
        style.map("Accent.TButton", background=[("active", ACCENT_DEEP)],
                  foreground=[("active", BACKGROUND)])

        style.configure("Play.TButton", font=PLAY_FONT, width=18, background=ACCENT,
                        foreground=BACKGROUND, focuscolor=ACCENT, padding=(8, 12))
        style.map("Play.TButton", background=[("active", ACCENT_DEEP)],
                  foreground=[("active", BACKGROUND)])

        # The quiet button that swaps the sign in screen between its two modes.
        style.configure("Link.TButton", font=SMALL_FONT, background=BACKGROUND,
                        foreground=TEXT_DIM, focuscolor=BACKGROUND, padding=(4, 4))
        style.map("Link.TButton", background=[("active", BACKGROUND)],
                  foreground=[("active", ACCENT)])

        # Each difficulty button is lettered in the colour of its band on the dial.
        for level in ZONE_COLOURS:
            style.configure(level + ".TButton", width=11, foreground=ZONE_COLOURS[level],
                            padding=(8, 12))
            style.map(level + ".TButton", background=[("active", BUTTON_ACTIVE)],
                      foreground=[("active", ZONE_COLOURS[level])])

        style.configure("Dark.TEntry", font=ENTRY_FONT, fieldbackground=BACKGROUND,
                        foreground=TEXT, insertcolor=ACCENT, borderwidth=2)
        style.map("Dark.TEntry", bordercolor=[("focus", ACCENT)])

        style.configure("Panel.TCheckbutton", font=LABEL_FONT, background=PANEL,
                        foreground=TEXT, focuscolor=PANEL, indicatorsize=CHECK_BOX_SIZE,
                        indicatormargin=CHECK_BOX_MARGIN, indicatorbackground=BACKGROUND,
                        indicatorforeground=ACCENT, upperbordercolor=PANEL_EDGE,
                        lowerbordercolor=PANEL_EDGE)
        style.map("Panel.TCheckbutton", background=[("active", PANEL)],
                  foreground=[("active", ACCENT)],
                  indicatorbackground=[("selected", BACKGROUND), ("active", BACKGROUND)])

    def load_images(self):
        """Open and shrink the two pictures once, and keep a reference to each.

        Tkinter does not hold on to a PhotoImage by itself, so an image with no
        reference left in Python is collected and the picture goes blank. Both
        are kept as attributes of the window for exactly that reason.
        """
        bike = Image.open(BIKE_FILE).resize(BIKE_SIZE)
        self.bike_img = ImageTk.PhotoImage(bike)

        back = Image.open(BACK_FILE).resize(BACK_SIZE)
        self.back_img = ImageTk.PhotoImage(back)

    def show_frame(self, screen):
        """Raise one screen to the top of the stack, refreshing it on the way."""
        if self.current is not None:
            self.current.on_hide()

        frame = self.frames[screen]
        self.current = frame
        frame.on_show()
        frame.tkraise()

    def start_race(self):
        """Begin a fresh race at the chosen difficulty and show the road."""
        self.race = Race(self.difficulty, self.settings.questions_per_race)
        self.show_frame(RacePage)

    def play_beep(self):
        """Beep, unless sound is switched off or the computer is not running Windows."""
        if self.settings.sound_on and SOUND_AVAILABLE:
            winsound.Beep(BEEP_HERTZ, BEEP_MILLISECONDS)

    def show_error(self, title, message):
        """Report something the user got wrong, with a beep to draw their attention."""
        self.play_beep()
        messagebox.showerror(title, message, parent=self)

    def show_info(self, title, message):
        """Report something that worked.

        Kept separate from ``show_error`` so the two kinds of message can never
        be confused for one another.
        """
        messagebox.showinfo(title, message, parent=self)


class Page(tk.Frame):
    """Base class for every screen, holding the parts they all share.

    Each screen is a frame with one canvas filling it. Subclasses draw their
    fixed parts in ``build``, refresh anything that changes in ``on_show``, and
    tidy up after themselves in ``on_hide``.
    """

    background = BACKGROUND

    def __init__(self, parent, controller):
        super().__init__(parent, bg=self.background)
        self.controller = controller
        self.canvas = tk.Canvas(self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
                                bg=self.background, highlightthickness=0)
        self.canvas.pack(pady=CANVAS_PAD)
        self.build()

    def build(self):
        """Draw the parts of the screen that never change."""

    def on_show(self):
        """Refresh the screen just before it is raised."""

    def on_hide(self):
        """Tidy up just before a different screen is raised."""

    def draw_heading(self, text, y, font=HEADING_FONT):
        """Draw a heading with its drop shadow, and return the item in front.

        The shadow is drawn first, three across and four down, so the heading
        lifts off the dark background instead of sinking into it.
        """
        self.canvas.create_text(328, y + 4, text=text, font=font, fill=SHADOW)
        return self.canvas.create_text(325, y, text=text, font=font, fill=ACCENT)

    def draw_back_button(self, x, y, command, text=" Back"):
        """Place a back button, using the arrow picture next to the wording."""
        back_btn = ttk.Button(self, text=text, image=self.controller.back_img,
                              compound=tk.LEFT, command=command, cursor="hand2")
        return self.canvas.create_window(x, y, anchor=tk.CENTER, window=back_btn)

    def to_menu(self):
        """Leave this screen and go back to the main menu."""
        self.controller.show_frame(MenuPage)


class LoginPage(Page):
    """The sign in screen, which doubles as the create account screen.

    The same three boxes serve both jobs. In sign in mode the confirm box and
    the password rules are hidden, and the two buttons change their wording and
    what they do, so there is only one form to keep working.
    """

    def build(self):
        """Draw the form, which is shared by both modes."""
        # Default to sign in, since returning users outnumber new ones.
        self.mode = "Sign In"

        self.title_txt = self.draw_heading("SIGN IN", 70)

        # A card behind the form so the boxes do not float on the background.
        self.canvas.create_rectangle(78, 152, 572, 404, fill=PANEL, outline=PANEL_EDGE, width=2)

        # The username row.
        self.canvas.create_text(288, 200, text="Username", font=LABEL_FONT,
                                fill=TEXT_DIM, anchor=tk.E)
        self.username_entry = ttk.Entry(self, width=20, font=ENTRY_FONT, style="Dark.TEntry")
        self.canvas.create_window(308, 200, anchor=tk.W, window=self.username_entry)

        # The password row, which hides the letters as they are typed.
        self.canvas.create_text(288, 260, text="Password", font=LABEL_FONT,
                                fill=TEXT_DIM, anchor=tk.E)
        self.password_entry = ttk.Entry(self, width=20, show="*", font=ENTRY_FONT,
                                        style="Dark.TEntry")
        self.canvas.create_window(308, 260, anchor=tk.W, window=self.password_entry)

        # The confirm row, which is only needed when making an account.
        self.confirm_txt = self.canvas.create_text(288, 320, text="Confirm Password",
                                                   font=LABEL_FONT, fill=TEXT_DIM, anchor=tk.E)
        self.confirm_entry = ttk.Entry(self, width=20, show="*", font=ENTRY_FONT,
                                       style="Dark.TEntry")
        self.confirm_win = self.canvas.create_window(308, 320, anchor=tk.W,
                                                     window=self.confirm_entry)

        # The password rules, shown only while an account is being created.
        self.rules_txt = self.canvas.create_text(325, 380, text=PASSWORD_RULES,
                                                 font=SMALL_FONT, fill=TEXT_DIM, width=420)

        # The main button, whose job changes depending on the mode.
        self.action_btn = ttk.Button(self, text="Sign In", width=20, command=self.sign_in,
                                     style="Accent.TButton", cursor="hand2")
        self.canvas.create_window(325, 450, anchor=tk.CENTER, window=self.action_btn)

        # The quiet button that swaps between the two modes.
        self.switch_btn = ttk.Button(self, text="Create an account instead", width=28,
                                     command=self.switch_mode, style="Link.TButton",
                                     cursor="hand2")
        self.canvas.create_window(325, 520, anchor=tk.CENTER, window=self.switch_btn)

        self.update_form()

    def on_show(self):
        """Put the cursor in the username box, ready to type."""
        self.username_entry.focus_set()

    def update_form(self):
        """Redraw the form for the current mode, hiding what sign in does not use."""
        if self.mode == "Sign In":
            self.canvas.itemconfig(self.title_txt, text="SIGN IN")
            self.canvas.itemconfig(self.confirm_txt, state=tk.HIDDEN)
            self.canvas.itemconfig(self.confirm_win, state=tk.HIDDEN)
            self.canvas.itemconfig(self.rules_txt, state=tk.HIDDEN)
            self.action_btn.config(text="Sign In", command=self.sign_in)
            self.switch_btn.config(text="Create an account instead")
        else:
            self.canvas.itemconfig(self.title_txt, text="CREATE ACCOUNT")
            self.canvas.itemconfig(self.confirm_txt, state=tk.NORMAL)
            self.canvas.itemconfig(self.confirm_win, state=tk.NORMAL)
            self.canvas.itemconfig(self.rules_txt, state=tk.NORMAL)
            self.action_btn.config(text="Create Account", command=self.create_account)
            self.switch_btn.config(text="Sign in instead")

        # Empty the boxes so nothing is left over from the other mode.
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.confirm_entry.delete(0, tk.END)

    def switch_mode(self):
        """Swap the screen between signing in and making a new account."""
        if self.mode == "Sign In":
            self.mode = "Create Account"
        else:
            self.mode = "Sign In"

        self.update_form()

    def open_menu(self, username):
        """Remember who signed in and hand over to the main menu."""
        self.controller.username = username
        self.controller.show_frame(MenuPage)

    def create_account(self):
        """Check every rule, then save a new account and sign the user straight in."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        # Reject a bad username before touching the accounts file.
        problem = Validator.check_username(username)
        if problem != "":
            self.controller.show_error("Cannot Create Account", problem)
            return

        # Stop the user taking a username that somebody else already has.
        if self.controller.accounts.exists(username):
            self.controller.show_error("Cannot Create Account", "The username " + username
                                       + " is already taken. Please choose a different username.")
            return

        # Apply the length, number and capital letter rules.
        problem = Validator.check_password(password)
        if problem != "":
            self.controller.show_error("Cannot Create Account", problem)
            return

        # Make sure the two password boxes were typed the same.
        if confirm != password:
            self.controller.show_error("Cannot Create Account", "Your two passwords do not "
                                       "match. Please type exactly the same password into "
                                       "both boxes.")
            return

        self.controller.accounts.add(username, password)
        self.controller.show_info("Account Created", "Welcome " + username + ". Your account "
                                  "has been saved, so next time you can just sign in.")
        self.open_menu(username)

    def sign_in(self):
        """Check the typed details against the accounts file and sign the user in."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "":
            self.controller.show_error("Cannot Sign In", "You have not typed a username. "
                                       "Please type the username you signed up with.")
            return

        if password == "":
            self.controller.show_error("Cannot Sign In", "You have not typed a password. "
                                       "Please type the password you signed up with.")
            return

        # Read from disk each time, so an account made this session is found.
        if not self.controller.accounts.exists(username):
            self.controller.show_error("Cannot Sign In", "There is no account saved with the "
                                       "username " + username + ". Please check your spelling, "
                                       "or use Create an account instead to make a new one.")
            return

        if not self.controller.accounts.check(username, password):
            self.controller.show_error("Cannot Sign In", "That password does not match the one "
                                       "saved for " + username + ". Please try typing it again.")
            return

        self.controller.show_info("Signed In", "Welcome back " + username + ".")
        self.open_menu(username)


class MenuPage(Page):
    """The main menu, and the screen every other screen goes back to."""

    def build(self):
        """Draw the title and the five buttons."""
        self.draw_heading("MATH RACER", 54, font=TITLE_FONT)
        self.canvas.create_line(140, 108, 510, 108, fill=PANEL_EDGE, width=3)

        self.user_txt = self.canvas.create_text(325, 620, text="", font=SMALL_FONT, fill=TEXT_DIM)

        play_btn = ttk.Button(self, text="PLAY", command=self.controller.start_race,
                              style="Play.TButton", cursor="hand2")
        self.canvas.create_window(350, 350, anchor=tk.CENTER, window=play_btn)

        settings_btn = ttk.Button(self, text="Setting",
                                  command=lambda: self.controller.show_frame(SettingsPage),
                                  style="Menu.TButton", cursor="hand2")
        self.canvas.create_window(200, 225, anchor=tk.CENTER, window=settings_btn)

        leaderboard_btn = ttk.Button(self, text="Leaderboard",
                                     command=lambda: self.controller.show_frame(LeaderboardPage),
                                     style="Menu.TButton", cursor="hand2")
        self.canvas.create_window(500, 225, anchor=tk.CENTER, window=leaderboard_btn)

        difficulty_btn = ttk.Button(self, text="Difficulty",
                                    command=lambda: self.controller.show_frame(DifficultyPage),
                                    style="Menu.TButton", cursor="hand2")
        self.canvas.create_window(200, 525, anchor=tk.CENTER, window=difficulty_btn)

        quit_btn = ttk.Button(self, text="Quit", command=self.controller.destroy,
                              style="Menu.TButton", cursor="hand2")
        self.canvas.create_window(500, 525, anchor=tk.CENTER, window=quit_btn)

    def on_show(self):
        """Name whoever is signed in along the bottom of the menu."""
        self.canvas.itemconfig(self.user_txt, text="Signed in as " + self.controller.username)


class DifficultyPage(Page):
    """The difficulty screen, drawn as the speedometer of the bike.

    The dial is a half circle split into three coloured bands. Picking a level
    sweeps the needle round to that band a few degrees at a time using
    ``after``, which is the animation loop tkinter tutorials teach in place of
    a frame by frame game loop.
    """

    def build(self):
        """Draw the dial, its bands and their wording, and the buttons."""
        self.draw_heading("DIFFICULTY", 55)

        # The square the gauge is drawn inside, worked out from its centre and radius.
        gauge_box = (GAUGE_X - GAUGE_RADIUS, GAUGE_Y - GAUGE_RADIUS,
                     GAUGE_X + GAUGE_RADIUS, GAUGE_Y + GAUGE_RADIUS)

        # A coloured band for each difficulty, each one a third of the dial.
        self.canvas.create_arc(gauge_box, start=120, extent=60, style=tk.ARC,
                               width=GAUGE_BAND, outline=ZONE_COLOURS["Easy"])
        self.canvas.create_arc(gauge_box, start=60, extent=60, style=tk.ARC,
                               width=GAUGE_BAND, outline=ZONE_COLOURS["Medium"])
        self.canvas.create_arc(gauge_box, start=0, extent=60, style=tk.ARC,
                               width=GAUGE_BAND, outline=ZONE_COLOURS["Hard"])

        # Name every band and print its real speed underneath, so the dial shows
        # the same numbers the game actually uses rather than made up ones.
        for level in LABEL_SPOTS:
            spot_x, spot_y, spot_anchor = LABEL_SPOTS[level]
            self.canvas.create_text(spot_x, spot_y, text=level.upper(), font=BAND_FONT,
                                    fill=ZONE_COLOURS[level], anchor=spot_anchor)
            self.canvas.create_text(spot_x, spot_y + 24, text="Speed " + str(SPEEDS[level]),
                                    font=SMALL_FONT, fill=TEXT_DIM, anchor=spot_anchor)

        # The needle starts straight up. show_needle swings it round below.
        self.needle = self.canvas.create_line(GAUGE_X, GAUGE_Y, GAUGE_X,
                                              GAUGE_Y - NEEDLE_LENGTH, width=6, fill=TEXT,
                                              arrow=tk.LAST, arrowshape=(18, 22, 7))
        self.canvas.create_oval(GAUGE_X - 15, GAUGE_Y - 15, GAUGE_X + 15, GAUGE_Y + 15,
                                fill=PANEL, outline=TEXT, width=3)

        # The wording under the dial that spells out what the needle points at.
        self.chosen_txt = self.canvas.create_text(325, 452, text="", font=SUBHEADING_FONT,
                                                  fill=TEXT)

        # The three difficulty buttons, sitting under the band each one selects.
        easy_btn = ttk.Button(self, text="Easy", command=lambda: self.pick("Easy"),
                              style="Easy.TButton", cursor="hand2")
        self.canvas.create_window(120, 520, anchor=tk.CENTER, window=easy_btn)

        medium_btn = ttk.Button(self, text="Medium", command=lambda: self.pick("Medium"),
                                style="Medium.TButton", cursor="hand2")
        self.canvas.create_window(325, 520, anchor=tk.CENTER, window=medium_btn)

        hard_btn = ttk.Button(self, text="Hard", command=lambda: self.pick("Hard"),
                              style="Hard.TButton", cursor="hand2")
        self.canvas.create_window(530, 520, anchor=tk.CENTER, window=hard_btn)

        self.draw_back_button(110, 600, self.to_menu)

        # Holds the booked sweep so it can be called off when the screen is left.
        self.sweep_job = None

    def on_show(self):
        """Sweep the needle round to the saved difficulty as the screen opens."""
        self.show_needle()

    def on_hide(self):
        """Call off any sweep still running, so it cannot fire after leaving."""
        if self.sweep_job is not None:
            self.after_cancel(self.sweep_job)
            self.sweep_job = None

    @staticmethod
    def needle_point(radius, degrees):
        """Return where a needle of this length, pointing at this angle, ends up."""
        radians = math.radians(degrees)
        return GAUGE_X + radius * math.cos(radians), GAUGE_Y - radius * math.sin(radians)

    def place_needle(self, degrees):
        """Put the needle at an exact angle."""
        point_x, point_y = self.needle_point(NEEDLE_LENGTH, degrees)
        self.canvas.coords(self.needle, GAUGE_X, GAUGE_Y, point_x, point_y)

    def needle_now(self):
        """Read back the angle the needle is pointing at from where it is drawn.

        This only works because the dial is a half circle, so the angle stays
        between 0 and 180 and never wraps past the point where atan2 flips sign.
        """
        start_x, start_y, tip_x, tip_y = self.canvas.coords(self.needle)
        return math.degrees(math.atan2(start_y - tip_y, tip_x - start_x))

    def sweep_needle(self, target):
        """Turn the needle one step towards the target, then book the next step."""
        self.sweep_job = None

        # Give up if a different difficulty was picked while this sweep ran, so
        # two sweeps can never fight over the same needle.
        if target != NEEDLE_ANGLES[self.controller.difficulty]:
            return

        angle = self.needle_now()
        gap = target - angle

        # Land exactly on the target once the last step would overshoot it.
        if abs(gap) <= NEEDLE_STEP:
            self.place_needle(target)
            return

        if gap > 0:
            self.place_needle(angle + NEEDLE_STEP)
        else:
            self.place_needle(angle - NEEDLE_STEP)

        self.sweep_job = self.after(NEEDLE_DELAY, self.sweep_needle, target)

    def show_needle(self):
        """Update the wording and start the needle sweeping to the new difficulty."""
        level = self.controller.difficulty
        self.canvas.itemconfig(self.chosen_txt,
                               text=level.upper() + "  -  SPEED " + str(SPEEDS[level]))
        self.sweep_needle(NEEDLE_ANGLES[level])

    def pick(self, level):
        """Remember the difficulty this button stands for and swing the needle to it."""
        self.controller.difficulty = level
        self.show_needle()


class SettingsPage(Page):
    """The settings screen, holding the sound switch and the race length."""

    def build(self):
        """Draw the card, the two settings, and the save and back buttons."""
        self.draw_heading("SETTINGS", 60)

        # A card behind the two settings so they read as one group.
        self.canvas.create_rectangle(88, 160, 562, 388, fill=PANEL, outline=PANEL_EDGE, width=2)

        # The sound row, ticked when sound is currently switched on.
        self.canvas.create_text(280, 210, text="Sound", font=LABEL_FONT,
                                fill=TEXT_DIM, anchor=tk.E)
        self.sound_value = tk.IntVar(self)
        sound_check = ttk.Checkbutton(self, text="On", variable=self.sound_value,
                                      style="Panel.TCheckbutton", cursor="hand2")
        self.canvas.create_window(300, 210, anchor=tk.W, window=sound_check)

        # The questions per race box, the one setting that is typed in.
        self.canvas.create_text(280, 300, text="Questions per race", font=LABEL_FONT,
                                fill=TEXT_DIM, anchor=tk.E)
        self.questions_entry = ttk.Entry(self, width=6, font=ENTRY_FONT, style="Dark.TEntry")
        self.canvas.create_window(300, 300, anchor=tk.W, window=self.questions_entry)

        # The small text explaining what the box will accept.
        self.canvas.create_text(325, 350, text="Choose a whole number between "
                                + str(QUESTIONS_MIN) + " and " + str(QUESTIONS_MAX) + ".",
                                font=SMALL_FONT, fill=TEXT_DIM)

        save_btn = ttk.Button(self, text="Save", width=14, command=self.save,
                              style="Accent.TButton", cursor="hand2")
        self.canvas.create_window(450, 470, anchor=tk.CENTER, window=save_btn)

        self.draw_back_button(150, 470, self.to_menu)

    def on_show(self):
        """Fill both settings in from the values currently in use.

        Doing this every time the screen opens is what throws away changes that
        were typed but never saved, so backing out really does undo them.
        """
        self.sound_value.set(int(self.controller.settings.sound_on))
        self.questions_entry.delete(0, tk.END)
        self.questions_entry.insert(0, str(self.controller.settings.questions_per_race))

    def save(self):
        """Check the typed box, then save both settings to the settings file."""
        # The typed box is the only setting that can be wrong, so it is checked first.
        typed = self.questions_entry.get()
        problem = Validator.check_questions(typed)
        if problem != "":
            self.controller.show_error("Cannot Save Settings", problem)
            return

        self.controller.settings.sound_on = self.sound_value.get() == 1
        self.controller.settings.questions_per_race = int(typed)
        self.controller.settings.save()

        self.controller.show_info("Settings Saved", "Your settings have been saved and will "
                                  "still be here next time you play.")


class LeaderboardPage(Page):
    """The leaderboard, showing the best drivers at each difficulty.

    The boards are rebuilt every time the screen is opened, because a race
    finished since the last look would otherwise be missing. Everything drawn
    from the records file is tagged so it can be cleared in one call.
    """

    ROWS_TAG = "boards"

    def build(self):
        """Draw the heading, the explanation and the back button."""
        self.draw_heading("LEADERBOARD", 60)

        # Explain the ordering, since equal scores are split by the clock.
        self.canvas.create_text(325, 578, text="Best score first. A tie is settled by the "
                                "quicker time. Only each driver's best run is shown.",
                                font=SMALL_FONT, fill=TEXT_DIM)

        self.draw_back_button(110, 618, self.to_menu)

    def on_show(self):
        """Throw away the old boards and draw them again from the records file."""
        self.canvas.delete(self.ROWS_TAG)

        column = 0
        for level in TOPICS:
            self.draw_board(level, column)
            column = column + 1

    def draw_board(self, level, column):
        """Draw one difficulty's board in the given column across the screen."""
        board_left = BOARD_GAP + column * (BOARD_WIDTH + BOARD_GAP)
        board_right = board_left + BOARD_WIDTH
        middle = (board_left + board_right) / 2

        # The card the board sits on, headed in that difficulty's colour.
        self.canvas.create_rectangle(board_left, BOARD_TOP, board_right, BOARD_BOTTOM,
                                     fill=PANEL, outline=PANEL_EDGE, width=2,
                                     tags=self.ROWS_TAG)
        self.canvas.create_text(middle, BOARD_TOP + 34, text=level.upper(), font=BAND_FONT,
                                fill=ZONE_COLOURS[level], tags=self.ROWS_TAG)

        # The column headings, which sit above a dividing line.
        self.canvas.create_text(board_left + NAME_OFFSET, BOARD_TOP + 68, text="DRIVER",
                                font=SMALL_FONT, fill=TEXT_DIM, anchor=tk.W, tags=self.ROWS_TAG)
        self.canvas.create_text(board_left + SCORE_OFFSET, BOARD_TOP + 68, text="PTS",
                                font=SMALL_FONT, fill=TEXT_DIM, anchor=tk.E, tags=self.ROWS_TAG)
        self.canvas.create_text(board_left + TIME_OFFSET, BOARD_TOP + 68, text="TIME",
                                font=SMALL_FONT, fill=TEXT_DIM, anchor=tk.E, tags=self.ROWS_TAG)
        self.canvas.create_line(board_left + 10, BOARD_TOP + 82, board_right - 10,
                                BOARD_TOP + 82, fill=PANEL_EDGE, width=2, tags=self.ROWS_TAG)

        rows = self.controller.records.best(level, LEADERBOARD_ROWS)

        # An empty board says so rather than leaving a blank card.
        if len(rows) == 0:
            self.canvas.create_text(middle, ROW_TOP + 60, text="No races yet", font=SMALL_FONT,
                                    fill=TEXT_DIM, tags=self.ROWS_TAG)
            return

        place = 0
        for level_name, driver, score, seconds in rows:
            row_y = ROW_TOP + place * ROW_HEIGHT

            # The driver who is signed in is picked out in the accent colour.
            if driver == self.controller.username:
                row_colour = ACCENT
            else:
                row_colour = TEXT

            self.canvas.create_text(board_left + NAME_OFFSET, row_y,
                                    text=str(place + 1) + "  " + driver, font=SMALL_FONT,
                                    fill=row_colour, anchor=tk.W, tags=self.ROWS_TAG)
            self.canvas.create_text(board_left + SCORE_OFFSET, row_y, text=str(score),
                                    font=SMALL_FONT, fill=row_colour, anchor=tk.E,
                                    tags=self.ROWS_TAG)
            self.canvas.create_text(board_left + TIME_OFFSET, row_y, text=format_time(seconds),
                                    font=SMALL_FONT, fill=row_colour, anchor=tk.E,
                                    tags=self.ROWS_TAG)
            place = place + 1


class RacePage(Page):
    """The race itself, drawn as a road with an answer gate in every lane.

    The player steers the bike into a lane and sets off. The gates then run
    down the road towards the bike a frame at a time, booked one after another
    with ``after``, which is how tkinter animates without a real game loop. A
    ``running`` flag guards every booked step so nothing can fire once the
    screen has been left.
    """

    background = ROAD_COLOUR

    def build(self):
        """Draw the road, the header and footer bars, the gates and the bike."""
        # The solid lines down either kerb of the road.
        self.canvas.create_line(ROAD_EDGE, ROAD_TOP, ROAD_EDGE, ROAD_BOTTOM,
                                fill=EDGE_COLOUR, width=6)
        self.canvas.create_line(CANVAS_WIDTH - ROAD_EDGE, ROAD_TOP, CANVAS_WIDTH - ROAD_EDGE,
                                ROAD_BOTTOM, fill=EDGE_COLOUR, width=6)

        # The dashed lines dividing the three lanes. They are kept in a list so
        # their dashes can be scrolled to make the road look like it is moving.
        self.lane_lines = []
        for divider in range(1, LANE_COUNT):
            line_x = (LANE_X[divider - 1] + LANE_X[divider]) / 2
            self.lane_lines.append(self.canvas.create_line(line_x, ROAD_TOP, line_x,
                                                           ROAD_BOTTOM,
                                                           fill=LANE_LINE_COLOUR, width=4,
                                                           dash=LANE_DASH))

        # The bar across the top holding the question and the score.
        self.canvas.create_rectangle(0, 0, CANVAS_WIDTH, HEADER_BOTTOM, fill=BACKGROUND,
                                     outline="")
        self.question_txt = self.canvas.create_text(325, QUESTION_Y, text="",
                                                    font=QUESTION_FONT, fill=TEXT, width=600,
                                                    justify=tk.CENTER)
        self.scoreboard_txt = self.canvas.create_text(325, SCOREBOARD_Y, text="",
                                                      font=SCORE_FONT, fill=ACCENT)
        self.canvas.create_text(325, INSTRUCTION_Y, text=DRIVING_HELP, font=SMALL_FONT,
                                fill=TEXT_DIM)

        # The bar that fills up as the race is worked through.
        self.canvas.create_rectangle(PROGRESS_LEFT, PROGRESS_TOP, PROGRESS_RIGHT,
                                     PROGRESS_BOTTOM, fill=PANEL_EDGE, outline="")
        self.progress_bar = self.canvas.create_rectangle(PROGRESS_LEFT, PROGRESS_TOP,
                                                         PROGRESS_LEFT, PROGRESS_BOTTOM,
                                                         fill=ACCENT, outline="")

        # The matching bar along the bottom for the back button and the result.
        self.canvas.create_rectangle(0, ROAD_BOTTOM, CANVAS_WIDTH, CANVAS_HEIGHT,
                                     fill=BACKGROUND, outline="")
        self.feedback_txt = self.canvas.create_text(400, BOTTOM_ROW_Y, text="",
                                                    font=SCORE_FONT, fill=TEXT)

        # The three answer gates, which are moved into place per question.
        self.gates = []
        self.gate_texts = []
        for lane in range(LANE_COUNT):
            self.gates.append(self.canvas.create_rectangle(0, 0, 0, 0, fill=GATE_COLOUR,
                                                           outline=LANE_LINE_COLOUR, width=3))
            self.gate_texts.append(self.canvas.create_text(0, 0, text="", font=GATE_FONT,
                                                           fill=TEXT))

        # The bike, which stays on its own row and only ever changes lane.
        self.bike_item = self.canvas.create_image(LANE_X[1], BIKE_Y, anchor=tk.CENTER,
                                                  image=self.controller.bike_img)

        # Lift the numbers above the bike, so the answer it lands on is still
        # readable once the bike has pulled up to it.
        for lane in range(LANE_COUNT):
            self.canvas.tag_raise(self.gate_texts[lane])

        self.draw_back_button(85, BOTTOM_ROW_Y, self.to_menu)

        # Set up before the first race so every guard has something to read.
        self.game = None
        self.running = False
        self.drive_step = 0
        self.drive_job = None
        self.pause_job = None
        self.bindings = []

    def on_show(self):
        """Take up the race the menu just built and put the first question on the road."""
        self.game = self.controller.race
        self.running = True
        self.drive_step = SPEEDS[self.game.difficulty] // DRIVE_DIVISOR

        # Start every race from the middle lane, whatever the last one ended on.
        self.canvas.coords(self.bike_item, LANE_X[1], BIKE_Y)
        self.canvas.itemconfig(self.feedback_txt, text="")

        self.bind_keys()
        self.show_question()

    def on_hide(self):
        """Stop the race dead, so no booked frame can fire after the screen is left."""
        self.running = False

        for job in (self.drive_job, self.pause_job):
            if job is not None:
                self.after_cancel(job)

        self.drive_job = None
        self.pause_job = None
        self.unbind_keys()

    def bind_keys(self):
        """Listen for the driving keys while this screen is the one on top.

        The keys are bound to the window rather than to this frame, because a
        frame does not take the keyboard focus by itself. They are unbound
        again in ``on_hide`` so they cannot drive a race that is not showing.
        """
        window = self.winfo_toplevel()
        self.bindings = [("<Left>", window.bind("<Left>", self.go_left)),
                         ("<Right>", window.bind("<Right>", self.go_right)),
                         ("<space>", window.bind("<space>", self.submit)),
                         ("<Return>", window.bind("<Return>", self.submit))]
        window.focus_set()

    def unbind_keys(self):
        """Stop listening for the driving keys."""
        window = self.winfo_toplevel()

        for sequence, binding in self.bindings:
            window.unbind(sequence, binding)

        self.bindings = []

    def bike_lane(self):
        """Return which lane the bike is in, worked out from where it is drawn.

        Reading it back off the canvas means there is no extra variable to keep
        in step with the picture on screen.
        """
        bike_x = self.canvas.coords(self.bike_item)[0]

        for lane in range(LANE_COUNT):
            if abs(LANE_X[lane] - bike_x) < 5:
                return lane

        return 1

    def gates_are_moving(self):
        """Return True while the gates are on their way down, so a run is under way."""
        return self.canvas.coords(self.gate_texts[0])[1] > GATE_Y

    def place_gates(self, row):
        """Line all three gates up across the road at the given height."""
        for lane in range(LANE_COUNT):
            self.canvas.coords(self.gate_texts[lane], LANE_X[lane], row)
            self.canvas.coords(self.gates[lane],
                               LANE_X[lane] - GATE_WIDTH / 2, row - GATE_HEIGHT / 2,
                               LANE_X[lane] + GATE_WIDTH / 2, row + GATE_HEIGHT / 2)

    def highlight_lane(self):
        """Outline the gate the bike is lined up with, so the choice is obvious."""
        for lane in range(LANE_COUNT):
            if lane == self.bike_lane():
                self.canvas.itemconfig(self.gates[lane], outline=ACCENT, width=5)
            else:
                self.canvas.itemconfig(self.gates[lane], outline=LANE_LINE_COLOUR, width=3)

    def steer(self, lane):
        """Slide the bike one lane sideways, ignoring the edges of the road."""
        # Lanes can only be changed before the gates are set moving.
        if self.gates_are_moving():
            return

        if 0 <= lane < LANE_COUNT:
            self.canvas.coords(self.bike_item, LANE_X[lane], BIKE_Y)
            self.highlight_lane()

    def go_left(self, event):
        """Move the bike one lane to the left."""
        self.steer(self.bike_lane() - 1)

    def go_right(self, event):
        """Move the bike one lane to the right."""
        self.steer(self.bike_lane() + 1)

    def show_scoreboard(self):
        """Refresh the score line and the progress bar at the top of the road."""
        self.canvas.itemconfig(self.scoreboard_txt,
                               text=self.game.difficulty.upper() + "    QUESTION "
                               + str(self.game.asked + 1) + " OF " + str(self.game.total)
                               + "    SCORE " + str(self.game.score) + "    "
                               + str(self.game.accuracy()) + "% CORRECT")

        # The bar is filled in proportion to how many have been answered.
        filled = (PROGRESS_LEFT + (PROGRESS_RIGHT - PROGRESS_LEFT)
                  * self.game.asked / self.game.total)
        self.canvas.coords(self.progress_bar, PROGRESS_LEFT, PROGRESS_TOP, filled,
                           PROGRESS_BOTTOM)

    def show_question(self):
        """Put a new question on the road, with a gate waiting in every lane."""
        self.canvas.itemconfig(self.question_txt, text=self.game.question.wording)
        choices = self.game.question.choices()

        for lane in range(LANE_COUNT):
            self.canvas.itemconfig(self.gate_texts[lane], text=choices[lane], fill=TEXT)
            self.canvas.itemconfig(self.gates[lane], fill=GATE_COLOUR)

        self.place_gates(GATE_Y)
        self.highlight_lane()
        self.show_scoreboard()

    def scroll_road(self):
        """Shift the lane markings along so the road appears to stream past."""
        offset = int(float(self.canvas.itemcget(self.lane_lines[0], "dashoffset")))

        for line in self.lane_lines:
            self.canvas.itemconfig(line, dashoffset=(offset + self.drive_step) % DASH_CYCLE)

    def submit(self, event):
        """Set the gates off down the road towards the bike."""
        # Ignore the key while a run is already under way or the race is over.
        if self.gates_are_moving() or self.game.is_finished():
            return

        self.drive_down()

    def drive_down(self):
        """Move the gates one frame down the road towards the waiting bike."""
        self.drive_job = None

        # Give up if the screen was left part way through a run.
        if not self.running:
            return

        row = self.canvas.coords(self.gate_texts[0])[1] + self.drive_step
        self.scroll_road()

        # Keep coming until the gates have pulled up in front of the bike.
        if row < GATE_STOP_Y:
            self.place_gates(row)
            self.drive_job = self.after(FRAME_DELAY, self.drive_down)
            return

        self.place_gates(GATE_STOP_Y)
        self.arrive()

    def arrive(self):
        """Mark whichever gate reached the bike, then line up the next question."""
        chosen_lane = self.bike_lane()
        chosen = self.canvas.itemcget(self.gate_texts[chosen_lane], "text")
        right_answer = self.game.question.answer

        if self.game.mark(chosen):
            self.canvas.itemconfig(self.feedback_txt, text="CORRECT", fill=CORRECT_COLOUR)
        else:
            self.canvas.itemconfig(self.feedback_txt, text="WRONG, it was " + right_answer,
                                   fill=WRONG_COLOUR)
            self.canvas.itemconfig(self.gates[chosen_lane], fill=WRONG_COLOUR)
            self.canvas.itemconfig(self.gate_texts[chosen_lane], fill=BACKGROUND)

        # Colour the right gate green either way, so a wrong answer still shows
        # the player where the correct one was.
        for lane in range(LANE_COUNT):
            if self.canvas.itemcget(self.gate_texts[lane], "text") == right_answer:
                self.canvas.itemconfig(self.gates[lane], fill=CORRECT_COLOUR)
                self.canvas.itemconfig(self.gate_texts[lane], fill=BACKGROUND)

        self.show_scoreboard()

        # Either way the message stays up for a moment before moving on, so the
        # last answer of a race is not swallowed by the results screen.
        if self.game.is_finished():
            self.pause_job = self.after(FEEDBACK_PAUSE, self.finish_race)
        else:
            self.pause_job = self.after(FEEDBACK_PAUSE, self.start_next)

    def start_next(self):
        """Send the gates back to the top ready for the next question."""
        self.pause_job = None

        # Give up if the screen was left while the message was showing.
        if not self.running:
            return

        self.game.next_question()
        self.show_question()
        self.canvas.itemconfig(self.feedback_txt, text="")

    def finish_race(self):
        """Save the finished run and hand it on to the results screen."""
        self.pause_job = None

        # Give up if the screen was left while the last message was showing.
        if not self.running:
            return

        self.controller.records.add(self.game.difficulty, self.controller.username,
                                    self.game.score, self.game.seconds())
        self.controller.show_frame(ResultsPage)


class ResultsPage(Page):
    """The results screen, shown once a race has been completed.

    Everything on the card is drawn again each time the screen opens, because
    every figure on it belongs to the race that has just finished.
    """

    STATS_TAG = "results"

    # The headings across the middle of the card, and where the first one sits.
    STATS_LEFT = 133
    STATS_GAP = 128

    def build(self):
        """Draw the heading, the card behind the figures, and the two buttons."""
        self.draw_heading("RACE COMPLETE", 70)

        # A card holding everything the driver earned.
        self.canvas.create_rectangle(70, 140, 580, 470, fill=PANEL, outline=PANEL_EDGE, width=2)
        self.canvas.create_text(325, 180, text="FINAL SCORE", font=SMALL_FONT, fill=TEXT_DIM)

        # The bar the accuracy is drawn against, which never changes size.
        self.canvas.create_rectangle(120, 388, 530, 400, fill=PANEL_EDGE, outline="")

        again_btn = ttk.Button(self, text="Race Again", width=16,
                               command=self.controller.start_race, style="Accent.TButton",
                               cursor="hand2")
        self.canvas.create_window(215, 540, anchor=tk.CENTER, window=again_btn)

        self.draw_back_button(440, 540, self.to_menu, text=" Main Menu")

    def on_show(self):
        """Draw every figure again from the race that has just finished."""
        self.canvas.delete(self.STATS_TAG)
        finished = self.controller.race

        # The score itself, given the most room because it is the headline.
        self.canvas.create_text(325, 235, text=str(finished.score), font=SCORE_BIG_FONT,
                                fill=ACCENT, tags=self.STATS_TAG)

        # Four figures underneath, each with its heading above the number.
        stats = [("DIFFICULTY", finished.difficulty),
                 ("CORRECT", str(finished.correct) + " of " + str(finished.total)),
                 ("ACCURACY", str(finished.accuracy()) + "%"),
                 ("TIME", format_time(finished.seconds()))]

        column = 0
        for heading, value in stats:
            spot_x = self.STATS_LEFT + column * self.STATS_GAP
            self.canvas.create_text(spot_x, 312, text=heading, font=SMALL_FONT, fill=TEXT_DIM,
                                    tags=self.STATS_TAG)
            self.canvas.create_text(spot_x, 340, text=value, font=STAT_FONT, fill=TEXT,
                                    tags=self.STATS_TAG)
            column = column + 1

        # A bar showing the accuracy, so the number has something to sit against.
        bar_fill = 120 + (530 - 120) * finished.accuracy() / 100
        self.canvas.create_rectangle(120, 388, bar_fill, 400, fill=ACCENT, outline="",
                                     tags=self.STATS_TAG)

        # A line of encouragement chosen from how the race actually went.
        self.canvas.create_text(325, 435, text=result_message(finished.accuracy()),
                                font=LABEL_FONT, fill=TEXT, width=460, tags=self.STATS_TAG)


def main():
    """Build the window and hand control over to tkinter."""
    app = MathRacerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
