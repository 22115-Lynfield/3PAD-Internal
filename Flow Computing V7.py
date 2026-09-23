from tkinter import *
from tkinter import messagebox
import tkinter as tk
import random
import hashlib
import secrets
import math
from PIL import Image, ImageTk

# winsound only exists on Windows, so the beep is skipped on any other system.
try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False



# The two typefaces the game uses, named once so they can be swapped easily.
TITLE_TYPEFACE = "Impact"
BODY_TYPEFACE = "Segoe UI"

# Every size of text in the game, so nothing is sized by a loose number.
TITLE_FONT = (TITLE_TYPEFACE, 58)
HEADING_FONT = (TITLE_TYPEFACE, 38)
BAND_FONT = (TITLE_TYPEFACE, 24)
SUBHEADING_FONT = (BODY_TYPEFACE, 15, "bold")
QUESTION_FONT = (BODY_TYPEFACE, 15, "bold")
GATE_FONT = (BODY_TYPEFACE, 21, "bold")
SCORE_FONT = (BODY_TYPEFACE, 10, "bold")
LABEL_FONT = (BODY_TYPEFACE, 12, "bold")
ENTRY_FONT = (BODY_TYPEFACE, 13)
BUTTON_FONT = (BODY_TYPEFACE, 11, "bold")
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


# Set up the main window and resize it.
root = tk.Tk()
root.title("Math Racer")
root.geometry("700x700")


# Set up the canvas widget.
canvas = Canvas(root, width = 650, height = 650, bg = BACKGROUND, highlightthickness = 0)
canvas.pack(pady = 5)
main_shadow = canvas.create_text(328, 58, text="MATH RACER", font=TITLE_FONT, fill=SHADOW)
main_txt = canvas.create_text(325, 54, text="MATH RACER", font=TITLE_FONT, fill=ACCENT)
menu_rule = canvas.create_line(140, 108, 510, 108, fill=PANEL_EDGE, width=3)
user_txt = canvas.create_text(325, 620, text="", font=SMALL_FONT, fill=TEXT_DIM)

# Open and resize bike image.
bike = Image.open(("Bike.png"))
resize_bike = bike.resize((100, 100))
bike_img = ImageTk.PhotoImage(resize_bike)

# Open and resize back arrow image.
back = Image.open(("Back.png"))
resize_back = back.resize((25, 25))
back_img = ImageTk.PhotoImage(resize_back)

# The speed shown on the dial for each difficulty, which is also how fast the
# answers drive towards the bike once it is divided by FALL_DIVISOR.
SPEEDS = {"Easy": 20, "Medium": 30, "Hard": 40}

# The speedometer that the difficulty window is drawn as.
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
LABEL_SPOTS = {"Easy": (132, 282, E), "Medium": (325, 166, S), "Hard": (518, 282, W)}

# How far the needle turns each frame, and how long it waits between frames.
NEEDLE_STEP = 4
NEEDLE_DELAY = 12

# Work out where a needle of this length, pointing at this angle, ends up.
def needle_point(radius, degrees):
    radians = math.radians(degrees)
    return GAUGE_X + radius * math.cos(radians), GAUGE_Y - radius * math.sin(radians)

# Remembers the difficulty the user picked. Easy is the default until they change it.
difficulty_picked = "Easy"

# Accounts are stored here so they survive between runs.
ACCOUNTS_FILE = "accounts.txt"

# The rules a username and a password have to follow.
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 12
PASSWORD_MIN_LENGTH = 5

# Bytes of randomness per salt. token_hex returns two characters per byte.
SALT_LENGTH = 8

# Built from PASSWORD_MIN_LENGTH so the message cannot drift from the check.
PASSWORD_RULES = "Your password must be at least " + str(PASSWORD_MIN_LENGTH) + " characters long, and include at least 1 number and 1 capital letter."

# Remembers who is signed in so the leaderboard can use their name later.
signed_in_user = ""

# Remembers whether the sign in window is signing in or making a new account.
login_mode = "Sign In"

# Preferences are stored here so the user only has to set them once.
SETTINGS_FILE = "settings.txt"

# The number of questions a race can be set to.
QUESTIONS_MIN = 5
QUESTIONS_MAX = 50

# The pitch and length of the beep that plays when an error box appears.
BEEP_HERTZ = 700
BEEP_MILLISECONDS = 150

# The settings themselves, holding the defaults until settings.txt is read.
sound_on = True
questions_per_race = 10

# The topics each difficulty draws from. Easy is plain arithmetic, Medium adds
# powers, fractions, percentages and number theory, and Hard moves on to
# algebra, geometry, statistics and basic calculus, so every level teaches
# something the one below it does not.
TOPICS = {"Easy": ["Addition", "Subtraction", "Multiplication", "Division"],
          "Medium": ["Exponents", "Square Roots", "Fractions", "Percentages",
                     "Prime Numbers", "Highest Common Factor", "Lowest Common Multiple"],
          "Hard": ["Algebra", "Area", "Perimeter", "Volume", "Mean", "Median",
                   "Mode", "Differentiation", "Integration"]}

# Points won for a right answer at each difficulty, so harder is worth more.
POINTS = {"Easy": 10, "Medium": 20, "Hard": 30}

# Points lost for a wrong answer, whatever the difficulty.
WRONG_PENALTY = 5

# The three lanes the bike drives between, and where the middle of each one is.
LANE_COUNT = 3
LANE_X = [108, 325, 542]

# Where everything sits on the race track.
QUESTION_Y = 55
SCOREBOARD_Y = 112
ANSWER_START_Y = 175
BIKE_Y = 545
BOTTOM_ROW_Y = 622

# The size of the answer gates the bike has to drive through.
GATE_WIDTH = 168
GATE_HEIGHT = 54

# How long the screen waits between frames, and how the dial speed becomes
# pixels moved per frame. Dividing keeps the dial numbers looking like a
# speedometer while the answers still fall at a readable pace.
FRAME_DELAY = 40
FALL_DIVISOR = 10

# The race is drawn on a road, a shade lighter than the menus so it reads as
# tarmac rather than as another screen.
ROAD_COLOUR = "#262a35"
LANE_LINE_COLOUR = "#e9ecf3"
GATE_COLOUR = "#12141c"
CORRECT_COLOUR = "#4ade80"
WRONG_COLOUR = "#f87171"

# Beep for errors, unless sound is off or the computer is not running Windows.
def play_beep():
    if sound_on and SOUND_AVAILABLE:
        winsound.Beep(BEEP_HERTZ, BEEP_MILLISECONDS)

# Report something the user got wrong, with a beep to draw their attention.
def show_error(title, message):
    play_beep()
    messagebox.showerror(title, message)

# Report something that worked. Kept separate from show_error so the two
# kinds of message can never be confused for one another.
def show_info(title, message):
    messagebox.showinfo(title, message)

# Return the reason a questions per race entry is rejected, or "" if it passes.
def check_questions(typed):

    if typed == "":
        return "You have not typed how many questions each race should have. Please type a whole number between " + str(QUESTIONS_MIN) + " and " + str(QUESTIONS_MAX) + "."

    # Checking every character rejects decimals, minus signs, spaces and symbols.
    for letter in typed:
        if letter not in "0123456789":
            return "Questions per race must be a whole number, but you typed " + typed + ". Please use digits only, with no spaces, decimal points or symbols, for example 10."

    number = int(typed)

    if number < QUESTIONS_MIN:
        return "A race of " + typed + " questions is too short. Please choose at least " + str(QUESTIONS_MIN) + "."

    if number > QUESTIONS_MAX:
        return "A race of " + typed + " questions is too long. Please choose " + str(QUESTIONS_MAX) + " or fewer."

    return ""

# Read the saved settings, ignoring any value that is missing or damaged.
def load_settings():
    global sound_on, questions_per_race

    try:
        with open(SETTINGS_FILE) as settings_file:
            for line in settings_file:

                # Every line is stored as name=value, for example questions=20.
                parts = line.strip().split("=")
                if len(parts) != 2:
                    continue

                name = parts[0]
                value = parts[1]

                if name == "sound" and value in ("on", "off"):
                    sound_on = value == "on"

                elif name == "questions" and check_questions(value) == "":
                    questions_per_race = int(value)

    # No file exists until the settings are saved for the first time.
    except FileNotFoundError:
        pass

# Write both settings back out, replacing whatever was there before.
def save_settings():
    if sound_on:
        sound_value = "on"
    else:
        sound_value = "off"

    with open(SETTINGS_FILE, "w") as settings_file:
        settings_file.write("sound=" + sound_value + "\n")
        settings_file.write("questions=" + str(questions_per_race) + "\n")

# Scramble a password together with its salt, so the real password is never saved.
def hash_password(password, salt):
    return hashlib.sha256((salt + password).encode()).hexdigest()

# Read every saved account out of the text file into a dictionary.
def load_accounts():
    accounts = {}

    try:
        with open(ACCOUNTS_FILE) as accounts_file:
            for line in accounts_file:

                # Split each line into the username, the salt and the scrambled password.
                parts = line.strip().split(",")

                # Ignore malformed rows rather than letting one bad line break the load.
                if len(parts) == 3 and parts[0] != "" and parts[1] != "" and parts[2] != "":
                    accounts[parts[0]] = (parts[1], parts[2])

    # No file exists until the first account is saved.
    except FileNotFoundError:
        pass

    return accounts

# Add one new account onto the end of the text file.
def save_account(username, salt, scrambled):
    with open(ACCOUNTS_FILE, "a") as accounts_file:
        accounts_file.write(username + "," + salt + "," + scrambled + "\n")

# Return the reason a username is rejected, or an empty string if it passes.
def check_username(username):

    if username == "":
        return "You have not typed a username. Please type one into the username box."

    if len(username) < USERNAME_MIN_LENGTH:
        return "Your username is only " + str(len(username)) + " characters long. Please make it at least " + str(USERNAME_MIN_LENGTH) + " characters."

    if len(username) > USERNAME_MAX_LENGTH:
        return "Your username is " + str(len(username)) + " characters long, which is too long. Please shorten it to " + str(USERNAME_MAX_LENGTH) + " characters or fewer."

    if " " in username:
        return "Your username has a space in it. Please use an underscore instead, for example math_racer."

    if "," in username:
        return "Your username has a comma in it. Commas separate the details inside the accounts file, so please use a different character."

    return ""

# Return the reason a password is rejected, or an empty string if it passes.
def check_password(password):

    if password == "":
        return "You have not typed a password. Please type one into the password box."

    if len(password) < PASSWORD_MIN_LENGTH:
        short_by = PASSWORD_MIN_LENGTH - len(password)
        return "Your password is only " + str(len(password)) + " characters long. Please add " + str(short_by) + " more so it is at least " + str(PASSWORD_MIN_LENGTH) + " characters."

    # One pass over the password, checking for both requirements at once.
    has_number = False
    has_capital = False
    for letter in password:
        if letter.isdigit():
            has_number = True
        if letter.isupper():
            has_capital = True

    if not has_number:
        return "Your password does not contain a number. Please add at least 1 number, for example 4 or 9."

    if not has_capital:
        return "Your password does not contain a capital letter. Please add at least 1 capital letter, for example A or M."

    if "," in password:
        return "Your password has a comma in it. Commas separate the details inside the accounts file, so please use a different character."

    return ""

# Work out the highest common factor of two numbers using Euclid's method,
# which keeps replacing the pair with the smaller number and the remainder.
def highest_common_factor(first, second):
    while second != 0:
        first, second = second, first % second
    return first

# Write a fraction in its simplest form, as a whole number when it divides exactly.
def simplify_fraction(top, bottom):
    divisor = highest_common_factor(top, bottom)
    top = top // divisor
    bottom = bottom // divisor

    if bottom == 1:
        return str(top)

    return str(top) + "/" + str(bottom)

# Test whether a number is prime by trying every factor up to its square root.
# Stopping at the square root is enough, because a factor above it would
# already have been found paired with one below it.
def is_prime(number):
    if number < 2:
        return False

    checker = 2
    while checker * checker <= number:
        if number % checker == 0:
            return False
        checker = checker + 1

    return True


class Question:

    # Hold the wording of one question, the answer it expects, and its topic.
    def __init__(self, wording, answer, topic):
        self.wording = wording
        self.answer = answer
        self.topic = topic

    # Compare a given answer against the right one, ignoring stray spaces.
    def is_correct(self, typed):
        return typed.strip() == self.answer

    # Build two believable wrong answers to sit in the other two lanes.
    def wrong_answers(self):
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

    # Return all three choices in a random order, ready to fill the lanes.
    def choices(self):
        options = self.wrong_answers()
        options.append(self.answer)
        random.shuffle(options)
        return options


class QuestionMaker:

    # Match every topic name to the method that builds that kind of question,
    # so make can look the right one up instead of using a long if else chain.
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

    # Build one random question from the topics that difficulty uses.
    def make(self, difficulty):
        topic = random.choice(TOPICS[difficulty])
        return self.builders[topic]()

    def make_addition(self):
        first = random.randint(2, 50)
        second = random.randint(2, 50)
        return Question("What is " + str(first) + " + " + str(second) + "?", str(first + second), "Addition")

    def make_subtraction(self):
        # The larger number goes first so the answer is never negative.
        first = random.randint(20, 60)
        second = random.randint(2, 19)
        return Question("What is " + str(first) + " - " + str(second) + "?", str(first - second), "Subtraction")

    def make_multiplication(self):
        first = random.randint(2, 12)
        second = random.randint(2, 12)
        return Question("What is " + str(first) + " x " + str(second) + "?", str(first * second), "Multiplication")

    def make_division(self):
        # Building the question from the answer keeps the division exact.
        divisor = random.randint(2, 12)
        answer = random.randint(2, 12)
        return Question("What is " + str(divisor * answer) + " / " + str(divisor) + "?", str(answer), "Division")

    def make_exponents(self):
        power = random.randint(2, 3)

        # Squares can use bigger numbers than cubes and still be worth doing
        # in your head, so the range depends on the power.
        if power == 2:
            base = random.randint(2, 20)
        else:
            base = random.randint(2, 10)

        return Question("What is " + str(base) + " to the power of " + str(power) + "?", str(base ** power), "Exponents")

    def make_square_root(self):
        # Squaring the answer first means the root is always a whole number.
        answer = random.randint(2, 30)
        return Question("What is the square root of " + str(answer * answer) + "?", str(answer), "Square Roots")

    def make_fraction(self):
        bottom = random.choice([4, 6, 8, 10, 12])
        first = random.randint(1, bottom - 2)
        second = random.randint(1, bottom - first - 1)
        wording = "What is " + str(first) + "/" + str(bottom) + " + " + str(second) + "/" + str(bottom) + "? Give your answer as a fraction in its simplest form."
        return Question(wording, simplify_fraction(first + second, bottom), "Fractions")

    def make_percentage(self):
        # The amount is a multiple of 20 and the percentage is a simple one,
        # which together guarantee a whole number answer.
        percent = random.choice([10, 20, 25, 50, 75])
        amount = random.randint(1, 20) * 20
        return Question("What is " + str(percent) + "% of " + str(amount) + "?", str(percent * amount // 100), "Percentages")

    def make_prime(self):
        start = random.randint(5, 150)
        answer = start + 1
        while not is_prime(answer):
            answer = answer + 1
        return Question("What is the next prime number after " + str(start) + "?", str(answer), "Prime Numbers")

    def make_factor(self):
        # Both numbers are built from a shared factor, so the answer is
        # rarely just 1 and the question is actually worth working out.
        shared = random.randint(2, 12)
        first = shared * random.randint(2, 9)
        second = first

        # Asking for the factor of a number and itself looks like a mistake,
        # so keep drawing until the two numbers are actually different.
        while second == first:
            second = shared * random.randint(2, 9)

        return Question("What is the highest common factor of " + str(first) + " and " + str(second) + "?", str(highest_common_factor(first, second)), "Highest Common Factor")

    def make_multiple(self):
        # Two numbers multiplied together, divided by their highest common
        # factor, always gives their lowest common multiple.
        first = random.randint(3, 20)
        second = first

        # Two identical numbers would make the question trivial.
        while second == first:
            second = random.randint(3, 20)

        answer = first * second // highest_common_factor(first, second)
        return Question("What is the lowest common multiple of " + str(first) + " and " + str(second) + "?", str(answer), "Lowest Common Multiple")

    def make_algebra(self):
        # Working backwards from a chosen x keeps the answer a whole number.
        answer = random.randint(2, 12)
        times = random.randint(2, 9)
        plus = random.randint(1, 20)
        wording = "Solve for x:   " + str(times) + "x + " + str(plus) + " = " + str(times * answer + plus)
        return Question(wording, str(answer), "Algebra")

    def make_area(self):
        width = random.randint(3, 15)
        height = random.randint(3, 15)
        wording = "A rectangle is " + str(width) + " cm wide and " + str(height) + " cm tall. What is its area in square cm?"
        return Question(wording, str(width * height), "Area")

    def make_perimeter(self):
        width = random.randint(3, 15)
        height = random.randint(3, 15)
        wording = "A rectangle is " + str(width) + " cm wide and " + str(height) + " cm tall. What is its perimeter in cm?"
        return Question(wording, str(2 * (width + height)), "Perimeter")

    def make_volume(self):
        length = random.randint(2, 12)
        width = random.randint(2, 12)
        height = random.randint(2, 12)
        wording = "A box is " + str(length) + " cm long, " + str(width) + " cm wide and " + str(height) + " cm tall. What is its volume in cubic cm?"
        return Question(wording, str(length * width * height), "Volume")

    def make_mean(self):
        count = random.choice([3, 4, 5])

        # Keep drawing ordinary numbers until they happen to divide exactly.
        # Forcing every number to be a multiple of the count would work too,
        # but it makes the numbers look obviously picked.
        numbers = []
        while len(numbers) == 0 or sum(numbers) % count != 0:
            numbers = []
            for spare in range(count):
                numbers.append(random.randint(2, 30))

        total = sum(numbers)
        wording = "What is the mean of " + ", ".join(str(number) for number in numbers) + "?"
        return Question(wording, str(total // count), "Mean")

    def make_median(self):
        # An odd count means the middle value is a single whole number.
        count = random.choice([3, 5, 7])
        numbers = random.sample(range(1, 60), count)
        middle = sorted(numbers)[count // 2]
        wording = "What is the median of " + ", ".join(str(number) for number in numbers) + "?"
        return Question(wording, str(middle), "Median")

    def make_mode(self):
        # One value is planted three times, and nothing else is allowed to
        # appear more than twice, so exactly one number can be the mode.
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
        # The power rule says the derivative of a x^n is n a x^(n-1). Asking
        # for its value at a point keeps the answer a plain number, so the
        # answer box never has to accept letters.
        coefficient = random.randint(2, 9)
        power = random.randint(2, 4)
        at = random.randint(1, 5)
        gradient = power * coefficient * (at ** (power - 1))
        wording = "y = " + str(coefficient) + "x^" + str(power) + ".   What is dy/dx when x = " + str(at) + "?"
        return Question(wording, str(gradient), "Differentiation")

    def make_integration(self):
        # Integrating a x^n from 0 to b gives a b^(n+1) / (n+1). The
        # coefficient is chosen as a multiple of n+1 so it divides exactly.
        power = random.randint(1, 3)
        coefficient = (power + 1) * random.randint(1, 5)
        upper = random.randint(2, 5)
        area = coefficient * (upper ** (power + 1)) // (power + 1)

        # Nobody writes x^1, so the power is left off when it is one.
        if power == 1:
            equation = str(coefficient) + "x"
        else:
            equation = str(coefficient) + "x^" + str(power)

        wording = "What is the area under y = " + equation + " between x = 0 and x = " + str(upper) + "?"
        return Question(wording, str(area), "Integration")


class Race:

    # Start a race of the given difficulty with a fresh first question.
    def __init__(self, difficulty, total):
        self.difficulty = difficulty
        self.total = total
        self.maker = QuestionMaker()
        self.question = self.maker.make(difficulty)
        self.asked = 0
        self.correct = 0
        self.score = 0

    # Mark the typed answer, move the score, and return True when it was right.
    def mark(self, typed):
        self.asked = self.asked + 1

        if self.question.is_correct(typed):
            self.correct = self.correct + 1
            self.score = self.score + POINTS[self.difficulty]
            return True

        # A wrong answer costs points, but the score never drops below zero.
        self.score = self.score - WRONG_PENALTY
        if self.score < 0:
            self.score = 0

        return False

    # Move on to a new question, unless the race has already finished.
    def next_question(self):
        if not self.is_finished():
            self.question = self.maker.make(self.difficulty)

    # The race is over once every question has been asked.
    def is_finished(self):
        return self.asked >= self.total

    # Work out the percentage answered correctly so far.
    def accuracy(self):
        if self.asked == 0:
            return 0
        return round(100 * self.correct / self.asked)


# Function for the sign in window, which opens before the main menu.
def login():

    # Default to sign in, since returning users outnumber new ones.
    global login_mode
    login_mode = "Sign In"

    login_win = tk.Toplevel(root)
    login_win.title("Sign In")
    login_win.geometry("700x700")

    # Set up the canvas widget for the sign in window.
    login_canvas = Canvas(login_win, width=650, height=650, bg=BACKGROUND, highlightthickness=0)
    login_canvas.pack(pady=5)
    title_shadow = login_canvas.create_text(328, 74, text="SIGN IN", font=HEADING_FONT, fill=SHADOW)
    title_txt = login_canvas.create_text(325, 70, text="SIGN IN", font=HEADING_FONT, fill=ACCENT)

    # A card behind the form so the boxes do not float on the background.
    form_panel = login_canvas.create_rectangle(78, 152, 572, 404, fill=PANEL, outline=PANEL_EDGE, width=2)

    # Set up the username label and entry box.
    username_txt = login_canvas.create_text(288, 200, text="Username", font=LABEL_FONT, fill=TEXT_DIM, anchor=E)
    username_entry = Entry(login_win, font=ENTRY_FONT, width=20, bg=BACKGROUND, fg=TEXT, insertbackground=ACCENT, relief=FLAT, highlightthickness=2, highlightbackground=PANEL_EDGE, highlightcolor=ACCENT)
    username_win = login_canvas.create_window(308, 200, anchor=W, window=username_entry)

    # Set up the password label and entry box, hiding the letters as they are typed.
    password_txt = login_canvas.create_text(288, 260, text="Password", font=LABEL_FONT, fill=TEXT_DIM, anchor=E)
    password_entry = Entry(login_win, font=ENTRY_FONT, width=20, show="*", bg=BACKGROUND, fg=TEXT, insertbackground=ACCENT, relief=FLAT, highlightthickness=2, highlightbackground=PANEL_EDGE, highlightcolor=ACCENT)
    password_win = login_canvas.create_window(308, 260, anchor=W, window=password_entry)

    # Set up the confirm password row, which is only needed when making an account.
    confirm_txt = login_canvas.create_text(288, 320, text="Confirm Password", font=LABEL_FONT, fill=TEXT_DIM, anchor=E)
    confirm_entry = Entry(login_win, font=ENTRY_FONT, width=20, show="*", bg=BACKGROUND, fg=TEXT, insertbackground=ACCENT, relief=FLAT, highlightthickness=2, highlightbackground=PANEL_EDGE, highlightcolor=ACCENT)
    confirm_win = login_canvas.create_window(308, 320, anchor=W, window=confirm_entry)

    # Password rules, shown only while an account is being created.
    rules_txt = login_canvas.create_text(325, 380, text=PASSWORD_RULES, font=SMALL_FONT, fill=TEXT_DIM, width=420)

    # Hand over to the main menu once the account has been accepted.
    def open_menu(username):
        global signed_in_user
        signed_in_user = username
        canvas.itemconfig(user_txt, text="Signed in as " + username)
        login_win.destroy()
        root.deiconify()

    # Function for the create account button.
    def create_account():
        username = username_entry.get()
        password = password_entry.get()
        confirm = confirm_entry.get()

        # Reject a bad username before touching the accounts file.
        problem = check_username(username)
        if problem != "":
            show_error("Cannot Create Account", problem)
            return

        # Stop the user taking a username that somebody else already has.
        accounts = load_accounts()
        if username in accounts:
            show_error("Cannot Create Account", "The username " + username + " is already taken. Please choose a different username.")
            return

        # Apply the length, number and capital letter rules.
        problem = check_password(password)
        if problem != "":
            show_error("Cannot Create Account", problem)
            return

        # Make sure the two password boxes were typed the same.
        if confirm != password:
            show_error("Cannot Create Account", "Your two passwords do not match. Please type exactly the same password into both boxes.")
            return

        # Save the account with a scrambled password instead of the real one.
        salt = secrets.token_hex(SALT_LENGTH)
        save_account(username, salt, hash_password(password, salt))
        show_info("Account Created", "Welcome " + username + ". Your account has been saved, so next time you can just sign in.")
        open_menu(username)

    # Function for the sign in button.
    def sign_in():
        username = username_entry.get()
        password = password_entry.get()

        if username == "":
            show_error("Cannot Sign In", "You have not typed a username. Please type the username you signed up with.")
            return

        if password == "":
            show_error("Cannot Sign In", "You have not typed a password. Please type the password you signed up with.")
            return

        # Reload from disk each time, so an account made this session is found.
        accounts = load_accounts()
        if username not in accounts:
            show_error("Cannot Sign In", "There is no account saved with the username " + username + ". Please check your spelling, or use Create an account instead to make a new one.")
            return

        # Scramble what was typed and compare it against the scrambled password saved.
        salt, scrambled = accounts[username]
        if hash_password(password, salt) != scrambled:
            show_error("Cannot Sign In", "That password does not match the one saved for " + username + ". Please try typing it again.")
            return

        show_info("Signed In", "Welcome back " + username + ".")
        open_menu(username)

    # Redraw the form for the current mode, hiding the parts sign in does not use.
    def update_form():
        if login_mode == "Sign In":
            login_canvas.itemconfig(title_txt, text="SIGN IN")
            login_canvas.itemconfig(confirm_txt, state=HIDDEN)
            login_canvas.itemconfig(confirm_win, state=HIDDEN)
            login_canvas.itemconfig(rules_txt, state=HIDDEN)
            action_btn.config(text="Sign In", command=sign_in)
            switch_btn.config(text="Create an account instead")
        else:
            login_canvas.itemconfig(title_txt, text="CREATE ACCOUNT")
            login_canvas.itemconfig(confirm_txt, state=NORMAL)
            login_canvas.itemconfig(confirm_win, state=NORMAL)
            login_canvas.itemconfig(rules_txt, state=NORMAL)
            action_btn.config(text="Create Account", command=create_account)
            switch_btn.config(text="Sign in instead")

        # Empty the boxes so nothing is left over from the other mode.
        username_entry.delete(0, END)
        password_entry.delete(0, END)
        confirm_entry.delete(0, END)

    # Swap the window between signing in and making a new account.
    def switch_mode():
        global login_mode
        if login_mode == "Sign In":
            login_mode = "Create Account"
        else:
            login_mode = "Sign In"
        update_form()

    # Set up the main button, whose job changes depending on the mode.
    action_btn = Button(login_win, text="Sign In", font=BUTTON_FONT, width=20, height=2, command=sign_in, bg=ACCENT, fg=BACKGROUND, activebackground=ACCENT_DEEP, activeforeground=BACKGROUND, relief=FLAT, bd=0, cursor="hand2")
    action_win = login_canvas.create_window(325, 450, anchor=CENTER, window=action_btn)

    # Set up the button that swaps between the two modes.
    switch_btn = Button(login_win, text="Create an account instead", font=SMALL_FONT, width=28, command=switch_mode, bg=BACKGROUND, fg=TEXT_DIM, activebackground=BACKGROUND, activeforeground=ACCENT, relief=FLAT, bd=0, cursor="hand2")
    switch_win = login_canvas.create_window(325, 520, anchor=CENTER, window=switch_btn)

    # Closing this window with the X quits, because the menu is hidden behind it.
    login_win.protocol("WM_DELETE_WINDOW", root.destroy)

    # Draw the form before the window is shown.
    update_form()

# Function for the play button, which runs the race itself.
def race():

    # Hide the main menu so only the race is on screen.
    root.withdraw()

    race_win = tk.Toplevel(root)
    race_win.title("Race")
    race_win.geometry("700x700")

    # Set up the canvas widget for the race, drawn as a road.
    race_canvas = Canvas(race_win, width=650, height=650, bg=ROAD_COLOUR, highlightthickness=0)
    race_canvas.pack(pady=5)

    # Paint the dashed lines that divide the road into its three lanes.
    for divider in range(1, LANE_COUNT):
        line_x = (LANE_X[divider - 1] + LANE_X[divider]) / 2
        race_canvas.create_line(line_x, 130, line_x, 650, fill=LANE_LINE_COLOUR, width=4, dash=(24, 22))

    # Set up the wording at the top of the screen.
    header_panel = race_canvas.create_rectangle(0, 0, 650, 132, fill=BACKGROUND, outline="")
    question_txt = race_canvas.create_text(325, QUESTION_Y, text="", font=QUESTION_FONT, fill=TEXT, width=610, justify=CENTER)
    scoreboard_txt = race_canvas.create_text(325, SCOREBOARD_Y, text="", font=SCORE_FONT, fill=ACCENT)
    feedback_txt = race_canvas.create_text(390, BOTTOM_ROW_Y, text="", font=SCORE_FONT, fill=TEXT)

    # Set up the three answer gates, which are moved into place per question.
    gates = []
    gate_texts = []
    for lane in range(LANE_COUNT):
        gates.append(race_canvas.create_rectangle(0, 0, 0, 0, fill=GATE_COLOUR, outline=LANE_LINE_COLOUR, width=3))
        gate_texts.append(race_canvas.create_text(0, 0, text="", font=GATE_FONT, fill=TEXT))

    # Set up the bike, which starts in the middle lane.
    bike_item = race_canvas.create_image(LANE_X[1], BIKE_Y, anchor=CENTER, image=bike_img)

    # Build the race itself from the difficulty and the saved settings.
    game = Race(difficulty_picked, questions_per_race)
    fall_step = SPEEDS[difficulty_picked] // FALL_DIVISOR

    # Work out which lane the bike is in from where it is drawn, so no extra
    # variable has to be kept in step with the picture on screen.
    def bike_lane():
        bike_x = race_canvas.coords(bike_item)[0]
        for lane in range(LANE_COUNT):
            if abs(LANE_X[lane] - bike_x) < 5:
                return lane
        return 1

    # Slide the bike one lane sideways, ignoring the edges of the road.
    def steer(lane):
        if 0 <= lane < LANE_COUNT:
            race_canvas.coords(bike_item, LANE_X[lane], BIKE_Y)

    def go_left(event):
        steer(bike_lane() - 1)

    def go_right(event):
        steer(bike_lane() + 1)

    # Refresh the score line at the top of the road.
    def show_scoreboard():
        race_canvas.itemconfig(scoreboard_txt, text=difficulty_picked.upper() + "    QUESTION " + str(game.asked + 1) + " OF " + str(game.total) + "    SCORE " + str(game.score) + "    " + str(game.accuracy()) + "% CORRECT")

    # Put a new question on the road with its three gates back at the top.
    def show_question():
        race_canvas.itemconfig(question_txt, text=game.question.wording)
        choices = game.question.choices()

        for lane in range(LANE_COUNT):
            race_canvas.coords(gate_texts[lane], LANE_X[lane], ANSWER_START_Y)
            race_canvas.itemconfig(gate_texts[lane], text=choices[lane])
            race_canvas.coords(gates[lane],
                               LANE_X[lane] - GATE_WIDTH / 2, ANSWER_START_Y - GATE_HEIGHT / 2,
                               LANE_X[lane] + GATE_WIDTH / 2, ANSWER_START_Y + GATE_HEIGHT / 2)

        show_scoreboard()

    # Clear the road and show how the whole race went.
    def finish_race():
        for lane in range(LANE_COUNT):
            race_canvas.itemconfig(gate_texts[lane], text="")
            race_canvas.coords(gates[lane], 0, 0, 0, 0)

        race_canvas.itemconfig(question_txt, text="RACE FINISHED")
        race_canvas.itemconfig(scoreboard_txt, text="FINAL SCORE " + str(game.score))
        race_canvas.itemconfig(feedback_txt, text=str(game.correct) + " of " + str(game.total) + " correct, " + str(game.accuracy()) + "% accuracy", fill=TEXT)

    # Move the gates down one frame, and mark the answer when they arrive.
    def drop():

        # Give up if the window was closed part way through the race.
        if not race_win.winfo_exists():
            return

        for lane in range(LANE_COUNT):
            race_canvas.move(gates[lane], 0, fall_step)
            race_canvas.move(gate_texts[lane], 0, fall_step)

        # Keep falling until the gates have reached the bike.
        if race_canvas.coords(gate_texts[0])[1] < BIKE_Y:
            race_win.after(FRAME_DELAY, drop)
            return

        # The gate the bike is sitting in front of is the answer it chose.
        chosen = race_canvas.itemcget(gate_texts[bike_lane()], "text")
        right_answer = game.question.answer

        if game.mark(chosen):
            race_canvas.itemconfig(feedback_txt, text="CORRECT", fill=CORRECT_COLOUR)
        else:
            race_canvas.itemconfig(feedback_txt, text="WRONG, it was " + right_answer, fill=WRONG_COLOUR)

        if game.is_finished():
            finish_race()
            return

        game.next_question()
        show_question()
        race_win.after(FRAME_DELAY, drop)

    # Function for the back button, which abandons the race and returns.
    def back():
        race_win.destroy()
        root.deiconify()

    # Set up the back button in the bottom corner of the road.
    back_btn = Button(race_win, text=" Back", font=BUTTON_FONT, image=back_img, compound=LEFT, command=back, bg=BUTTON_BG, fg=TEXT, activebackground=BUTTON_ACTIVE, activeforeground=ACCENT, relief=FLAT, bd=0, cursor="hand2", padx=8, pady=4)
    back_win = race_canvas.create_window(80, BOTTOM_ROW_Y, anchor=CENTER, window=back_btn)

    # Steer with the arrow keys. There is no answer box on this screen, so
    # left and right are free to be used for driving.
    race_win.bind("<Left>", go_left)
    race_win.bind("<Right>", go_right)
    race_win.focus_set()

    # Send the window X button through the back function so the menu cannot get stranded.
    race_win.protocol("WM_DELETE_WINDOW", back)

    # Put the first question up and start the gates moving.
    show_question()
    drop()


# Function for quit button.
def quit():
    root.destroy()

# Function for leaderboard button.
def leaderboard():
    print ("hello")

# Function for setting button.
def settings():

    # Hide the main menu so only the settings window is on screen.
    root.withdraw()

    settings_win = tk.Toplevel(root)
    settings_win.title("Settings Window")
    settings_win.geometry("700x700")

    # Set up the canvas widget for the settings window.
    settings_canvas = Canvas(settings_win, width=650, height=650, bg=BACKGROUND, highlightthickness=0)
    settings_canvas.pack(pady=5)
    settings_shadow = settings_canvas.create_text(328, 64, text="SETTINGS", font=HEADING_FONT, fill=SHADOW)
    settings_txt = settings_canvas.create_text(325, 60, text="SETTINGS", font=HEADING_FONT, fill=ACCENT)

    # A card behind the two settings so they read as one group.
    settings_panel = settings_canvas.create_rectangle(88, 160, 562, 388, fill=PANEL, outline=PANEL_EDGE, width=2)

    # Set up the sound row, ticked when sound is currently switched on.
    sound_txt = settings_canvas.create_text(280, 210, text="Sound", font=LABEL_FONT, fill=TEXT_DIM, anchor=E)
    sound_value = IntVar(settings_win, value=int(sound_on))
    sound_check = Checkbutton(settings_win, text="On", font=LABEL_FONT, variable=sound_value, bg=PANEL, fg=TEXT, activebackground=PANEL, activeforeground=ACCENT, selectcolor=BACKGROUND, relief=FLAT, bd=0, cursor="hand2")
    sound_win = settings_canvas.create_window(300, 210, anchor=W, window=sound_check)

    # Set up the questions per race box, the one setting that is typed in.
    questions_txt = settings_canvas.create_text(280, 300, text="Questions per race", font=LABEL_FONT, fill=TEXT_DIM, anchor=E)
    questions_entry = Entry(settings_win, font=ENTRY_FONT, width=6, bg=BACKGROUND, fg=TEXT, insertbackground=ACCENT, relief=FLAT, highlightthickness=2, highlightbackground=PANEL_EDGE, highlightcolor=ACCENT)
    questions_win = settings_canvas.create_window(300, 300, anchor=W, window=questions_entry)
    questions_entry.insert(0, str(questions_per_race))

    # Set up the small text explaining what the box will accept.
    questions_rule_txt = settings_canvas.create_text(325, 350, text="Choose a whole number between " + str(QUESTIONS_MIN) + " and " + str(QUESTIONS_MAX) + ".", font=SMALL_FONT, fill=TEXT_DIM)

    # Function for the save button.
    def save():
        global sound_on, questions_per_race

        # The typed box is the only setting that can be wrong, so it is checked first.
        typed = questions_entry.get()
        problem = check_questions(typed)
        if problem != "":
            show_error("Cannot Save Settings", problem)
            return

        sound_on = sound_value.get() == 1
        questions_per_race = int(typed)

        save_settings()
        show_info("Settings Saved", "Your settings have been saved and will still be here next time you play.")

    # Function for the back button, which throws away any unsaved changes.
    def back():
        settings_win.destroy()
        root.deiconify()

    # Set up the save and back buttons.
    save_btn = Button(settings_win, text="Save", font=BUTTON_FONT, width=14, height=2, command=save, bg=ACCENT, fg=BACKGROUND, activebackground=ACCENT_DEEP, activeforeground=BACKGROUND, relief=FLAT, bd=0, cursor="hand2")
    save_win = settings_canvas.create_window(450, 470, anchor=CENTER, window=save_btn)
    back_btn = Button(settings_win, text=" Back", font=BUTTON_FONT, image=back_img, compound=LEFT, command=back, bg=BUTTON_BG, fg=TEXT, activebackground=BUTTON_ACTIVE, activeforeground=ACCENT, relief=FLAT, bd=0, cursor="hand2", padx=8, pady=6)
    back_win = settings_canvas.create_window(150, 470, anchor=CENTER, window=back_btn)

    # Send the window X button through the back function so the menu cannot get stranded.
    settings_win.protocol("WM_DELETE_WINDOW", back)

# Function for mode button.
def difficulty():

    # Hide the main menu so only the difficulty window is on screen.
    root.withdraw()

    difficulty_win = tk.Toplevel(root)
    difficulty_win.title("Difficulty Window")
    difficulty_win.geometry("700x700")

    # Set up the canvas widget for the difficulty window.
    difficulty_canvas = Canvas(difficulty_win, width=650, height=650, bg=BACKGROUND, highlightthickness=0)
    difficulty_canvas.pack(pady=5)
    difficulty_shadow = difficulty_canvas.create_text(328, 59, text="DIFFICULTY", font=HEADING_FONT, fill=SHADOW)
    difficulty_txt = difficulty_canvas.create_text(325, 55, text="DIFFICULTY", font=HEADING_FONT, fill=ACCENT)

    # The square the gauge is drawn inside, worked out from its centre and radius.
    gauge_box = (GAUGE_X - GAUGE_RADIUS, GAUGE_Y - GAUGE_RADIUS, GAUGE_X + GAUGE_RADIUS, GAUGE_Y + GAUGE_RADIUS)

    # Draw a coloured band for each difficulty, each one a third of the dial.
    easy_band = difficulty_canvas.create_arc(gauge_box, start=120, extent=60, style=ARC, width=GAUGE_BAND, outline=ZONE_COLOURS["Easy"])
    medium_band = difficulty_canvas.create_arc(gauge_box, start=60, extent=60, style=ARC, width=GAUGE_BAND, outline=ZONE_COLOURS["Medium"])
    hard_band = difficulty_canvas.create_arc(gauge_box, start=0, extent=60, style=ARC, width=GAUGE_BAND, outline=ZONE_COLOURS["Hard"])

    # Name every band and print its real speed underneath, so the dial shows
    # the same numbers the game actually uses rather than made up ones.
    for level in LABEL_SPOTS:
        spot_x, spot_y, spot_anchor = LABEL_SPOTS[level]
        difficulty_canvas.create_text(spot_x, spot_y, text=level.upper(), font=BAND_FONT, fill=ZONE_COLOURS[level], anchor=spot_anchor)
        difficulty_canvas.create_text(spot_x, spot_y + 24, text="Speed " + str(SPEEDS[level]), font=SMALL_FONT, fill=TEXT_DIM, anchor=spot_anchor)

    # Draw the needle straight up for now. show_needle swings it round below.
    needle = difficulty_canvas.create_line(GAUGE_X, GAUGE_Y, GAUGE_X, GAUGE_Y - NEEDLE_LENGTH, width=6, fill=TEXT, arrow=LAST, arrowshape=(18, 22, 7))
    hub = difficulty_canvas.create_oval(GAUGE_X - 15, GAUGE_Y - 15, GAUGE_X + 15, GAUGE_Y + 15, fill=PANEL, outline=TEXT, width=3)

    # The wording under the dial that spells out what the needle is pointing at.
    chosen_txt = difficulty_canvas.create_text(325, 452, text="", font=SUBHEADING_FONT, fill=TEXT)

    # Put the needle at an exact angle.
    def place_needle(degrees):
        point_x, point_y = needle_point(NEEDLE_LENGTH, degrees)
        difficulty_canvas.coords(needle, GAUGE_X, GAUGE_Y, point_x, point_y)

    # Read back the angle the needle is pointing at from where it is drawn.
    # This only works because the dial is a half circle, so the angle stays
    # between 0 and 180 and never wraps past the point where atan2 flips sign.
    def needle_now():
        start_x, start_y, tip_x, tip_y = difficulty_canvas.coords(needle)
        return math.degrees(math.atan2(start_y - tip_y, tip_x - start_x))

    # Turn the needle one step towards the target, then book the next step.
    def sweep_needle(target):

        # Give up if the window has been closed part way through a sweep.
        if not difficulty_win.winfo_exists():
            return

        # Give up if a different difficulty was picked while this sweep ran,
        # so two sweeps can never fight over the same needle.
        if target != NEEDLE_ANGLES[difficulty_picked]:
            return

        angle = needle_now()
        gap = target - angle

        # Land exactly on the target once the last step would overshoot it.
        if abs(gap) <= NEEDLE_STEP:
            place_needle(target)
            return

        if gap > 0:
            place_needle(angle + NEEDLE_STEP)
        else:
            place_needle(angle - NEEDLE_STEP)

        difficulty_win.after(NEEDLE_DELAY, sweep_needle, target)

    # Update the wording and start the needle sweeping to the new difficulty.
    def show_needle():
        difficulty_canvas.itemconfig(chosen_txt, text=difficulty_picked.upper() + "  -  SPEED " + str(SPEEDS[difficulty_picked]))
        sweep_needle(NEEDLE_ANGLES[difficulty_picked])

    # Function for the easy button.
    def easy():
        global difficulty_picked
        difficulty_picked = "Easy"
        show_needle()

    # Function for the medium button.
    def medium():
        global difficulty_picked
        difficulty_picked = "Medium"
        show_needle()

    # Function for the hard button.
    def hard():
        global difficulty_picked
        difficulty_picked = "Hard"
        show_needle()

    # Function for the back button, which closes this window and brings the menu back.
    def back():
        difficulty_win.destroy()
        root.deiconify()

    # Set up the three difficulty buttons, sitting under the band each one selects.
    easy_btn = Button(difficulty_win, text="Easy", font=BUTTON_FONT, width=11, height=2, command=easy, bg=BUTTON_BG, fg=ZONE_COLOURS["Easy"], activebackground=BUTTON_ACTIVE, activeforeground=ZONE_COLOURS["Easy"], relief=FLAT, bd=0, cursor="hand2")
    easy_win = difficulty_canvas.create_window(120, 520, anchor=CENTER, window=easy_btn)
    medium_btn = Button(difficulty_win, text="Medium", font=BUTTON_FONT, width=11, height=2, command=medium, bg=BUTTON_BG, fg=ZONE_COLOURS["Medium"], activebackground=BUTTON_ACTIVE, activeforeground=ZONE_COLOURS["Medium"], relief=FLAT, bd=0, cursor="hand2")
    medium_win = difficulty_canvas.create_window(325, 520, anchor=CENTER, window=medium_btn)
    hard_btn = Button(difficulty_win, text="Hard", font=BUTTON_FONT, width=11, height=2, command=hard, bg=BUTTON_BG, fg=ZONE_COLOURS["Hard"], activebackground=BUTTON_ACTIVE, activeforeground=ZONE_COLOURS["Hard"], relief=FLAT, bd=0, cursor="hand2")
    hard_win = difficulty_canvas.create_window(530, 520, anchor=CENTER, window=hard_btn)

    # Set up the back button, using the arrow image next to the word Back.
    back_btn = Button(difficulty_win, text=" Back", font=BUTTON_FONT, image=back_img, compound=LEFT, command=back, bg=BUTTON_BG, fg=TEXT, activebackground=BUTTON_ACTIVE, activeforeground=ACCENT, relief=FLAT, bd=0, cursor="hand2", padx=8, pady=6)
    back_win = difficulty_canvas.create_window(110, 600, anchor=CENTER, window=back_btn)

    # Send the window X button through the back function so the menu cannot get stranded.
    difficulty_win.protocol("WM_DELETE_WINDOW", back)

    # Sweep the needle round to the saved difficulty as the window opens.
    show_needle()



# Set up buttons for main menu.
play_btn = Button(root, text="PLAY", font=(BODY_TYPEFACE, 16, "bold"), width=18, height=2, command=race, bg=ACCENT, fg=BACKGROUND, activebackground=ACCENT_DEEP, activeforeground=BACKGROUND, relief=FLAT, bd=0, cursor="hand2")
menu_play_win = canvas.create_window(350, 350, anchor=CENTER, window=play_btn)
quit_btn = Button(root, text="Quit", font=BUTTON_FONT, width=15, height=2, command=quit, bg=BUTTON_BG, fg=TEXT, activebackground=BUTTON_ACTIVE, activeforeground=ACCENT, relief=FLAT, bd=0, cursor="hand2")
menu_quit_win = canvas.create_window(500, 525, anchor=CENTER, window=quit_btn)
leaderboard_btn = Button(root, text="Leaderboard", font=BUTTON_FONT, width=15, height=2, command=leaderboard, bg=BUTTON_BG, fg=TEXT, activebackground=BUTTON_ACTIVE, activeforeground=ACCENT, relief=FLAT, bd=0, cursor="hand2")
menu_leaderboard_win = canvas.create_window(500, 225, anchor=CENTER, window=leaderboard_btn)
settings_btn = Button(root, text="Setting", font=BUTTON_FONT, width=15, height=2, command=settings, bg=BUTTON_BG, fg=TEXT, activebackground=BUTTON_ACTIVE, activeforeground=ACCENT, relief=FLAT, bd=0, cursor="hand2")
menu_settings_win = canvas.create_window(200, 225, anchor=CENTER, window=settings_btn)
difficulty_btn = Button(root, text="Difficulty", font=BUTTON_FONT, width=15, height=2, command=difficulty, bg=BUTTON_BG, fg=TEXT, activebackground=BUTTON_ACTIVE, activeforeground=ACCENT, relief=FLAT, bd=0, cursor="hand2")
menu_difficulty_win = canvas.create_window(200, 525, anchor=CENTER, window=difficulty_btn)




# Load the saved settings before the menu is shown.
load_settings()

# Hide the main menu and make the user sign in before they can reach it.
root.withdraw()
login()

root.mainloop()