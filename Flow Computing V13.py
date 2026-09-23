# Author: Maurya Patel
# Date: 03/09/2026
# Purpose: Maths Racing Game

# Racing colour scheme for the dark theme.
dark_colours = {
    "background": "#12141c" ,
    "panel": "#1c2030" ,
    "panel_edge": "#2e3446" ,
    "shadow": "#05060a" ,
    "text": "#f2f4f8" ,
    "dim_text": "#9aa1b4" ,
    "button": "#2a3040" ,
    "button_text": "#f2f4f8" ,
    "button_active": "#3b435a" ,
    "accent": "#ffd23f" ,
    "accent_deep": "#e0a800" ,
    "on_accent": "#12141c" ,
    "road": "#262a35" ,
    "lane": "#e9ecf3" ,
    "edge": "#4a5163" ,
    "gate": "#12141c" ,
    "correct": "#4ade80" ,
    "wrong": "#f87171" ,
    "easy": "#3ddc84" ,
    "medium": "#ffb020" ,
    "hard": "#ff5c5c"
}

# The same colours again for the light theme, dark writing on a pale background.
light_colours = {
    "background": "#f2f4f8" ,
    "panel": "#ffffff" ,
    "panel_edge": "#d3d8e2" ,
    "shadow": "#c4cad6" ,
    "text": "#12141c" ,
    "dim_text": "#5a6070" ,
    "button": "#e2e6ef" ,
    "button_text": "#12141c" ,
    "button_active": "#cdd3e0" ,
    "accent": "#f0a500" ,
    "accent_deep": "#c98700" ,
    "on_accent": "#12141c" ,
    "road": "#b9c0cd" ,
    "lane": "#ffffff" ,
    "edge": "#7c8494" ,
    "gate": "#ffffff" ,
    "correct": "#2fa860" ,
    "wrong": "#d64545" ,
    "easy": "#1f9d55" ,
    "medium": "#c47f00" ,
    "hard": "#d64545"
}

title_font = "Impact"
font = "Segoe UI"

# Importing tkinter library and other important components from tkinter and python.
from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
import os
import random
import math
import time
import hashlib
import secrets
from PIL import Image , ImageTk

# Winsound only works on Windows, so the beep is skipped on other systems.
try:
    import winsound
    sound_available = True
except ImportError:
    sound_available = False

# Setting global variables for use later on.
current_user = None
current_difficulty = "Easy"
login_mode = "Sign In"
sound_on = True
current_theme = "Dark"
back_img = None

# The rules a username and a password have to follow.
username_min = 3
username_max = 12
password_min = 5

# Every race is the same length, whatever difficulty is being played.
questions_per_race = 10

# The pitch and length of the beep that plays when an error box appears.
beep_hertz = 700
beep_milliseconds = 150

# Points won for a right answer at each difficulty, so harder is worth more.
points = {"Easy": 10 , "Medium": 20 , "Hard": 30}

# Points taken off for a wrong answer, whatever the difficulty.
wrong_penalty = 5

# How fast the gates run down the road, so a harder race gives less time to choose.
gate_speeds = {"Easy": 20 , "Medium": 30 , "Hard": 40}

# The angle the needle points to for each difficulty.
needle_angles = {"Easy": 150 , "Medium": 90 , "Hard": 30}

# Creating a dictionary of the topics each difficulty draws its questions from.
topics = {
    "Easy": [
        "Addition" ,
        "Subtraction" ,
        "Multiplication" ,
        "Division"
    ] ,

    "Medium": [
        "Exponents" ,
        "Square Roots" ,
        "Fractions" ,
        "Percentages" ,
        "Prime Numbers" ,
        "Highest Common Factor" ,
        "Lowest Common Multiple"
    ] ,

    "Hard": [
        "Algebra" ,
        "Area" ,
        "Perimeter" ,
        "Volume" ,
        "Mean" ,
        "Median" ,
        "Mode" ,
        "Differentiation" ,
        "Integration"
    ]
}

# The end of race message for each accuracy, best first.
result_messages = [
    [90 , "Superb driving. Almost everything right."] ,
    [70 , "A strong race, with only a few slips."] ,
    [50 , "A steady run. Worth another lap."] ,
    [25 , "Getting there. Keep practising these topics."] ,
    [0 , "A tough race. Try an easier level to build up."]
]

# The three lanes the bike drives between and the middle of each one.
lane_count = 3
lane_x = [108 , 325 , 542]

# Where everything sits on the race track.
question_y = 50
scoreboard_y = 105
instruction_y = 133
header_bottom = 152
progress_top = 152
progress_bottom = 158
progress_left = 60
progress_right = 590
road_top = 164
road_bottom = 600
gate_y = 228
gate_stop_y = 462
bike_y = 540
bottom_row_y = 624
road_edge = 14

# The size of each answer gate.
gate_width = 168
gate_height = 54

# The dash pattern of the lane markings and the length of one repeat.
lane_dash = (26 , 24)
dash_cycle = 50

# How long the screen waits between frames and how gate speed becomes pixels.
frame_delay = 40
drive_divisor = 3

# How long the correct or wrong message stays on screen.
feedback_pause = 950

# The speedometer that the difficulty screen is drawn as.
gauge_x = 325
gauge_y = 395
gauge_radius = 170
gauge_band = 24
needle_length = 132
needle_step = 4
needle_delay = 12

# Where the sign in form sits and where each of its rows lines up.
form_left = 78
form_top = 152
form_right = 572
form_bottom = 404
label_right = 288
field_left = 308
username_row = 200
password_row = 260
confirm_row = 320
rules_row = 380
action_row = 450
switch_row = 520
show_button_x = 500

# Where the three leaderboards and their columns go.
leaderboard_rows = 10
board_top = 128
board_bottom = 556
board_width = 190
board_gap = 20
name_offset = 12
score_offset = 132
time_offset = 180
row_top = 228
row_height = 33

# Where the settings panel and its two rows sit.
settings_left = 88
settings_top = 160
settings_right = 562
settings_bottom = 388
sound_row = 210
theme_row = 300

# Where the results card and the figures on it sit.
results_left = 70
results_top = 140
results_right = 580
results_bottom = 470
stats_left = 133
stats_gap = 128
bar_left = 120
bar_right = 530

# What the player has to do, spelled out so nobody has to guess.
driving_help = "Left and right arrows to pick a lane, then Space or Enter to drive through it."

# Returns the highest common factor of two numbers using Euclid's method.
def highest_common_factor(first , second):
    while second != 0:
        first , second = second , first % second
    return first

# Returns a fraction in its simplest form, or a whole number when it divides exactly.
def simplify_fraction(top , bottom):
    divisor = highest_common_factor(top , bottom)
    top = top // divisor
    bottom = bottom // divisor

    if bottom == 1:
        return str(top)

    return str(top) + "/" + str(bottom)

# Returns True when a number is prime, testing factors up to its square root.
def is_prime(number):
    if number < 2:
        return False

    checker = 2
    while checker * checker <= number:
        if number % checker == 0:
            return False
        checker = checker + 1

    return True

# Returns a number of seconds written as minutes and seconds, for example 2:05.
def format_time(seconds):
    minutes = seconds // 60
    rest = seconds % 60
    return str(minutes) + ":" + str(rest).zfill(2)

# Returns the closing message that matches how accurate the race was.
def result_message(accuracy):
    for lowest , message in result_messages:
        if accuracy >= lowest:
            return message

    return result_messages[-1][1]

# Builds two believable wrong answers to sit in the other two lanes.
def wrong_answers(answer):
    wrongs = []

    # A fraction answer needs fraction decoys or the right one would stand out.
    if "/" in answer:
        top , bottom = answer.split("/")
        top = int(top)
        bottom = int(bottom)
        guesses = [str(top + 1) + "/" + str(bottom) , str(top) + "/" + str(bottom + 2) , str(bottom) + "/" + str(top) , str(top + 2) + "/" + str(bottom)]
        random.shuffle(guesses)

        for guess in guesses:
            if guess != answer and guess not in wrongs:
                wrongs.append(guess)
            if len(wrongs) == 2:
                break

        return wrongs

    # Whole number answers get decoys just above and below the real answer.
    number = int(answer)
    guesses = [number - 2 , number - 1 , number + 1 , number + 2 , number + 10]
    random.shuffle(guesses)

    for guess in guesses:
        # Never offer a negative decoy when the real answer is positive.
        if guess > 0 and str(guess) != answer and str(guess) not in wrongs:
            wrongs.append(str(guess))
        if len(wrongs) == 2:
            break

    # Widen the gap until two decoys are found, however small the answer.
    gap = 3
    while len(wrongs) < 2:
        guess = str(number + gap)
        if guess != answer and guess not in wrongs:
            wrongs.append(guess)
        gap = gap + 1

    return wrongs

# Builds one question into the same dictionary shape every screen expects.
def build_question(question , answer , topic):
    options = wrong_answers(answer)
    options.append(answer)
    random.shuffle(options)

    return {
        "question": question ,
        "options": options ,
        "answer": answer ,
        "topic": topic
    }

# Makes an addition question.
def make_addition():
    first = random.randint(2 , 50)
    second = random.randint(2 , 50)
    return build_question("What is " + str(first) + " + " + str(second) + "?" , str(first + second) , "Addition")

# Makes a subtraction question, larger number first so it is never negative.
def make_subtraction():
    first = random.randint(20 , 60)
    second = random.randint(2 , 19)
    return build_question("What is " + str(first) + " - " + str(second) + "?" , str(first - second) , "Subtraction")

# Makes a times table question.
def make_multiplication():
    first = random.randint(2 , 12)
    second = random.randint(2 , 12)
    return build_question("What is " + str(first) + " x " + str(second) + "?" , str(first * second) , "Multiplication")

# Makes a division question from the answer, which keeps it exact.
def make_division():
    divisor = random.randint(2 , 12)
    answer = random.randint(2 , 12)
    return build_question("What is " + str(divisor * answer) + " / " + str(divisor) + "?" , str(answer) , "Division")

# Makes a power question, using smaller numbers for cubes than for squares.
def make_exponents():
    power = random.randint(2 , 3)

    if power == 2:
        base = random.randint(2 , 20)
    else:
        base = random.randint(2 , 10)

    return build_question("What is " + str(base) + " to the power of " + str(power) + "?" , str(base ** power) , "Exponents")

# Makes a square root question by squaring the answer first.
def make_square_root():
    answer = random.randint(2 , 30)
    return build_question("What is the square root of " + str(answer * answer) + "?" , str(answer) , "Square Roots")

# Makes an addition of two fractions that share a denominator.
def make_fraction():
    bottom = random.choice([4 , 6 , 8 , 10 , 12])
    first = random.randint(1 , bottom - 2)
    second = random.randint(1 , bottom - first - 1)
    question = "What is " + str(first) + "/" + str(bottom) + " + " + str(second) + "/" + str(bottom) + "? Give your answer as a fraction in its simplest form."
    return build_question(question , simplify_fraction(first + second , bottom) , "Fractions")

# Makes a percentage question that always gives a whole number.
def make_percentage():
    percent = random.choice([10 , 20 , 25 , 50 , 75])
    amount = random.randint(1 , 20) * 20
    return build_question("What is " + str(percent) + "% of " + str(amount) + "?" , str(percent * amount // 100) , "Percentages")

# Makes a question asking for the next prime number after a starting point.
def make_prime():
    start = random.randint(5 , 150)
    answer = start + 1

    while not is_prime(answer):
        answer = answer + 1

    return build_question("What is the next prime number after " + str(start) + "?" , str(answer) , "Prime Numbers")

# Makes a highest common factor question from two numbers sharing a factor.
def make_factor():
    shared = random.randint(2 , 12)
    first = shared * random.randint(2 , 9)
    second = first

    # Keep picking until the two numbers are different.
    while second == first:
        second = shared * random.randint(2 , 9)

    return build_question("What is the highest common factor of " + str(first) + " and " + str(second) + "?" , str(highest_common_factor(first , second)) , "Highest Common Factor")

# Makes a lowest common multiple question.
def make_multiple():
    first = random.randint(3 , 20)
    second = first

    # Two of the same number would make the question too easy.
    while second == first:
        second = random.randint(3 , 20)

    answer = first * second // highest_common_factor(first , second)
    return build_question("What is the lowest common multiple of " + str(first) + " and " + str(second) + "?" , str(answer) , "Lowest Common Multiple")

# Makes a one step equation, working backwards from a chosen whole number x.
def make_algebra():
    answer = random.randint(2 , 12)
    times = random.randint(2 , 9)
    plus = random.randint(1 , 20)
    question = "Solve for x:   " + str(times) + "x + " + str(plus) + " = " + str(times * answer + plus)
    return build_question(question , str(answer) , "Algebra")

# Makes a rectangle area question.
def make_area():
    width = random.randint(3 , 15)
    height = random.randint(3 , 15)
    question = "A rectangle is " + str(width) + " cm wide and " + str(height) + " cm tall. What is its area in square cm?"
    return build_question(question , str(width * height) , "Area")

# Makes a rectangle perimeter question.
def make_perimeter():
    width = random.randint(3 , 15)
    height = random.randint(3 , 15)
    question = "A rectangle is " + str(width) + " cm wide and " + str(height) + " cm tall. What is its perimeter in cm?"
    return build_question(question , str(2 * (width + height)) , "Perimeter")

# Makes a cuboid volume question.
def make_volume():
    length = random.randint(2 , 12)
    width = random.randint(2 , 12)
    height = random.randint(2 , 12)
    question = "A box is " + str(length) + " cm long, " + str(width) + " cm wide and " + str(height) + " cm tall. What is its volume in cubic cm?"
    return build_question(question , str(length * width * height) , "Volume")

# Makes a mean question whose numbers divide exactly.
def make_mean():
    count = random.choice([3 , 4 , 5])
    numbers = []

    while len(numbers) == 0 or sum(numbers) % count != 0:
        numbers = []
        for spare in range(count):
            numbers.append(random.randint(2 , 30))

    question = "What is the mean of " + ", ".join(str(number) for number in numbers) + "?"
    return build_question(question , str(sum(numbers) // count) , "Mean")

# Makes a median question with an odd count, so the middle is a single value.
def make_median():
    count = random.choice([3 , 5 , 7])
    numbers = random.sample(range(1 , 60) , count)
    middle = sorted(numbers)[count // 2]
    question = "What is the median of " + ", ".join(str(number) for number in numbers) + "?"
    return build_question(question , str(middle) , "Median")

# Makes a mode question with exactly one most common value.
def make_mode():
    common = random.randint(1 , 20)
    numbers = [common , common , common]

    while len(numbers) < 7:
        spare = random.randint(1 , 20)
        if spare != common and numbers.count(spare) < 2:
            numbers.append(spare)

    random.shuffle(numbers)
    question = "What is the mode of " + ", ".join(str(number) for number in numbers) + "?"
    return build_question(question , str(common) , "Mode")

# Makes a differentiation question answered at a point, using the power rule.
def make_differentiation():
    coefficient = random.randint(2 , 9)
    power = random.randint(2 , 4)
    at = random.randint(1 , 5)
    gradient = power * coefficient * (at ** (power - 1))
    question = "y = " + str(coefficient) + "x^" + str(power) + ".   What is dy/dx when x = " + str(at) + "?"
    return build_question(question , str(gradient) , "Differentiation")

# Makes a definite integral question that divides exactly.
def make_integration():
    power = random.randint(1 , 3)
    coefficient = (power + 1) * random.randint(1 , 5)
    upper = random.randint(2 , 5)
    area = coefficient * (upper ** (power + 1)) // (power + 1)

    # Nobody writes x^1, so the power is left off when it is one.
    if power == 1:
        equation = str(coefficient) + "x"
    else:
        equation = str(coefficient) + "x^" + str(power)

    question = "What is the area under y = " + equation + " between x = 0 and x = " + str(upper) + "?"
    return build_question(question , str(area) , "Integration")

# Creating a dictionary that matches every topic name to the function that makes it.
question_makers = {
    "Addition": make_addition ,
    "Subtraction": make_subtraction ,
    "Multiplication": make_multiplication ,
    "Division": make_division ,
    "Exponents": make_exponents ,
    "Square Roots": make_square_root ,
    "Fractions": make_fraction ,
    "Percentages": make_percentage ,
    "Prime Numbers": make_prime ,
    "Highest Common Factor": make_factor ,
    "Lowest Common Multiple": make_multiple ,
    "Algebra": make_algebra ,
    "Area": make_area ,
    "Perimeter": make_perimeter ,
    "Volume": make_volume ,
    "Mean": make_mean ,
    "Median": make_median ,
    "Mode": make_mode ,
    "Differentiation": make_differentiation ,
    "Integration": make_integration
}

# Makes one random question from the topics that difficulty uses.
def make_question(difficulty):
    topic = random.choice(topics[difficulty])
    return question_makers[topic]()

# Beeps for errors, unless sound is off or the computer is not running Windows.
def play_beep():
    if sound_on and sound_available:
        winsound.Beep(beep_hertz , beep_milliseconds)

# Shows an error message box with a beep to draw the user's attention.
def show_error(title , message):
    play_beep()
    messagebox.showerror(title , message)

# Shows a success message box, kept separate from show_error.
def show_info(title , message):
    messagebox.showinfo(title , message)

# Paints every colour in the game from whichever theme is switched on.
def apply_theme():
    global background_color , panel_color , panel_edge , shadow_color , text_color , dim_text
    global button_color , button_text , button_active , accent , accent_deep , on_accent
    global road_color , lane_color , edge_color , gate_color , correct_color , wrong_color
    global zone_colors

    if current_theme == "Light":
        colours = light_colours
    else:
        colours = dark_colours

    background_color = colours["background"]
    panel_color = colours["panel"]
    panel_edge = colours["panel_edge"]
    shadow_color = colours["shadow"]
    text_color = colours["text"]
    dim_text = colours["dim_text"]
    button_color = colours["button"]
    button_text = colours["button_text"]
    button_active = colours["button_active"]
    accent = colours["accent"]
    accent_deep = colours["accent_deep"]
    on_accent = colours["on_accent"]
    road_color = colours["road"]
    lane_color = colours["lane"]
    edge_color = colours["edge"]
    gate_color = colours["gate"]
    correct_color = colours["correct"]
    wrong_color = colours["wrong"]

    # The three bands on the dial are named separately so they can be looked up.
    zone_colors = {"Easy": colours["easy"] , "Medium": colours["medium"] , "Hard": colours["hard"]}

# Returns the full path of a saved file so it always sits beside this program.
def file_path(name):
    return os.path.join(os.path.dirname(__file__) , name)

# Makes the canvas that every screen is drawn on.
def build_canvas(colour):
    canvas = Canvas(main_screen , width = 650 , height = 650 , bg = colour , highlightthickness = 0)
    canvas.pack(pady = 5)
    return canvas

# Draws a heading with its drop shadow, the same way on every screen.
def draw_heading(canvas , words , y , size):
    canvas.create_text(328 , y + 4 , text = words , font = (title_font , size) , fill = shadow_color)
    canvas.create_text(325 , y , text = words , font = (title_font , size) , fill = accent)

# Loads the back arrow picture and keeps a reference so tkinter does not bin it.
def load_back_image():
    global back_img

    picture = Image.open(file_path("Back.png")).resize((25 , 25)).convert("RGBA")

    # The arrow was drawn pale, so it is repainted in the writing colour for light mode.
    red = int(text_color[1:3] , 16)
    green = int(text_color[3:5] , 16)
    blue = int(text_color[5:7] , 16)
    pixels = picture.load()

    for x in range(picture.width):
        for y in range(picture.height):
            pixels[x , y] = (red , green , blue , pixels[x , y][3])

    back_img = ImageTk.PhotoImage(picture)
    return back_img

# Sign in screen, which doubles as the create account screen.
# The same three boxes serve both jobs, so there is only one form to keep working.
def main():
    clear_screen()

    global login_mode

    canvas = build_canvas(background_color)
    title = canvas.create_text(325 , 70 , text = "SIGN IN" , font = (title_font , 38) , fill = accent)
    shadow = canvas.create_text(328 , 74 , text = "SIGN IN" , font = (title_font , 38) , fill = shadow_color)
    canvas.tag_raise(title)

    # A card behind the form so the boxes do not float on the background.
    canvas.create_rectangle(form_left , form_top , form_right , form_bottom , fill = panel_color , outline = panel_edge , width = 2)

    # The username row.
    canvas.create_text(label_right , username_row , text = "Username" , font = (font , 12 , "bold") , fill = dim_text , anchor = E)
    username_entry = Entry(main_screen , font = (font , 13) , width = 20 , bg = background_color , fg = text_color , insertbackground = accent , relief = FLAT)
    canvas.create_window(field_left , username_row , anchor = W , window = username_entry)

    # The password row, which hides the letters as they are typed.
    canvas.create_text(label_right , password_row , text = "Password" , font = (font , 12 , "bold") , fill = dim_text , anchor = E)
    password_entry = Entry(main_screen , font = (font , 13) , width = 20 , show = "*" , bg = background_color , fg = text_color , insertbackground = accent , relief = FLAT)
    canvas.create_window(field_left , password_row , anchor = W , window = password_entry)

    # The confirm row, which is only needed when making an account.
    confirm_label = canvas.create_text(label_right , confirm_row , text = "Confirm Password" , font = (font , 12 , "bold") , fill = dim_text , anchor = E)
    confirm_entry = Entry(main_screen , font = (font , 13) , width = 20 , show = "*" , bg = background_color , fg = text_color , insertbackground = accent , relief = FLAT)
    confirm_window = canvas.create_window(field_left , confirm_row , anchor = W , window = confirm_entry)

    # Function for show password button to switch between hidden * and visible.
    def show_password():
        if password_entry.cget("show") == "*":
            password_entry.config(show = "")
            confirm_entry.config(show = "")
            show_button.config(text = "Hide")
        else:
            password_entry.config(show = "*")
            confirm_entry.config(show = "*")
            show_button.config(text = "Show")

    show_button = Button(main_screen , text = "Show" , font = (font , 9) , width = 6 , command = show_password , fg = button_text , bg = button_color , activebackground = button_active , relief = FLAT)
    canvas.create_window(show_button_x , password_row , anchor = W , window = show_button)

    # The password rules, shown only while an account is being created.
    rules = canvas.create_text(325 , rules_row , text = "Your password must be at least " + str(password_min) + " characters long, and include at least 1 number and 1 capital letter." , font = (font , 9) , fill = dim_text , width = 420)

    # Remembers who signed in and hands over to the main menu.
    def open_menu(username):
        global current_user
        current_user = username
        menu_screen()

    # Checks every rule, then saves a new account and signs the user straight in.
    def create_account():
        username = username_entry.get()
        password = password_entry.get()
        confirm = confirm_entry.get()

        # Rejecting a bad username before the accounts file is opened.
        if username == "":
            show_error("Cannot Create Account" , "You have not typed a username. Please type one into the username box.")
            return

        if len(username) < username_min:
            show_error("Cannot Create Account" , "Your username is only " + str(len(username)) + " characters long. Please make it at least " + str(username_min) + " characters.")
            return

        if len(username) > username_max:
            show_error("Cannot Create Account" , "Your username is " + str(len(username)) + " characters long, which is too long. Please shorten it to " + str(username_max) + " characters or fewer.")
            return

        if " " in username:
            show_error("Cannot Create Account" , "Your username has a space in it. Please use an underscore instead, for example math_racer.")
            return

        if "," in username:
            show_error("Cannot Create Account" , "Your username has a comma in it. Commas separate the details inside the accounts file, so please use a different character.")
            return

        # Stopping the user taking a username that somebody else already has.
        if username in load_accounts():
            show_error("Cannot Create Account" , "The username " + username + " is already taken. Please choose a different username.")
            return

        if password == "":
            show_error("Cannot Create Account" , "You have not typed a password. Please type one into the password box.")
            return

        if len(password) < password_min:
            short_by = password_min - len(password)
            show_error("Cannot Create Account" , "Your password is only " + str(len(password)) + " characters long. Please add " + str(short_by) + " more so it is at least " + str(password_min) + " characters.")
            return

        # One pass over the password, checking for both requirements at once.
        has_number = False
        has_capital = False
        for letter in password:
            if letter.isdigit():
                has_number = True
            if letter.isupper():
                has_capital = True

        if not has_number:
            show_error("Cannot Create Account" , "Your password does not contain a number. Please add at least 1 number, for example 4 or 9.")
            return

        if not has_capital:
            show_error("Cannot Create Account" , "Your password does not contain a capital letter. Please add at least 1 capital letter, for example A or M.")
            return

        if "," in password:
            show_error("Cannot Create Account" , "Your password has a comma in it. Commas separate the details inside the accounts file, so please use a different character.")
            return

        # Making sure the two password boxes were typed the same.
        if confirm != password:
            show_error("Cannot Create Account" , "Your two passwords do not match. Please type exactly the same password into both boxes.")
            return

        save_account(username , password)
        show_info("Account Created" , "Welcome " + username + ". Your account has been saved, so next time you can just sign in.")
        open_menu(username)

    # Checks the typed details against the accounts file and signs the user in.
    def sign_in():
        username = username_entry.get()
        password = password_entry.get()

        if username == "":
            show_error("Cannot Sign In" , "You have not typed a username. Please type the username you signed up with.")
            return

        if password == "":
            show_error("Cannot Sign In" , "You have not typed a password. Please type the password you signed up with.")
            return

        # Reading from the file each time means an account made this session is found.
        accounts = load_accounts()

        if username not in accounts:
            show_error("Cannot Sign In" , "There is no account saved with the username " + username + ". Please check your spelling, or use Create an account instead to make a new one.")
            return

        salt , scrambled = accounts[username]

        if hash_password(password , salt) != scrambled:
            show_error("Cannot Sign In" , "That password does not match the one saved for " + username + ". Please try typing it again.")
            return

        show_info("Signed In" , "Welcome back " + username + ".")
        open_menu(username)

    # Redraws the form for the current mode, hiding what sign in does not use.
    def update_form():
        if login_mode == "Sign In":
            canvas.itemconfig(title , text = "SIGN IN")
            canvas.itemconfig(shadow , text = "SIGN IN")
            canvas.itemconfig(confirm_label , state = HIDDEN)
            canvas.itemconfig(confirm_window , state = HIDDEN)
            canvas.itemconfig(rules , state = HIDDEN)
            action_button.config(text = "Sign In" , command = sign_in)
            switch_button.config(text = "Create an account instead")
        else:
            canvas.itemconfig(title , text = "CREATE ACCOUNT")
            canvas.itemconfig(shadow , text = "CREATE ACCOUNT")
            canvas.itemconfig(confirm_label , state = NORMAL)
            canvas.itemconfig(confirm_window , state = NORMAL)
            canvas.itemconfig(rules , state = NORMAL)
            action_button.config(text = "Create Account" , command = create_account)
            switch_button.config(text = "Sign in instead")

        # Emptying the boxes so nothing is left over from the other mode.
        username_entry.delete(0 , END)
        password_entry.delete(0 , END)
        confirm_entry.delete(0 , END)

    # Swaps the screen between signing in and making a new account.
    def switch_mode():
        global login_mode

        if login_mode == "Sign In":
            login_mode = "Create Account"
        else:
            login_mode = "Sign In"

        update_form()

    # The main button, whose job changes depending on the mode.
    action_button = Button(main_screen , text = "Sign In" , font = (font , 11 , "bold") , width = 20 , height = 2 , command = sign_in , fg = on_accent , bg = accent , activebackground = accent_deep , relief = FLAT)
    canvas.create_window(325 , action_row , anchor = CENTER , window = action_button)

    # The quiet button that swaps between the two modes.
    switch_button = Button(main_screen , text = "Create an account instead" , font = (font , 9) , width = 28 , command = switch_mode , fg = dim_text , bg = background_color , activebackground = background_color , activeforeground = accent , relief = FLAT)
    canvas.create_window(325 , switch_row , anchor = CENTER , window = switch_button)

    update_form()
    username_entry.focus_set()

# Menu screen function displays the play, difficulty, settings and leaderboard buttons.
def menu_screen():
    clear_screen()

    canvas = build_canvas(background_color)
    draw_heading(canvas , "MATH RACER" , 54 , 58)
    canvas.create_line(140 , 108 , 510 , 108 , fill = panel_edge , width = 3)
    canvas.create_text(325 , 620 , text = "Signed in as " + str(current_user) , font = (font , 9) , fill = dim_text)

    play_button = Button(main_screen , text = "PLAY" , font = (font , 16 , "bold") , width = 18 , height = 2 , command = lambda: start_race(current_difficulty , current_user) , fg = on_accent , bg = accent , activebackground = accent_deep , relief = FLAT)
    canvas.create_window(350 , 350 , anchor = CENTER , window = play_button)

    settings_button = Button(main_screen , text = "Setting" , font = (font , 11 , "bold") , width = 15 , height = 2 , command = settings_screen , fg = button_text , bg = button_color , activebackground = button_active , relief = FLAT)
    canvas.create_window(200 , 225 , anchor = CENTER , window = settings_button)

    leaderboard_button = Button(main_screen , text = "Leaderboard" , font = (font , 11 , "bold") , width = 15 , height = 2 , command = leaderboard_screen , fg = button_text , bg = button_color , activebackground = button_active , relief = FLAT)
    canvas.create_window(500 , 225 , anchor = CENTER , window = leaderboard_button)

    difficulty_button = Button(main_screen , text = "Difficulty" , font = (font , 11 , "bold") , width = 15 , height = 2 , command = difficulty_screen , fg = button_text , bg = button_color , activebackground = button_active , relief = FLAT)
    canvas.create_window(200 , 525 , anchor = CENTER , window = difficulty_button)

    quit_button = Button(main_screen , text = "Quit" , font = (font , 11 , "bold") , width = 15 , height = 2 , command = close_program , fg = button_text , bg = button_color , activebackground = button_active , relief = FLAT)
    canvas.create_window(500 , 525 , anchor = CENTER , window = quit_button)

# Difficulty screen shows a speedometer whose needle sweeps to the chosen level.
def difficulty_screen():
    clear_screen()

    canvas = build_canvas(background_color)
    draw_heading(canvas , "DIFFICULTY" , 55 , 38)

    # The square the gauge is drawn inside, worked out from its centre and radius.
    box = (gauge_x - gauge_radius , gauge_y - gauge_radius , gauge_x + gauge_radius , gauge_y + gauge_radius)

    # Drawing a coloured band for each difficulty, each one a third of the dial.
    canvas.create_arc(box , start = 120 , extent = 60 , style = ARC , width = gauge_band , outline = zone_colors["Easy"])
    canvas.create_arc(box , start = 60 , extent = 60 , style = ARC , width = gauge_band , outline = zone_colors["Medium"])
    canvas.create_arc(box , start = 0 , extent = 60 , style = ARC , width = gauge_band , outline = zone_colors["Hard"])

    # Naming every band and printing its real speed underneath the name.
    canvas.create_text(132 , 282 , text = "EASY" , font = (title_font , 24) , fill = zone_colors["Easy"] , anchor = E)
    canvas.create_text(132 , 306 , text = str(points["Easy"]) + " points an answer" , font = (font , 9) , fill = dim_text , anchor = E)
    canvas.create_text(325 , 166 , text = "MEDIUM" , font = (title_font , 24) , fill = zone_colors["Medium"] , anchor = S)
    canvas.create_text(325 , 190 , text = str(points["Medium"]) + " points an answer" , font = (font , 9) , fill = dim_text , anchor = S)
    canvas.create_text(518 , 282 , text = "HARD" , font = (title_font , 24) , fill = zone_colors["Hard"] , anchor = W)
    canvas.create_text(518 , 306 , text = str(points["Hard"]) + " points an answer" , font = (font , 9) , fill = dim_text , anchor = W)

    # The needle starts pointing straight up and is swung round by sweep_needle.
    needle = canvas.create_line(gauge_x , gauge_y , gauge_x , gauge_y - needle_length , width = 6 , fill = text_color , arrow = LAST , arrowshape = (18 , 22 , 7))
    canvas.create_oval(gauge_x - 15 , gauge_y - 15 , gauge_x + 15 , gauge_y + 15 , fill = panel_color , outline = text_color , width = 3)

    # The wording under the dial that spells out what the needle points at.
    chosen = canvas.create_text(325 , 452 , text = "" , font = (font , 15 , "bold") , fill = text_color)

    # Puts the needle at an exact angle worked out with sine and cosine.
    def place_needle(degrees):
        radians = math.radians(degrees)
        canvas.coords(needle , gauge_x , gauge_y , gauge_x + needle_length * math.cos(radians) , gauge_y - needle_length * math.sin(radians))

    # Reads back the angle the needle is pointing at from where it is drawn.
    def needle_now():
        start_x , start_y , tip_x , tip_y = canvas.coords(needle)
        return math.degrees(math.atan2(start_y - tip_y , tip_x - start_x))

    # Turns the needle one step towards the target then books the next step.
    def sweep_needle(target):
        # If the dial no longer exists because the screen changed the sweep is called off.
        if not canvas.winfo_exists():
            return

        # Giving up when a different difficulty was picked stops two sweeps fighting.
        if target != needle_angles[current_difficulty]:
            return

        angle = needle_now()
        gap = target - angle

        # Landing exactly on the target stops the needle overshooting it.
        if abs(gap) <= needle_step:
            place_needle(target)
            return

        if gap > 0:
            place_needle(angle + needle_step)
        else:
            place_needle(angle - needle_step)

        main_screen.after(needle_delay , lambda: sweep_needle(target))

    # Updates the wording and starts the needle sweeping to the new difficulty.
    def show_needle():
        canvas.itemconfig(chosen , text = current_difficulty.upper() + "  -  " + str(points[current_difficulty]) + " POINTS AN ANSWER")
        sweep_needle(needle_angles[current_difficulty])

    # Remembers the difficulty a button stands for and swings the needle to it.
    def pick(level):
        global current_difficulty
        current_difficulty = level
        show_needle()

    easy_button = Button(main_screen , text = "Easy" , font = (font , 11 , "bold") , width = 11 , height = 2 , command = lambda: pick("Easy") , fg = zone_colors["Easy"] , bg = button_color , activebackground = button_active , activeforeground = zone_colors["Easy"] , relief = FLAT)
    canvas.create_window(120 , 520 , anchor = CENTER , window = easy_button)

    medium_button = Button(main_screen , text = "Medium" , font = (font , 11 , "bold") , width = 11 , height = 2 , command = lambda: pick("Medium") , fg = zone_colors["Medium"] , bg = button_color , activebackground = button_active , activeforeground = zone_colors["Medium"] , relief = FLAT)
    canvas.create_window(325 , 520 , anchor = CENTER , window = medium_button)

    hard_button = Button(main_screen , text = "Hard" , font = (font , 11 , "bold") , width = 11 , height = 2 , command = lambda: pick("Hard") , fg = zone_colors["Hard"] , bg = button_color , activebackground = button_active , activeforeground = zone_colors["Hard"] , relief = FLAT)
    canvas.create_window(530 , 520 , anchor = CENTER , window = hard_button)

    back_button = Button(main_screen , text = " Back" , font = (font , 11 , "bold") , image = load_back_image() , compound = LEFT , command = menu_screen , fg = button_text , bg = button_color , activebackground = button_active , relief = FLAT , padx = 8 , pady = 6)
    canvas.create_window(110 , 600 , anchor = CENTER , window = back_button)

    # Sweeping the needle round to the saved difficulty as the screen opens.
    show_needle()

# Settings screen lets the player switch the sound off and set the race length.
def settings_screen():
    clear_screen()

    canvas = build_canvas(background_color)
    draw_heading(canvas , "SETTINGS" , 60 , 38)

    # A card behind the two settings so they read as one group.
    canvas.create_rectangle(settings_left , settings_top , settings_right , settings_bottom , fill = panel_color , outline = panel_edge , width = 2)

    # The sound row, ticked when sound is currently switched on.
    canvas.create_text(280 , sound_row , text = "Sound" , font = (font , 12 , "bold") , fill = dim_text , anchor = E)
    sound_value = IntVar(main_screen , value = int(sound_on))
    sound_check = Checkbutton(main_screen , text = "On" , font = (font , 12 , "bold") , variable = sound_value , fg = text_color , bg = panel_color , activebackground = panel_color , activeforeground = accent , selectcolor = background_color , relief = FLAT)
    canvas.create_window(300 , sound_row , anchor = W , window = sound_check)

    # The theme row, which switches the whole game between dark and light.
    canvas.create_text(280 , theme_row , text = "Theme" , font = (font , 12 , "bold") , fill = dim_text , anchor = E)
    theme_value = StringVar(main_screen , value = current_theme)
    theme_frame = Frame(main_screen , bg = panel_color)
    canvas.create_window(300 , theme_row , anchor = W , window = theme_frame)
    dark_button = Radiobutton(theme_frame , text = "Dark mode" , font = (font , 11 , "bold") , variable = theme_value , value = "Dark" , fg = text_color , bg = panel_color , activebackground = panel_color , activeforeground = accent , selectcolor = background_color , relief = FLAT)
    dark_button.pack(side = LEFT)
    light_button = Radiobutton(theme_frame , text = "Light mode" , font = (font , 11 , "bold") , variable = theme_value , value = "Light" , fg = text_color , bg = panel_color , activebackground = panel_color , activeforeground = accent , selectcolor = background_color , relief = FLAT)
    light_button.pack(side = LEFT , padx = 10)

    # The small text explaining what the theme buttons do.
    canvas.create_text(325 , 350 , text = "Light mode is easier to read in a bright room. Every race is " + str(questions_per_race) + " questions." , font = (font , 9) , fill = dim_text)
    # Saves both settings, then paints the screen again in the chosen theme.
    def save():
        global sound_on , current_theme

        sound_on = sound_value.get() == 1
        current_theme = theme_value.get()
        save_settings()

        apply_theme()
        main_screen.configure(bg = background_color)
        settings_screen()

        show_info("Settings Saved" , "Your settings have been saved and will still be here next time you play.")
    save_button = Button(main_screen , text = "Save" , font = (font , 11 , "bold") , width = 14 , height = 2 , command = save , fg = on_accent , bg = accent , activebackground = accent_deep , relief = FLAT)
    canvas.create_window(450 , 470 , anchor = CENTER , window = save_button)

    back_button = Button(main_screen , text = " Back" , font = (font , 11 , "bold") , image = load_back_image() , compound = LEFT , command = menu_screen , fg = button_text , bg = button_color , activebackground = button_active , relief = FLAT , padx = 8 , pady = 6)
    canvas.create_window(150 , 470 , anchor = CENTER , window = back_button)

# Leaderboard screen shows the best drivers for all three difficulties side by side.
def leaderboard_screen():
    clear_screen()

    canvas = build_canvas(background_color)
    draw_heading(canvas , "LEADERBOARD" , 60 , 38)

    # Drawing one board for each difficulty, side by side across the screen.
    column = 0

    for level in topics:
        left = board_gap + column * (board_width + board_gap)
        right = left + board_width

        # The card the board sits on, headed in that difficulty's colour.
        canvas.create_rectangle(left , board_top , right , board_bottom , fill = panel_color , outline = panel_edge , width = 2)
        canvas.create_text((left + right) / 2 , board_top + 34 , text = level.upper() , font = (title_font , 24) , fill = zone_colors[level])

        # The column headings, which sit above a dividing line.
        canvas.create_text(left + name_offset , board_top + 68 , text = "DRIVER" , font = (font , 9) , fill = dim_text , anchor = W)
        canvas.create_text(left + score_offset , board_top + 68 , text = "PTS" , font = (font , 9) , fill = dim_text , anchor = E)
        canvas.create_text(left + time_offset , board_top + 68 , text = "TIME" , font = (font , 9) , fill = dim_text , anchor = E)
        canvas.create_line(left + 10 , board_top + 82 , right - 10 , board_top + 82 , fill = panel_edge , width = 2)

        rows = best_records(level , leaderboard_rows)

        # An empty board says so rather than leaving a blank card.
        if len(rows) == 0:
            canvas.create_text((left + right) / 2 , row_top + 60 , text = "No races yet" , font = (font , 9) , fill = dim_text)

        place = 0

        for driver , score , seconds in rows:
            y = row_top + place * row_height

            # The driver who is signed in is picked out in the accent colour.
            if driver == current_user:
                row_color = accent
            else:
                row_color = text_color

            canvas.create_text(left + name_offset , y , text = str(place + 1) + "  " + driver , font = (font , 9) , fill = row_color , anchor = W)
            canvas.create_text(left + score_offset , y , text = str(score) , font = (font , 9) , fill = row_color , anchor = E)
            canvas.create_text(left + time_offset , y , text = format_time(seconds) , font = (font , 9) , fill = row_color , anchor = E)
            place = place + 1

        column = column + 1

    # Explaining the ordering, since equal scores are split by the clock.
    canvas.create_text(325 , 578 , text = "Best score first. A tie is settled by the quicker time. Only each driver's best run is shown." , font = (font , 9) , fill = dim_text)

    back_button = Button(main_screen , text = " Back" , font = (font , 11 , "bold") , image = load_back_image() , compound = LEFT , command = menu_screen , fg = button_text , bg = button_color , activebackground = button_active , relief = FLAT , padx = 8 , pady = 6)
    canvas.create_window(110 , 618 , anchor = CENTER , window = back_button)

# Race class shows the questions on a road, checks answers and tracks the score.
class Race:
    # Runs when the class is created and called.
    # Defines all the variables used later in the class and calls show_question.
    def __init__(self , difficulty , username):
        self.difficulty = difficulty
        self.username = username
        self.score = 0
        self.correct = 0
        self.question_no = 0
        self.total = questions_per_race
        self.question = make_question(difficulty)
        self.lane = 1
        self.moving = False
        self.drive_step = gate_speeds[difficulty] // drive_divisor
        self.started = time.time()
        self.taken = 0
        self.show_question()

    # Show_question function draws the road and puts a gate in every lane.
    def show_question(self):
        clear_screen()

        self.canvas = build_canvas(road_color)

        # Painting the solid lines down either kerb of the road.
        self.canvas.create_line(road_edge , road_top , road_edge , road_bottom , fill = edge_color , width = 6)
        self.canvas.create_line(650 - road_edge , road_top , 650 - road_edge , road_bottom , fill = edge_color , width = 6)

        # Painting the dashed lines that divide the three lanes.
        self.lane_lines = []
        for divider in range(1 , lane_count):
            line_x = (lane_x[divider - 1] + lane_x[divider]) / 2
            self.lane_lines.append(self.canvas.create_line(line_x , road_top , line_x , road_bottom , fill = lane_color , width = 4 , dash = lane_dash))

        # The bar across the top holding the question and the score.
        self.canvas.create_rectangle(0 , 0 , 650 , header_bottom , fill = background_color , outline = "")
        self.canvas.create_text(325 , question_y , text = self.question["question"] , font = (font , 15 , "bold") , fill = text_color , width = 600 , justify = CENTER)
        self.scoreboard = self.canvas.create_text(325 , scoreboard_y , text = "" , font = (font , 10 , "bold") , fill = accent)
        self.canvas.create_text(325 , instruction_y , text = driving_help , font = (font , 9) , fill = dim_text)

        # The bar that fills up as the race is worked through.
        self.canvas.create_rectangle(progress_left , progress_top , progress_right , progress_bottom , fill = panel_edge , outline = "")
        filled = progress_left + (progress_right - progress_left) * self.question_no / self.total
        self.canvas.create_rectangle(progress_left , progress_top , filled , progress_bottom , fill = accent , outline = "")

        # The matching bar along the bottom for the back button and the result.
        self.canvas.create_rectangle(0 , road_bottom , 650 , 650 , fill = background_color , outline = "")
        self.feedback = self.canvas.create_text(400 , bottom_row_y , text = "" , font = (font , 10 , "bold") , fill = text_color)

        # Creating the three answer gates from the options of this question.
        options = self.question["options"]
        self.gates = []
        self.gate_texts = []

        for lane in range(lane_count):
            self.gates.append(self.canvas.create_rectangle(lane_x[lane] - gate_width / 2 , gate_y - gate_height / 2 , lane_x[lane] + gate_width / 2 , gate_y + gate_height / 2 , fill = gate_color , outline = lane_color , width = 3))
            self.gate_texts.append(self.canvas.create_text(lane_x[lane] , gate_y , text = options[lane] , font = (font , 21 , "bold") , fill = text_color))

        # Loading the bike picture and keeping a reference so tkinter does not bin it.
        self.bike_img = ImageTk.PhotoImage(Image.open(file_path("Bike.png")).resize((100 , 100)))
        self.bike = self.canvas.create_image(lane_x[self.lane] , bike_y , anchor = CENTER , image = self.bike_img)

        # Lifting the numbers above the bike so the chosen answer stays readable.
        for lane in range(lane_count):
            self.canvas.tag_raise(self.gate_texts[lane])

        back_button = Button(main_screen , text = " Back" , font = (font , 11 , "bold") , image = load_back_image() , compound = LEFT , command = self.leave_race , fg = button_text , bg = button_color , activebackground = button_active , relief = FLAT , padx = 8 , pady = 4)
        self.canvas.create_window(85 , bottom_row_y , anchor = CENTER , window = back_button)

        # Steering with the arrow keys and setting off with space or enter.
        main_screen.bind("<Left>" , self.go_left)
        main_screen.bind("<Right>" , self.go_right)
        main_screen.bind("<space>" , self.submit)
        main_screen.bind("<Return>" , self.submit)
        main_screen.focus_set()

        self.highlight_lane()
        self.show_scoreboard()

    # Refreshes the score line at the top of the road.
    def show_scoreboard(self):
        # The number shown never goes past the total, because the counter has already moved on.
        showing = self.question_no + 1
        if showing > self.total:
            showing = self.total

        accuracy = 0
        if self.question_no > 0:
            accuracy = round(100 * self.correct / self.question_no)

        self.canvas.itemconfig(self.scoreboard , text = self.difficulty.upper() + "    QUESTION " + str(showing) + " OF " + str(self.total) + "    SCORE " + str(self.score) + "    " + str(accuracy) + "% CORRECT")

    # Outlines the gate the bike is lined up with so the choice is obvious.
    def highlight_lane(self):
        for lane in range(lane_count):
            if lane == self.lane:
                self.canvas.itemconfig(self.gates[lane] , outline = accent , width = 5)
            else:
                self.canvas.itemconfig(self.gates[lane] , outline = lane_color , width = 3)

    # Slides the bike one lane to the left.
    def go_left(self , event):
        self.steer(self.lane - 1)

    # Slides the bike one lane to the right.
    def go_right(self , event):
        self.steer(self.lane + 1)

    # Moves the bike into a lane, ignoring the edges of the road.
    def steer(self , lane):
        # Lanes can only be changed before the gates are set moving.
        if self.moving or not self.canvas.winfo_exists():
            return

        if 0 <= lane < lane_count:
            self.lane = lane
            self.canvas.coords(self.bike , lane_x[lane] , bike_y)
            self.highlight_lane()

    # Submit function sets the gates off down the road towards the bike.
    def submit(self , event):
        # Ignoring the key while a run is under way or the race is over stops a double start.
        if self.moving or self.question_no >= self.total or not self.canvas.winfo_exists():
            return

        self.moving = True
        self.drive_down()

    # Drive_down function moves the gates one frame closer every 40 ms.
    def drive_down(self):
        # If the canvas no longer exists because the screen changed the run is called off.
        if not self.canvas.winfo_exists():
            return

        row = self.canvas.coords(self.gate_texts[0])[1] + self.drive_step

        # Shifting the lane markings makes the road look like it is streaming past.
        offset = int(float(self.canvas.itemcget(self.lane_lines[0] , "dashoffset")))
        for line in self.lane_lines:
            self.canvas.itemconfig(line , dashoffset = (offset + self.drive_step) % dash_cycle)

        # Keeping the gates coming until they have pulled up in front of the bike.
        if row < gate_stop_y:
            self.place_gates(row)
            main_screen.after(frame_delay , self.drive_down)
        else:
            self.place_gates(gate_stop_y)
            self.arrive()

    # Lines all three gates up across the road at the given height.
    def place_gates(self , row):
        for lane in range(lane_count):
            self.canvas.coords(self.gate_texts[lane] , lane_x[lane] , row)
            self.canvas.coords(self.gates[lane] , lane_x[lane] - gate_width / 2 , row - gate_height / 2 , lane_x[lane] + gate_width / 2 , row + gate_height / 2)

    # Arrive function marks whichever gate reached the bike and moves the score.
    def arrive(self):
        # Marking twice would count a question that was never asked, so it is ignored.
        if self.question_no >= self.total:
            return

        chosen = self.canvas.itemcget(self.gate_texts[self.lane] , "text")
        right_answer = self.question["answer"]
        self.question_no = self.question_no + 1

        if chosen == right_answer:
            self.correct = self.correct + 1
            self.score = self.score + points[self.difficulty]
            self.canvas.itemconfig(self.feedback , text = "CORRECT" , fill = correct_color)
        else:
            # A wrong answer costs points, but the score never drops below zero.
            self.score = self.score - wrong_penalty
            if self.score < 0:
                self.score = 0

            self.canvas.itemconfig(self.feedback , text = "WRONG, it was " + right_answer , fill = wrong_color)
            self.canvas.itemconfig(self.gates[self.lane] , fill = wrong_color)
            self.canvas.itemconfig(self.gate_texts[self.lane] , fill = on_accent)

        # Colouring the right gate green shows the player where the answer was.
        for lane in range(lane_count):
            if self.canvas.itemcget(self.gate_texts[lane] , "text") == right_answer:
                self.canvas.itemconfig(self.gates[lane] , fill = correct_color)
                self.canvas.itemconfig(self.gate_texts[lane] , fill = on_accent)

        self.show_scoreboard()

        # The message stays up for a moment so the last answer is not swallowed.
        if self.question_no >= self.total:
            self.taken = int(time.time() - self.started)
            main_screen.after(feedback_pause , self.end)
        else:
            main_screen.after(feedback_pause , self.next_question)

    # Puts the next question on the road with a fresh set of gates.
    def next_question(self):
        # If the canvas no longer exists the player has already left the race.
        if not self.canvas.winfo_exists():
            return

        self.question = make_question(self.difficulty)
        self.moving = False
        self.show_question()

    # Leaves the race early and goes back to the menu without saving the run.
    def leave_race(self):
        self.unbind_keys()
        menu_screen()

    # Stops the arrow keys driving a race that is no longer on screen.
    def unbind_keys(self):
        main_screen.unbind("<Left>")
        main_screen.unbind("<Right>")
        main_screen.unbind("<space>")
        main_screen.unbind("<Return>")

    # Shows the results screen with the final score, the four figures and a message.
    def end(self):
        # If the canvas no longer exists the player has already left the race.
        if not self.canvas.winfo_exists():
            return

        self.unbind_keys()
        save_record(self.difficulty , self.username , self.score , self.taken)
        clear_screen()

        accuracy = round(100 * self.correct / self.total)

        canvas = build_canvas(background_color)
        draw_heading(canvas , "RACE COMPLETE" , 70 , 38)

        # A card holding everything the driver earned.
        canvas.create_rectangle(results_left , results_top , results_right , results_bottom , fill = panel_color , outline = panel_edge , width = 2)

        # The score itself, given the most room because it is the headline.
        canvas.create_text(325 , 180 , text = "FINAL SCORE" , font = (font , 9) , fill = dim_text)
        canvas.create_text(325 , 235 , text = str(self.score) , font = (title_font , 64) , fill = accent)

        # Four figures underneath, each with its heading above the number.
        stats = [["DIFFICULTY" , self.difficulty] , ["CORRECT" , str(self.correct) + " of " + str(self.total)] , ["ACCURACY" , str(accuracy) + "%"] , ["TIME" , format_time(self.taken)]]
        column = 0

        for heading , value in stats:
            spot_x = stats_left + column * stats_gap
            canvas.create_text(spot_x , 312 , text = heading , font = (font , 9) , fill = dim_text)
            canvas.create_text(spot_x , 340 , text = value , font = (font , 19 , "bold") , fill = text_color)
            column = column + 1

        # A bar showing the accuracy, so the number has something to sit against.
        canvas.create_rectangle(bar_left , 388 , bar_right , 400 , fill = panel_edge , outline = "")
        canvas.create_rectangle(bar_left , 388 , bar_left + (bar_right - bar_left) * accuracy / 100 , 400 , fill = accent , outline = "")

        # A line of encouragement chosen from how the race actually went.
        canvas.create_text(325 , 435 , text = result_message(accuracy) , font = (font , 12 , "bold") , fill = text_color , width = 460)

        again_button = Button(main_screen , text = "Race Again" , font = (font , 11 , "bold") , width = 16 , height = 2 , command = lambda: start_race(current_difficulty , current_user) , fg = on_accent , bg = accent , activebackground = accent_deep , relief = FLAT)
        canvas.create_window(215 , 540 , anchor = CENTER , window = again_button)

        menu_button = Button(main_screen , text = " Main Menu" , font = (font , 11 , "bold") , image = load_back_image() , compound = LEFT , command = menu_screen , fg = button_text , bg = button_color , activebackground = button_active , relief = FLAT , padx = 10 , pady = 10)
        canvas.create_window(440 , 540 , anchor = CENTER , window = menu_button)

# Function to call the Race class which is called when the play button is pressed.
def start_race(difficulty , username):
    Race(difficulty , username)

# Scrambles a password together with its salt, so the real password is never saved.
def hash_password(password , salt):
    return hashlib.sha256((salt + password).encode()).hexdigest()

# Reads every saved account out of the text file into a dictionary.
def load_accounts():
    accounts = {}

    try:
        with open(file_path("accounts.txt") , "r") as file:
            for line in file:
                # Splitting each line into the username, the salt and the scrambled password.
                parts = line.strip().split(",")

                # Ignoring a damaged row stops one bad line breaking the whole load.
                if len(parts) == 3 and parts[0] != "" and parts[1] != "" and parts[2] != "":
                    accounts[parts[0]] = (parts[1] , parts[2])
    except FileNotFoundError:
        pass

    return accounts

# Adds one new account onto the end of the accounts file.
def save_account(username , password):
    salt = secrets.token_hex(8)

    with open(file_path("accounts.txt") , "a") as file:
        file.write(username + "," + salt + "," + hash_password(password , salt) + "\n")

# Saves one finished race onto the end of the records file.
def save_record(difficulty , username , score , seconds):
    with open(file_path("records.txt") , "a") as file:
        file.write(difficulty + "," + str(username) + "," + str(score) + "," + str(seconds) + "\n")

# Returns the best runs for one difficulty, one row per driver.
def best_records(difficulty , how_many):
    best = {}

    try:
        with open(file_path("records.txt") , "r") as file:
            for line in file:
                parts = line.strip().split(",")

                # A row is only trusted when the level is real and both numbers are numbers.
                if len(parts) != 4:
                    continue

                if parts[0] != difficulty or parts[1] == "":
                    continue

                if not parts[2].isdigit() or not parts[3].isdigit():
                    continue

                driver = parts[1]
                score = int(parts[2])
                seconds = int(parts[3])

                # Only a driver's best run is kept so nobody can fill the whole board.
                if driver not in best or score > best[driver][0] or (score == best[driver][0] and seconds < best[driver][1]):
                    best[driver] = [score , seconds]
    except FileNotFoundError:
        pass

    rows = []
    for driver in best:
        rows.append([driver , best[driver][0] , best[driver][1]])

    # Sorting by highest score first, then by the quicker time for a tie.
    def get_score(player):
        return (-player[1] , player[2])

    rows.sort(key = get_score)
    return rows[:how_many]

# Reads the saved settings, ignoring any value that is missing or damaged.
def load_settings():
    global sound_on , current_theme

    try:
        with open(file_path("settings.txt") , "r") as file:
            for line in file:
                # Every line is stored as name=value, for example questions=20.
                parts = line.strip().split("=")

                if len(parts) != 2:
                    continue

                if parts[0] == "sound" and parts[1] in ["on" , "off"]:
                    sound_on = parts[1] == "on"

                if parts[0] == "theme" and parts[1] in ["Dark" , "Light"]:
                    current_theme = parts[1]
    except FileNotFoundError:
        pass

# Writes both settings back out, replacing whatever was there before.
def save_settings():
    if sound_on:
        sound_value = "on"
    else:
        sound_value = "off"

    with open(file_path("settings.txt") , "w") as file:
        file.write("sound=" + sound_value + "\n")
        file.write("theme=" + current_theme + "\n")

# Function to clear widgets off the window before creating new ones when the screen changes.
def clear_screen():
    for widget in main_screen.winfo_children():
        widget.destroy()

# Function to close the program when the exit buttons are pressed.
def close_program():
    if messagebox.askyesno("Exit" , "Are you sure you want to quit?"):
        main_screen.destroy()

# Reading the saved settings first, so the chosen theme is painted from the start.
load_settings()
apply_theme()

main_screen = Tk()
main_screen.geometry("700x700")
main_screen.title("Math Racer")
main_screen.configure(bg = background_color)
main_screen.resizable(False , False)

# Calling main()
main()

main_screen.mainloop()
