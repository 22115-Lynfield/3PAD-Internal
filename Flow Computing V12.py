# Author: Maurya Patel
# Date: 03/09/2026
# Purpose: Maths Racing Game

# Racing colour scheme.
background_color = "#12141c"
panel_color = "#1c2030"
panel_edge = "#2e3446"
shadow_color = "#05060a"
text_color = "#f2f4f8"
dim_text = "#9aa1b4"
button_color = "#2a3040"
button_text = "#f2f4f8"
button_active = "#3b435a"
accent = "#ffd23f"
accent_deep = "#e0a800"

# Colours used on the race track.
road_color = "#262a35"
lane_color = "#e9ecf3"
edge_color = "#4a5163"
gate_color = "#12141c"
correct_color = "#4ade80"
wrong_color = "#f87171"

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
sound_on = True
questions_per_race = 10

# The rules a username and a password have to follow.
username_min = 3
username_max = 12
password_min = 5

# The smallest and largest number of questions a race can be set to.
questions_min = 5
questions_max = 50

# The pitch and length of the beep that plays when an error box appears.
beep_hertz = 700
beep_milliseconds = 150

# Points won for a right answer at each difficulty, so harder is worth more.
points = {"Easy": 10 , "Medium": 20 , "Hard": 30}

# Points taken off for a wrong answer, whatever the difficulty.
wrong_penalty = 5

# The speed shown on the dial for each difficulty.
speeds = {"Easy": 20 , "Medium": 30 , "Hard": 40}

# The colour of each band on the dial.
zone_colors = {"Easy": "#3ddc84" , "Medium": "#ffb020" , "Hard": "#ff5c5c"}

# The angle the needle points to for each difficulty.
needle_angles = {"Easy": 150 , "Medium": 90 , "Hard": 30}

# The planet style name shown for each difficulty.
challenge_names = {"Easy": "Learner" , "Medium": "Rider" , "Hard": "Racer"}

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

# How long the screen waits between frames and how dial speed becomes pixels.
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

# Returns the full path of a saved file so it always sits beside this program.
def file_path(name):
    return os.path.join(os.path.dirname(__file__) , name)

# Draws the yellow title with its drop shadow on a small canvas at the top.
def draw_title(words , size , height):
    banner = Canvas(main_screen , width = 650 , height = height , bg = background_color , highlightthickness = 0)
    banner.pack()
    banner.create_text(328 , height / 2 + 4 , text = words , font = (title_font , size) , fill = shadow_color)
    banner.create_text(325 , height / 2 , text = words , font = (title_font , size) , fill = accent)
    return banner

# Creating the start up screen with login and sign up buttons.
def main():
    clear_screen()

    draw_title("MATH RACER" , 58 , 130)

    subtitle = Label(main_screen , text = "Answer the maths to accelerate the bike" , fg = dim_text , bg = background_color , font = (font , 11))
    subtitle.pack(pady = (0 , 10))

    login_button = Button(main_screen , text = "Login" , fg = button_text , bg = button_color , activebackground = button_active , command = login_screen , font = (font , 15) , width = 20 , height = 2)
    login_button.pack(pady = 25)

    signup_button = Button(main_screen , text = "Signup" , fg = button_text , bg = button_color , activebackground = button_active , command = signup_screen , font = (font , 15) , width = 20 , height = 2)
    signup_button.pack(pady = 15)

    close_button = Button(main_screen , text = "Exit" , fg = button_text , bg = button_color , activebackground = button_active , command = close_program , font = (font , 15) , width = 10 , height = 1)
    close_button.pack(pady = 20)

# Signup screen function displays signup entry boxes allowing user to create a new account.
# This is called when user presses sign up button on start up screen.
def signup_screen():
    clear_screen()

    # Global variables for the entry fields so they can be read by the signup function.
    global username_entry , password_entry , con_password_entry

    draw_title("SIGN UP" , 38 , 100)

    username_label = Label(main_screen , text = "Enter desired username" , fg = text_color , bg = background_color , font = (font , 12 , "bold"))
    username_label.pack(pady = (20 , 0))
    username_entry = Entry(main_screen , width = 40 , bg = panel_color , fg = text_color , insertbackground = accent , relief = FLAT)
    username_entry.pack()

    password_label = Label(main_screen , text = "Create a new password" , fg = text_color , bg = background_color , font = (font , 12 , "bold"))
    password_label.pack(pady = (20 , 0))
    password_entry = Entry(main_screen , width = 40 , show = "*" , bg = panel_color , fg = text_color , insertbackground = accent , relief = FLAT)
    password_entry.pack()

    # Function for show password button to switch between hidden * and visible.
    def show_password():
        if password_entry.cget("show") == "*":
            password_entry.config(show = "")
            show_button.config(text = "Hide Password")
        else:
            password_entry.config(show = "*")
            show_button.config(text = "Show Password")

    show_button = Button(main_screen , text = "Show Password" , fg = button_text , bg = button_color , activebackground = button_active , command = show_password)
    show_button.pack(pady = 5)

    con_password_label = Label(main_screen , text = "Confirm password" , fg = text_color , bg = background_color , font = (font , 12 , "bold"))
    con_password_label.pack(pady = (15 , 0))
    con_password_entry = Entry(main_screen , width = 40 , show = "*" , bg = panel_color , fg = text_color , insertbackground = accent , relief = FLAT)
    con_password_entry.pack()

    rules_label = Label(main_screen , text = "Your password must be at least " + str(password_min) + " characters long, and include at least 1 number and 1 capital letter." , fg = dim_text , bg = background_color , font = (font , 9) , wraplength = 420)
    rules_label.pack(pady = 15)

    sign_up_but = Button(main_screen , text = "Sign Up" , fg = background_color , bg = accent , activebackground = accent_deep , command = signup , font = (font , 12 , "bold") , width = 20 , height = 2)
    sign_up_but.pack(pady = 10)

    back_but = Button(main_screen , text = "Back" , fg = button_text , bg = button_color , activebackground = button_active , command = main , font = (font , 12 , "bold") , width = 10 , height = 1)
    back_but.pack()

# Function checks the fields on the signup screen and creates the account.
def signup():
    # Reading the global entry fields from the signup screen above.
    username = username_entry.get()
    password = password_entry.get()
    con_password = con_password_entry.get()

    # Validating every field and showing an error box saying how to fix it.
    if username == "" or password == "" or con_password == "":
        show_error("Error" , "Please fill all fields")
        return

    if len(username) < username_min:
        show_error("Error" , "Your username is only " + str(len(username)) + " characters long. Please make it at least " + str(username_min) + " characters.")
        return

    if len(username) > username_max:
        show_error("Error" , "Your username is " + str(len(username)) + " characters long, which is too long. Please shorten it to " + str(username_max) + " characters or fewer.")
        return

    if " " in username:
        show_error("Error" , "Your username has a space in it. Please use an underscore instead, for example math_racer.")
        return

    if "," in username:
        show_error("Error" , "Username cannot contain commas.")
        return

    if len(password) < password_min:
        show_error("Error" , "Your password is only " + str(len(password)) + " characters long. Please make it at least " + str(password_min) + " characters.")
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
        show_error("Error" , "Your password does not contain a number. Please add at least 1 number, for example 4 or 9.")
        return

    if not has_capital:
        show_error("Error" , "Your password does not contain a capital letter. Please add at least 1 capital letter, for example A or M.")
        return

    if "," in password:
        show_error("Error" , "Password cannot contain commas.")
        return

    if password != con_password:
        show_error("Error" , "Passwords do not match!")
        return

    # Setting a filepath for the account details text file to be placed.
    # The file path will create the file in the same folder that the code is in.
    filepath = file_path("accounts.txt")

    # Using a try and except block lets the code open the file if it exists and carry on if it does not.
    try:
        with open(filepath , "r") as file:
            # This for loop goes through every line and splits the details apart with a comma.
            for line in file:
                stored_user , stored_salt , stored_hash = line.strip().split(",")
                # Checking if the username already exists in the file.
                if stored_user == username:
                    show_error("Error" , "Username already exists")
                    return
    except FileNotFoundError:
        pass

    # A random salt is saved with the scrambled password so the real password is never stored.
    salt = secrets.token_hex(8)
    scrambled = hashlib.sha256((salt + password).encode()).hexdigest()

    with open(filepath , "a") as file:
        file.write(f"{username},{salt},{scrambled}\n")

    show_info("Success" , "Account created!")

    main()

# Login screen function displays entry fields and buttons for the login screen.
def login_screen():
    clear_screen()

    # Global variables for the login entry fields so the login function can read them.
    global login_username , login_password

    draw_title("LOGIN" , 38 , 110)

    username_label = Label(main_screen , text = "Enter username" , fg = text_color , bg = background_color , font = (font , 10 , "bold"))
    username_label.pack(pady = (30 , 0))
    login_username = Entry(main_screen , width = 30 , bg = panel_color , fg = text_color , insertbackground = accent , relief = FLAT)
    login_username.pack()

    password_label = Label(main_screen , text = "Enter password" , fg = text_color , bg = background_color , font = (font , 10 , "bold"))
    password_label.pack(pady = (20 , 0))
    login_password = Entry(main_screen , width = 30 , show = "*" , bg = panel_color , fg = text_color , insertbackground = accent , relief = FLAT)
    login_password.pack()

    # Function for show password button to switch between hidden * and visible.
    def show_password():
        if login_password.cget("show") == "*":
            login_password.config(show = "")
            show_button.config(text = "Hide Password")
        else:
            login_password.config(show = "*")
            show_button.config(text = "Show Password")

    show_button = Button(main_screen , text = "Show Password" , fg = button_text , bg = button_color , activebackground = button_active , command = show_password)
    show_button.pack(pady = 10)

    login_but = Button(main_screen , text = "Login" , fg = background_color , bg = accent , activebackground = accent_deep , command = login , font = (font , 10 , "bold") , width = 20 , height = 2)
    login_but.pack(pady = 25)

    back_but = Button(main_screen , text = "Back" , fg = button_text , bg = button_color , activebackground = button_active , command = main , font = (font , 10 , "bold") , width = 10 , height = 1)
    back_but.pack()

# Login function checks the username and password against accounts.txt then opens the menu.
def login():
    # Define the global current_user so the leaderboard and the race know who is playing.
    global current_user
    username = login_username.get()
    password = login_password.get()

    if username == "":
        show_error("Error" , "You have not typed a username. Please type the username you signed up with.")
        return

    if password == "":
        show_error("Error" , "You have not typed a password. Please type the password you signed up with.")
        return

    filepath = file_path("accounts.txt")

    try:
        with open(filepath , "r") as file:
            for line in file:
                stored_user , stored_salt , stored_hash = line.strip().split(",")

                # The typed password is scrambled the same way and the two are compared.
                scrambled = hashlib.sha256((stored_salt + password).encode()).hexdigest()

                if username == stored_user and scrambled == stored_hash:
                    current_user = username
                    show_info("Success" , "Login successful!")
                    menu_screen()
                    return

        show_error("Error" , "Invalid username or password")

    except FileNotFoundError:
        show_error("Error" , "No users registered")

# Menu screen function displays the play, difficulty, settings and leaderboard buttons.
def menu_screen():
    clear_screen()

    draw_title("MATH RACER" , 58 , 130)

    rule = Canvas(main_screen , width = 400 , height = 4 , bg = panel_edge , highlightthickness = 0)
    rule.pack()

    signed_in = Label(main_screen , text = f"Signed in as {current_user}" , fg = dim_text , bg = background_color , font = (font , 10))
    signed_in.pack(pady = (10 , 20))

    play_btn = Button(main_screen , text = "PLAY" , fg = background_color , bg = accent , activebackground = accent_deep , command = lambda: start_race(current_difficulty , current_user) , font = (font , 16 , "bold") , width = 18 , height = 2)
    play_btn.pack(pady = 10)

    top_frame = Frame(main_screen , bg = background_color)
    top_frame.pack(pady = 15)

    difficulty_btn = Button(top_frame , text = "Difficulty" , fg = button_text , bg = button_color , activebackground = button_active , command = difficulty_screen , font = (font , 11 , "bold") , width = 15 , height = 2)
    difficulty_btn.pack(side = LEFT , padx = 12)

    settings_btn = Button(top_frame , text = "Settings" , fg = button_text , bg = button_color , activebackground = button_active , command = settings_screen , font = (font , 11 , "bold") , width = 15 , height = 2)
    settings_btn.pack(side = RIGHT , padx = 12)

    leaderboard_btn = Button(main_screen , text = "🏆 Leaderboard" , fg = button_text , bg = button_color , activebackground = button_active , command = leaderboard_screen , font = (font , 11 , "bold") , width = 34 , height = 2)
    leaderboard_btn.pack(pady = 5)

    bottom_frame = Frame(main_screen , bg = background_color)
    bottom_frame.pack(pady = 20)

    logout_btn = Button(bottom_frame , text = "Log Out" , fg = button_text , bg = button_color , activebackground = button_active , command = main , font = (font , 11) , width = 15 , height = 2)
    logout_btn.pack(side = LEFT , padx = 12)

    close_button = Button(bottom_frame , text = "Exit" , fg = button_text , bg = button_color , activebackground = button_active , command = close_program , font = (font , 11) , width = 15 , height = 2)
    close_button.pack(side = RIGHT , padx = 12)

# Difficulty screen shows a speedometer whose needle sweeps to the chosen level.
def difficulty_screen():
    clear_screen()

    draw_title("DIFFICULTY" , 38 , 100)

    dial = Canvas(main_screen , width = 650 , height = 400 , bg = background_color , highlightthickness = 0)
    dial.pack()

    # The square the gauge is drawn inside, worked out from its centre and radius.
    dial_x = 325
    dial_y = 260
    box = (dial_x - gauge_radius , dial_y - gauge_radius , dial_x + gauge_radius , dial_y + gauge_radius)

    # Drawing a coloured band for each difficulty, each one a third of the dial.
    dial.create_arc(box , start = 120 , extent = 60 , style = ARC , width = gauge_band , outline = zone_colors["Easy"])
    dial.create_arc(box , start = 60 , extent = 60 , style = ARC , width = gauge_band , outline = zone_colors["Medium"])
    dial.create_arc(box , start = 0 , extent = 60 , style = ARC , width = gauge_band , outline = zone_colors["Hard"])

    # Naming every band and printing its real speed underneath the name.
    dial.create_text(132 , 147 , text = "EASY" , font = (title_font , 24) , fill = zone_colors["Easy"] , anchor = E)
    dial.create_text(132 , 171 , text = "Speed " + str(speeds["Easy"]) , font = (font , 9) , fill = dim_text , anchor = E)
    dial.create_text(325 , 31 , text = "MEDIUM" , font = (title_font , 24) , fill = zone_colors["Medium"] , anchor = S)
    dial.create_text(325 , 55 , text = "Speed " + str(speeds["Medium"]) , font = (font , 9) , fill = dim_text , anchor = S)
    dial.create_text(518 , 147 , text = "HARD" , font = (title_font , 24) , fill = zone_colors["Hard"] , anchor = W)
    dial.create_text(518 , 171 , text = "Speed " + str(speeds["Hard"]) , font = (font , 9) , fill = dim_text , anchor = W)

    # The needle starts pointing straight up and is swung round by sweep_needle.
    needle = dial.create_line(dial_x , dial_y , dial_x , dial_y - needle_length , width = 6 , fill = text_color , arrow = LAST , arrowshape = (18 , 22 , 7))
    dial.create_oval(dial_x - 15 , dial_y - 15 , dial_x + 15 , dial_y + 15 , fill = panel_color , outline = text_color , width = 3)

    chosen_label = Label(main_screen , text = "" , fg = text_color , bg = background_color , font = (font , 15 , "bold"))
    chosen_label.pack(pady = 5)

    # Puts the needle at an exact angle worked out with sine and cosine.
    def place_needle(degrees):
        radians = math.radians(degrees)
        dial.coords(needle , dial_x , dial_y , dial_x + needle_length * math.cos(radians) , dial_y - needle_length * math.sin(radians))

    # Reads back the angle the needle is pointing at from where it is drawn.
    def needle_now():
        start_x , start_y , tip_x , tip_y = dial.coords(needle)
        return math.degrees(math.atan2(start_y - tip_y , tip_x - start_x))

    # Turns the needle one step towards the target then books the next step.
    def sweep_needle(target):
        # If the dial no longer exists because the screen changed the sweep is called off.
        if not dial.winfo_exists():
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
        chosen_label.config(text = f"{current_difficulty.upper()}  -  SPEED {speeds[current_difficulty]}")
        sweep_needle(needle_angles[current_difficulty])

    # Remembers the difficulty a button stands for and swings the needle to it.
    def pick(level):
        global current_difficulty
        current_difficulty = level
        show_needle()

    button_frame = Frame(main_screen , bg = background_color)
    button_frame.pack(pady = 10)

    easy_btn = Button(button_frame , text = "Easy" , fg = zone_colors["Easy"] , bg = button_color , activebackground = button_active , command = lambda: pick("Easy") , font = (font , 11 , "bold") , width = 11 , height = 2)
    easy_btn.pack(side = LEFT , padx = 15)

    medium_btn = Button(button_frame , text = "Medium" , fg = zone_colors["Medium"] , bg = button_color , activebackground = button_active , command = lambda: pick("Medium") , font = (font , 11 , "bold") , width = 11 , height = 2)
    medium_btn.pack(side = LEFT , padx = 15)

    hard_btn = Button(button_frame , text = "Hard" , fg = zone_colors["Hard"] , bg = button_color , activebackground = button_active , command = lambda: pick("Hard") , font = (font , 11 , "bold") , width = 11 , height = 2)
    hard_btn.pack(side = LEFT , padx = 15)

    back_but = Button(main_screen , text = "Back" , fg = button_text , bg = button_color , activebackground = button_active , command = menu_screen , font = (font , 11 , "bold") , width = 10 , height = 1)
    back_but.pack(pady = 10)

    # Sweeping the needle round to the saved difficulty as the screen opens.
    show_needle()

# Settings screen lets the player switch the sound off and set the race length.
def settings_screen():
    clear_screen()

    draw_title("SETTINGS" , 38 , 110)

    panel = Frame(main_screen , bg = panel_color , highlightbackground = panel_edge , highlightthickness = 2)
    panel.pack(pady = 30 , padx = 90 , fill = "x")

    sound_value = IntVar(main_screen , value = int(sound_on))

    sound_row = Frame(panel , bg = panel_color)
    sound_row.pack(pady = 25)
    sound_label = Label(sound_row , text = "Sound" , fg = dim_text , bg = panel_color , font = (font , 12 , "bold") , width = 18 , anchor = E)
    sound_label.pack(side = LEFT)
    sound_check = Checkbutton(sound_row , text = "On" , variable = sound_value , fg = text_color , bg = panel_color , activebackground = panel_color , activeforeground = accent , selectcolor = background_color , font = (font , 12 , "bold"))
    sound_check.pack(side = LEFT , padx = 10)

    questions_row = Frame(panel , bg = panel_color)
    questions_row.pack(pady = 5)
    questions_label = Label(questions_row , text = "Questions per race" , fg = dim_text , bg = panel_color , font = (font , 12 , "bold") , width = 18 , anchor = E)
    questions_label.pack(side = LEFT)
    questions_entry = Entry(questions_row , width = 6 , bg = background_color , fg = text_color , insertbackground = accent , relief = FLAT , font = (font , 13))
    questions_entry.pack(side = LEFT , padx = 10)
    questions_entry.insert(0 , str(questions_per_race))

    rule_label = Label(panel , text = "Choose a whole number between " + str(questions_min) + " and " + str(questions_max) + "." , fg = dim_text , bg = panel_color , font = (font , 9))
    rule_label.pack(pady = 20)

    # Checks the typed box then saves both settings to the settings file.
    def save():
        global sound_on , questions_per_race

        typed = questions_entry.get()

        if typed == "":
            show_error("Cannot Save Settings" , "You have not typed how many questions each race should have. Please type a whole number between " + str(questions_min) + " and " + str(questions_max) + ".")
            return

        # Checking every character rejects decimals, minus signs, spaces and symbols.
        for letter in typed:
            if letter not in "0123456789":
                show_error("Cannot Save Settings" , "Questions per race must be a whole number, but you typed " + typed + ". Please use digits only, for example 10.")
                return

        if int(typed) < questions_min:
            show_error("Cannot Save Settings" , "A race of " + typed + " questions is too short. Please choose at least " + str(questions_min) + ".")
            return

        if int(typed) > questions_max:
            show_error("Cannot Save Settings" , "A race of " + typed + " questions is too long. Please choose " + str(questions_max) + " or fewer.")
            return

        sound_on = sound_value.get() == 1
        questions_per_race = int(typed)
        save_settings()

        show_info("Settings Saved" , "Your settings have been saved and will still be here next time you play.")

    button_frame = Frame(main_screen , bg = background_color)
    button_frame.pack(pady = 30)

    back_but = Button(button_frame , text = "Back" , fg = button_text , bg = button_color , activebackground = button_active , command = menu_screen , font = (font , 11 , "bold") , width = 12 , height = 2)
    back_but.pack(side = LEFT , padx = 20)

    save_btn = Button(button_frame , text = "Save" , fg = background_color , bg = accent , activebackground = accent_deep , command = save , font = (font , 11 , "bold") , width = 12 , height = 2)
    save_btn.pack(side = LEFT , padx = 20)

# Leaderboard screen shows the best drivers for all three difficulties side by side.
def leaderboard_screen():
    clear_screen()

    draw_title("🏆 LEADERBOARD 🏆" , 30 , 100)

    boards_frame = Frame(main_screen , bg = background_color)
    boards_frame.pack(pady = 10)

    for level in ["Easy" , "Medium" , "Hard"]:
        board = Frame(boards_frame , bg = panel_color , highlightbackground = panel_edge , highlightthickness = 2 , width = 200 , height = 400)
        board.pack(side = LEFT , padx = 8)
        board.pack_propagate(False)

        Label(board , text = level.upper() , fg = zone_colors[level] , bg = panel_color , font = (title_font , 24)).pack(pady = 10)
        Label(board , text = "DRIVER          PTS   TIME" , fg = dim_text , bg = panel_color , font = (font , 8 , "bold")).pack()

        rows = best_records(level , 10)

        # An empty board says so rather than leaving a blank card.
        if len(rows) == 0:
            Label(board , text = "No races yet" , fg = dim_text , bg = panel_color , font = (font , 9)).pack(pady = 40)

        rank = 1

        for driver , score , seconds in rows:
            if rank == 1:
                medal = "🥇"
            elif rank == 2:
                medal = "🥈"
            elif rank == 3:
                medal = "🥉"
            else:
                medal = str(rank)

            # The driver who is signed in is picked out in the accent colour.
            if driver == current_user:
                row_color = accent
            else:
                row_color = text_color

            Label(board , text = f"{medal:<3}{driver:<11}{score:<5}{format_time(seconds)}" , fg = row_color , bg = panel_color , font = (font , 9)).pack(pady = 2)
            rank = rank + 1

    note = Label(main_screen , text = "Best score first. A tie is settled by the quicker time. Only each driver's best run is shown." , fg = dim_text , bg = background_color , font = (font , 9) , wraplength = 600)
    note.pack(pady = 15)

    back_but = Button(main_screen , text = "Back" , fg = button_text , bg = button_color , activebackground = button_active , command = menu_screen , font = (font , 11 , "bold") , width = 12 , height = 2)
    back_but.pack()

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
        self.drive_step = speeds[difficulty] // drive_divisor
        self.started = time.time()
        self.taken = 0
        self.show_question()

    # Show_question function draws the road and puts a gate in every lane.
    def show_question(self):
        clear_screen()

        self.canvas = Canvas(main_screen , width = 650 , height = 650 , bg = road_color , highlightthickness = 0)
        self.canvas.pack(pady = 5)

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

        back_but = Button(main_screen , text = "Back" , fg = button_text , bg = button_color , activebackground = button_active , command = self.leave_race , font = (font , 10 , "bold") , width = 10 , height = 1)
        self.canvas.create_window(85 , bottom_row_y , anchor = CENTER , window = back_but)

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
        accuracy = 0
        if self.question_no > 0:
            accuracy = round(100 * self.correct / self.question_no)

        self.canvas.itemconfig(self.scoreboard , text = f"{self.difficulty.upper()}    QUESTION {self.question_no + 1} OF {self.total}    SCORE {self.score}    {accuracy}% CORRECT")

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
        # Ignoring the key while a run is already under way stops a double start.
        if self.moving or not self.canvas.winfo_exists():
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
        chosen = self.canvas.itemcget(self.gate_texts[self.lane] , "text")
        right_answer = self.question["answer"]
        self.question_no += 1

        if chosen == right_answer:
            self.correct += 1
            self.score += points[self.difficulty]
            self.canvas.itemconfig(self.feedback , text = "CORRECT" , fill = correct_color)
        else:
            # A wrong answer costs points, but the score never drops below zero.
            self.score -= wrong_penalty
            if self.score < 0:
                self.score = 0

            self.canvas.itemconfig(self.feedback , text = "WRONG, it was " + right_answer , fill = wrong_color)
            self.canvas.itemconfig(self.gates[self.lane] , fill = wrong_color)
            self.canvas.itemconfig(self.gate_texts[self.lane] , fill = background_color)

        # Colouring the right gate green shows the player where the answer was.
        for lane in range(lane_count):
            if self.canvas.itemcget(self.gate_texts[lane] , "text") == right_answer:
                self.canvas.itemconfig(self.gates[lane] , fill = correct_color)
                self.canvas.itemconfig(self.gate_texts[lane] , fill = background_color)

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

    # Shows the end screen with the final score, accuracy, rating and menu button.
    def end(self):
        # If the canvas no longer exists the player has already left the race.
        if not self.canvas.winfo_exists():
            return

        self.unbind_keys()
        save_record(self.difficulty , self.username , self.score , self.taken)
        clear_screen()

        accuracy = round(100 * self.correct / self.total)

        if accuracy == 100:
            rating = "🏆 Maths Master!"
        elif accuracy >= 80:
            rating = "🌟 Excellent!"
        elif accuracy >= 60:
            rating = "👍 Great Job!"
        elif accuracy >= 40:
            rating = "🙂 Good Effort!"
        else:
            rating = "📚 Keep Practising!"

        draw_title("RACE COMPLETE" , 38 , 110)

        Label(main_screen , text = "FINAL SCORE" , fg = dim_text , bg = background_color , font = (font , 9)).pack(pady = (20 , 0))
        Label(main_screen , text = str(self.score) , fg = accent , bg = background_color , font = (title_font , 64)).pack()
        Label(main_screen , text = rating , fg = "gold" , bg = background_color , font = (font , 20 , "bold")).pack(pady = 10)
        Label(main_screen , text = f"{self.username} scored {self.correct} out of {self.total} on {self.difficulty}" , fg = text_color , bg = background_color , font = (font , 14)).pack(pady = 5)
        Label(main_screen , text = f"Accuracy: {accuracy}%          Time: {format_time(self.taken)}" , fg = text_color , bg = background_color , font = (font , 14)).pack(pady = 5)
        Label(main_screen , text = result_message(accuracy) , fg = dim_text , bg = background_color , font = (font , 11) , wraplength = 460).pack(pady = 15)

        button_frame = Frame(main_screen , bg = background_color)
        button_frame.pack(pady = 20)

        again_btn = Button(button_frame , text = "Race Again" , fg = background_color , bg = accent , activebackground = accent_deep , command = lambda: start_race(current_difficulty , current_user) , font = (font , 11 , "bold") , width = 16 , height = 2)
        again_btn.pack(side = LEFT , padx = 15)

        menu_btn = Button(button_frame , text = "Main Menu" , fg = button_text , bg = button_color , activebackground = button_active , command = menu_screen , font = (font , 11 , "bold") , width = 16 , height = 2)
        menu_btn.pack(side = LEFT , padx = 15)

# Function to call the Race class which is called when the play button is pressed.
def start_race(difficulty , username):
    Race(difficulty , username)

# Saves one finished race onto the end of the records file.
def save_record(difficulty , username , score , seconds):
    with open(file_path("records.txt") , "a") as file:
        file.write(f"{difficulty},{username},{score},{seconds}\n")

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
    global sound_on , questions_per_race

    try:
        with open(file_path("settings.txt") , "r") as file:
            for line in file:
                # Every line is stored as name=value, for example questions=20.
                parts = line.strip().split("=")

                if len(parts) != 2:
                    continue

                if parts[0] == "sound" and parts[1] in ["on" , "off"]:
                    sound_on = parts[1] == "on"

                if parts[0] == "questions" and parts[1].isdigit():
                    if questions_min <= int(parts[1]) <= questions_max:
                        questions_per_race = int(parts[1])
    except FileNotFoundError:
        pass

# Writes both settings back out, replacing whatever was there before.
def save_settings():
    if sound_on:
        sound_value = "on"
    else:
        sound_value = "off"

    with open(file_path("settings.txt") , "w") as file:
        file.write(f"sound={sound_value}\n")
        file.write(f"questions={questions_per_race}\n")

# Function to clear widgets off the window before creating new ones when the screen changes.
def clear_screen():
    for widget in main_screen.winfo_children():
        widget.destroy()

# Function to close the program when the exit buttons are pressed.
def close_program():
    if messagebox.askyesno("Exit" , "Are you sure you want to quit?"):
        main_screen.destroy()

main_screen = Tk()
main_screen.geometry("700x700")
main_screen.title("Math Racer")
main_screen.configure(bg = background_color)
main_screen.resizable(False , False)

# Reading the saved settings before the first screen is shown.
load_settings()

# Calling main()
main()

main_screen.mainloop()
