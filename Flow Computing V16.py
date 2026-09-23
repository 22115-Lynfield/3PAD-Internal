# Author: Maurya Patel.
# Date: 09/09/2026.
# Purpose: A maths racing game where the questions are the accelerator.

# Racing colour scheme for the dark theme.
DARK_COLOURS = {
    "background": "#12141c" ,
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
    "gate": "#12141c" ,
    "correct": "#4ade80" ,
    "wrong": "#f87171" ,
    "pad": "#f7f8fb" ,
    "pad_ink": "#12141c" ,
    "easy": "#3ddc84" ,
    "medium": "#ffb020" ,
    "hard": "#ff5c5c"
}

# The same colours again for the light theme, dark writing on a pale background.
LIGHT_COLOURS = {
    "background": "#f2f4f8" ,
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
    "gate": "#ffffff" ,
    "correct": "#2fa860" ,
    "wrong": "#d64545" ,
    "pad": "#ffffff" ,
    "pad_ink": "#12141c" ,
    "easy": "#1f9d55" ,
    "medium": "#c47f00" ,
    "hard": "#d64545"
}

TITLE_FONT = "Impact"
FONT = "Segoe UI"
EMOJI_FONT = "Segoe UI Emoji"

# The sizes used again and again, named once so every screen matches.
HEAD_FONT = (TITLE_FONT , 38)
BTN_FONT = (FONT , 11 , "bold")
LABEL_FONT = (FONT , 12 , "bold")
TOOL_FONT = (FONT , 10 , "bold")
SMALL_FONT = (FONT , 9)
ENTRY_FONT = (FONT , 13)

# Importing tkinter library and other important components from tkinter and python.
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import os
import random
import math
from PIL import Image , ImageTk

# The FOLDER this program is saved in, so the text files always sit beside it.
FOLDER = os.path.dirname(__file__)

# Setting global variables for use later on.
current_user = None
current_level = "Easy"
current_theme = "Dark"
answer_mode = "Gates"

# The rules a username and a password have to follow.
USERNAME_MIN = 3
USERNAME_MAX = 12
PASSWORD_MIN = 5

# Every race is the same length, whatever difficulty is being played.
RACE_LENGTH = 10

# Points won for a right answer at each difficulty, so harder is worth more.
POINTS = {"Easy": 10 , "Medium": 20 , "Hard": 30}

# Points taken off for a wrong answer, whatever the difficulty.
PENALTY = 5

# How fast the gates run down the road, so a harder race gives less time to choose.
SPEEDS = {"Easy": 20 , "Medium": 30 , "Hard": 40}

# The angle the needle POINTS to for each difficulty.
ANGLES = {"Easy": 150 , "Medium": 90 , "Hard": 30}

# How many drivers each leaderboard shows.
BOARD_ROWS = 10

# Creating a dictionary of race questions with a sub list of question, options and answers for each difficulty.
RACE_QUESTIONS = {
    "Easy": [
        {"question": "What is 27 + 46?" , "options": ["63" , "73" , "83"] , "answer": "73"} ,
        {"question": "What is 38 + 25?" , "options": ["53" , "63" , "67"] , "answer": "63"} ,
        {"question": "What is 19 + 47?" , "options": ["56" , "66" , "76"] , "answer": "66"} ,
        {"question": "What is 84 + 39?" , "options": ["113" , "123" , "133"] , "answer": "123"} ,
        {"question": "What is 54 - 19?" , "options": ["25" , "35" , "45"] , "answer": "35"} ,
        {"question": "What is 71 - 38?" , "options": ["33" , "37" , "43"] , "answer": "33"} ,
        {"question": "What is 60 - 24?" , "options": ["26" , "36" , "44"] , "answer": "36"} ,
        {"question": "What is 7 x 8?" , "options": ["48" , "54" , "56"] , "answer": "56"} ,
        {"question": "What is 9 x 12?" , "options": ["96" , "108" , "112"] , "answer": "108"} ,
        {"question": "What is 6 x 7?" , "options": ["36" , "42" , "48"] , "answer": "42"} ,
        {"question": "What is 11 x 12?" , "options": ["121" , "132" , "144"] , "answer": "132"} ,
        {"question": "What is 96 / 8?" , "options": ["11" , "12" , "14"] , "answer": "12"} ,
        {"question": "What is 91 / 7?" , "options": ["12" , "13" , "14"] , "answer": "13"} ,
        {"question": "What is 120 / 8?" , "options": ["12" , "15" , "18"] , "answer": "15"} ,
        {"question": "What is 45 / 5?" , "options": ["7" , "8" , "9"] , "answer": "9"}
    ] ,

    "Medium": [
        {"question": "What is 6 to the power of 2?" , "options": ["12" , "36" , "42"] , "answer": "36"} ,
        {"question": "What is 4 to the power of 3?" , "options": ["12" , "43" , "64"] , "answer": "64"} ,
        {"question": "What is the square root of 144?" , "options": ["12" , "14" , "72"] , "answer": "12"} ,
        {"question": "What is the square root of 225?" , "options": ["15" , "25" , "45"] , "answer": "15"} ,
        {"question": "What is 1/8 + 3/8? Give your answer as a fraction in its simplest form." , "options": ["1/4" , "1/2" , "3/8"] , "answer": "1/2"} ,
        {"question": "What is 3/10 + 1/10? Give your answer as a fraction in its simplest form." , "options": ["1/5" , "2/5" , "4/5"] , "answer": "2/5"} ,
        {"question": "What is 25% of 160?" , "options": ["30" , "40" , "45"] , "answer": "40"} ,
        {"question": "What is 75% of 240?" , "options": ["160" , "180" , "200"] , "answer": "180"} ,
        {"question": "What is 20% of 350?" , "options": ["60" , "70" , "75"] , "answer": "70"} ,
        {"question": "What is the next prime number after 31?" , "options": ["33" , "35" , "37"] , "answer": "37"} ,
        {"question": "What is the next prime number after 89?" , "options": ["91" , "95" , "97"] , "answer": "97"} ,
        {"question": "What is the highest common factor of 36 and 48?" , "options": ["6" , "12" , "16"] , "answer": "12"} ,
        {"question": "What is the highest common factor of 45 and 60?" , "options": ["5" , "9" , "15"] , "answer": "15"} ,
        {"question": "What is the lowest common multiple of 6 and 8?" , "options": ["14" , "24" , "48"] , "answer": "24"} ,
        {"question": "What is the lowest common multiple of 9 and 12?" , "options": ["24" , "36" , "108"] , "answer": "36"}
    ] ,

    "Hard": [
        {"question": "Solve for x:   3x + 7 = 25" , "options": ["4" , "6" , "9"] , "answer": "6"} ,
        {"question": "Solve for x:   5x - 12 = 38" , "options": ["8" , "10" , "12"] , "answer": "10"} ,
        {"question": "A rectangle is 12 cm wide and 9 cm tall. What is its area in square cm?" , "options": ["42" , "96" , "108"] , "answer": "108"} ,
        {"question": "A rectangle is 15 cm wide and 7 cm tall. What is its area in square cm?" , "options": ["44" , "105" , "115"] , "answer": "105"} ,
        {"question": "A rectangle is 14 cm wide and 6 cm tall. What is its perimeter in cm?" , "options": ["20" , "40" , "84"] , "answer": "40"} ,
        {"question": "A rectangle is 11 cm wide and 8 cm tall. What is its perimeter in cm?" , "options": ["19" , "38" , "88"] , "answer": "38"} ,
        {"question": "A box is 5 cm long, 4 cm wide and 3 cm tall. What is its volume in cubic cm?" , "options": ["12" , "47" , "60"] , "answer": "60"} ,
        {"question": "A box is 8 cm long, 6 cm wide and 2 cm tall. What is its volume in cubic cm?" , "options": ["16" , "48" , "96"] , "answer": "96"} ,
        {"question": "What is the mean of 4, 8, 12, 16?" , "options": ["8" , "10" , "12"] , "answer": "10"} ,
        {"question": "What is the median of 7, 3, 11, 5, 9?" , "options": ["5" , "7" , "9"] , "answer": "7"} ,
        {"question": "What is the mode of 2, 5, 5, 7, 9, 5, 3?" , "options": ["3" , "5" , "7"] , "answer": "5"} ,
        {"question": "y = 4x^2.   What is dy/dx when x = 3?" , "options": ["12" , "24" , "36"] , "answer": "24"} ,
        {"question": "y = 2x^3.   What is dy/dx when x = 3?" , "options": ["18" , "36" , "54"] , "answer": "54"} ,
        {"question": "What is the area under y = 6x between x = 0 and x = 4?" , "options": ["24" , "48" , "96"] , "answer": "48"} ,
        {"question": "What is the area under y = 3x^2 between x = 0 and x = 3?" , "options": ["9" , "27" , "81"] , "answer": "27"}
    ]
}

# The three lanes the bike drives between and the middle of each one.
LANE_COUNT = 3
LANE_X = [108 , 325 , 542]

# Where everything sits on the race track.
QUESTION_Y = 50
SCORE_Y = 105
HELP_Y = 133
HEADER_Y = 152
BAR_TOP = 152
BAR_BOTTOM = 158
BAR_LEFT = 60
BAR_RIGHT = 590
ROAD_TOP = 164
ROAD_BOTTOM = 600
GATE_Y = 228
GATE_STOP_Y = 462
BIKE_Y = 540
FOOTER_Y = 624
ROAD_EDGE = 14

# The size of each answer gate.
GATE_WIDTH = 168
GATE_HEIGHT = 54

# The working out pad that the pen button opens over the road.
PAD_LEFT = 55
PAD_TOP = 218
PAD_WIDTH = 540
PAD_HEIGHT = 330
PAD_TOOLS_Y = 196
PEN_WIDTH = 3
ERASER_SIZE = 14
PEN_X = 585

# The dash pattern of the lane markings and the length of one repeat.
LANE_DASH = (26 , 24)
DASH_CYCLE = 50

# How long the screen waits between frames and how gate speed becomes pixels.
FRAME_DELAY = 40
DIVISOR = 3

# How long the correct or wrong message stays on screen.
PAUSE = 950

# How often the live timer on the race screen is refreshed, in milliseconds.
TIMER_TICK = 1000

# The speedometer that the difficulty screen is drawn as.
GAUGE_X = 325
GAUGE_Y = 300
GAUGE_RADIUS = 150
GAUGE_BAND = 22
NEEDLE_LEN = 115

# What the player has to do, spelled out so nobody has to guess.
HELP_TEXT = "Arrow keys pick a lane, Space or Enter drives, the pen opens a working out pad."
TYPING_HELP = "Type your answer in the box and press Enter. Click the pen for a working out pad."

# Returns a number of seconds written as minutes and seconds, for example 2:05.
def format_time(seconds):
    minutes = seconds // 60
    rest = seconds % 60
    return f"{minutes}:{str(rest).zfill(2)}"

# Paints every colour in the game from whichever theme is switched on.
def apply_theme():
    global background_color , text_color , dim_text , button_color , button_text , button_active
    global accent , accent_deep , on_accent , road_color , lane_color , gate_color
    global correct_color , wrong_color , pad_color , pad_ink , zones
    global plain_btn , accent_btn , dim_label , page_label

    if current_theme == "Light":
        colours = LIGHT_COLOURS
    else:
        colours = DARK_COLOURS

    background_color = colours["background"]
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
    gate_color = colours["gate"]
    correct_color = colours["correct"]
    wrong_color = colours["wrong"]
    pad_color = colours["pad"]
    pad_ink = colours["pad_ink"]

    # The three bands on the dial are named separately so they can be looked up.
    zones = {"Easy": colours["easy"] , "Medium": colours["medium"] , "Hard": colours["hard"]}

    # The look of each kind of widget, written once so every screen matches.
    plain_btn = {"fg": button_text , "bg": button_color , "activebackground": button_active , "relief": FLAT}
    accent_btn = {"fg": on_accent , "bg": accent , "activebackground": accent_deep , "relief": FLAT}
    dim_label = {"fg": dim_text , "bg": background_color}
    page_label = {"fg": text_color , "bg": background_color}

# The characters a username is allowed to contain, so anything else can be refused.
ALLOWED_LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

# Check_username function checks a username and returns a message, or an empty string when it is fine.
# The checking is kept out of the screen functions so the same rules can be reused and tested on their own.
def check_username(username):
    if username == "":
        return "You have not typed a username. Please type one into the username box."

    if len(username) < USERNAME_MIN:
        return f"Your username is only {len(username)} characters long. Please make it at least {USERNAME_MIN} characters."

    if len(username) > USERNAME_MAX:
        return f"Your username is {len(username)} characters long, which is too long. Please shorten it to {USERNAME_MAX} characters or fewer."

    # Going through the username one letter at a time, the way the GeeksforGeeks string examples do.
    for letter in username:
        if letter not in ALLOWED_LETTERS:
            if letter == " ":
                return "Your username has a space in it. Please use an underscore instead, for example math_racer."
            return f"Your username contains {letter} which is not allowed. Please use only letters, numbers and underscores, for example math_racer."

    return ""

# Check_password function checks a password and returns a message, or an empty string when it is fine.
def check_password(password):
    if password == "":
        return "You have not typed a password. Please type one into the password box."

    if len(password) < PASSWORD_MIN:
        short_by = PASSWORD_MIN - len(password)
        return f"Your password is only {len(password)} characters long. Please add {short_by} more so it is at least {PASSWORD_MIN} characters."

    if "," in password:
        return "Your password has a comma in it. Commas separate the details inside the accounts file, so please use a different character."

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

    return ""

# Check_answer function checks a typed answer and returns a message, or an empty string when it is fine.
def check_answer(typed):
    if typed == "":
        return "You have not typed an answer. Please type your answer into the answer box."

    # Isdigit only accepts digits, so the slash of a fraction is taken out before the check.
    if not typed.replace("/" , "").isdigit():
        return f"Your answer {typed} is not a number. Please type digits only, for example 12, or a fraction like 1/2."

    if typed.count("/") > 1:
        return f"Your answer {typed} has more than one slash in it. A fraction only needs one, for example 3/4."

    return ""

# Show_password function switches the password boxes between hidden * and visible.
# It takes the boxes it works on so that the sign in screen and the signup screen can share it.
def show_password(boxes , button):
    if boxes[0].cget("show") == "*":
        for box in boxes:
            box.config(show = "")
        button.config(text = "Hide Password")
    else:
        for box in boxes:
            box.config(show = "*")
        button.config(text = "Show Password")

# Load_accounts function reads every saved account into a dictionary of username to password.
def load_accounts():
    accounts = {}
    filepath = os.path.join(FOLDER , "accounts.txt")

    # Using a try and except code block so a missing file gives an empty dictionary instead of an error.
    try:
        with open(filepath , "r" , encoding = "utf-8") as file:
            # This for loop goes through every line in the file and splits the username and password with a comma.
            for line in file:
                parts = line.strip().split(",")

                # A row is only used when it has both details, so a damaged row is skipped.
                if len(parts) == 2 and parts[0] != "":
                    accounts[parts[0]] = parts[1]
    except FileNotFoundError:
        pass

    return accounts

# Save_account function adds one new account onto the end of the accounts file.
def save_account(username , password):
    filepath = os.path.join(FOLDER , "accounts.txt")

    with open(filepath , "a" , encoding = "utf-8") as file:
        file.write(f"{username},{password}\n")

# Creating the sign in screen, which is the first screen the player sees.
def main():
    clear_screen()

    # Defining global variables for the sign in entry fields so that they can be accessed from the login function below.
    global login_username , login_password

    title = Label(main_screen , text = "SIGN IN" , fg = accent , bg = background_color , font = HEAD_FONT)
    title.pack(pady = (60 , 20))

    username_label = Label(main_screen , text = "Enter your username" , **dim_label , font = LABEL_FONT)
    username_label.pack(pady = (20 , 0))
    login_username = Entry(main_screen , width = 30 , font = ENTRY_FONT)
    login_username.pack()

    password_label = Label(main_screen , text = "Enter your password" , **dim_label , font = LABEL_FONT)
    password_label.pack(pady = (20 , 0))
    login_password = Entry(main_screen , width = 30 , show = "*" , font = ENTRY_FONT)
    login_password.pack()

    show_button = Button(main_screen , text = "Show Password" , **plain_btn , font = SMALL_FONT)
    show_button.config(command = lambda: show_password([login_password] , show_button))
    show_button.pack(pady = 8)

    login_but = Button(main_screen , text = "Sign In" , **accent_btn , command = login , font = BTN_FONT , width = 20 , height = 2)
    login_but.pack(pady = 30)

    switch_but = Button(main_screen , text = "Create an account instead" , **dim_label , activeforeground = accent , command = signup_screen , font = SMALL_FONT , relief = FLAT)
    switch_but.pack()

    login_username.focus_set()

# Login function checks the typed details against the saved accounts and opens the menu.
def login():
    # Define global variable for current_user and assign it the value of username only if it is a valid username.
    global current_user

    username = login_username.get()
    password = login_password.get()

    if username == "":
        messagebox.showerror("Cannot Sign In" , "You have not typed a username. Please type the username you signed up with.")
        return

    if password == "":
        messagebox.showerror("Cannot Sign In" , "You have not typed a password. Please type the password you signed up with.")
        return

    # The reading function fetches the accounts, and this function only decides what to show.
    accounts = load_accounts()

    if len(accounts) == 0:
        messagebox.showerror("Cannot Sign In" , "There are no accounts saved yet. Please use Create an account instead to make one.")
        return

    if username not in accounts:
        messagebox.showerror("Cannot Sign In" , f"There is no account saved with the username {username}. Please check your spelling, or use Create an account instead to make a new one.")
        return

    if accounts[username] != password:
        messagebox.showerror("Cannot Sign In" , f"That password does not match the one saved for {username}. Please try typing it again.")
        return

    current_user = username
    messagebox.showinfo("Signed In" , f"Welcome back {username}.")
    menu_screen()

# Signup screen function displays signup entry boxes allowing user to create a new account.
# This is called when user presses the create an account button on the sign in screen.
def signup_screen():
    clear_screen()

    # Global variable for all the entry fields so they can be accessed from the sign up function.
    global username_entry , password_entry , con_password_entry

    title = Label(main_screen , text = "CREATE ACCOUNT" , fg = accent , bg = background_color , font = HEAD_FONT)
    title.pack(pady = (25 , 5))

    username_label = Label(main_screen , text = "Enter desired username" , **dim_label , font = LABEL_FONT)
    username_label.pack(pady = (12 , 0))
    username_entry = Entry(main_screen , width = 30 , font = ENTRY_FONT)
    username_entry.pack()

    password_label = Label(main_screen , text = "Create a new password" , **dim_label , font = LABEL_FONT)
    password_label.pack(pady = (12 , 0))
    password_entry = Entry(main_screen , width = 30 , show = "*" , font = ENTRY_FONT)
    password_entry.pack()

    show_button = Button(main_screen , text = "Show Password" , **plain_btn , font = SMALL_FONT)
    show_button.config(command = lambda: show_password([password_entry , con_password_entry] , show_button))
    show_button.pack(pady = 6)

    con_password_label = Label(main_screen , text = "Confirm password" , **dim_label , font = LABEL_FONT)
    con_password_label.pack(pady = (8 , 0))
    con_password_entry = Entry(main_screen , width = 30 , show = "*" , font = ENTRY_FONT)
    con_password_entry.pack()

    # The rules, so nobody has to guess what makes a username and password good enough.
    rules_label = Label(main_screen , text = f"Your username must be {USERNAME_MIN} to {USERNAME_MAX} letters, numbers or underscores. Your password must be at least {PASSWORD_MIN} characters long, and include at least 1 number and 1 capital letter." , **dim_label , font = SMALL_FONT , wraplength = 430 , justify = CENTER)
    rules_label.pack(pady = 12)

    sign_up_but = Button(main_screen , text = "Sign Up" , **accent_btn , command = signup , font = BTN_FONT , width = 20 , height = 2)
    sign_up_but.pack(pady = 8)

    switch_but = Button(main_screen , text = "Sign in instead" , **dim_label , activeforeground = accent , command = main , font = SMALL_FONT , relief = FLAT)
    switch_but.pack()

    username_entry.focus_set()

# Function checks fields on signup screen and creates the account.
def signup():
    # Accessing the global variables of the signup screen fields from above.
    global current_user

    username = username_entry.get()
    password = password_entry.get()
    con_password = con_password_entry.get()

    # The checking functions do the deciding, and this function only shows what they say.
    problem = check_username(username)
    if problem != "":
        messagebox.showerror("Cannot Create Account" , problem)
        return

    problem = check_password(password)
    if problem != "":
        messagebox.showerror("Cannot Create Account" , problem)
        return

    # Making sure the two password boxes were typed the same.
    if password != con_password:
        messagebox.showerror("Cannot Create Account" , "Your two passwords do not match. Please type exactly the same password into both boxes.")
        return

    # Stopping the player taking a username that somebody else already has.
    if username in load_accounts():
        messagebox.showerror("Cannot Create Account" , f"The username {username} is already taken. Please choose a different username.")
        return

    save_account(username , password)

    current_user = username
    messagebox.showinfo("Account Created" , f"Welcome {username}. Your account has been saved, so next time you can just sign in.")
    menu_screen()

# Menu screen function displays the play, difficulty, settings and leaderboard buttons.
def menu_screen():
    clear_screen()

    title = Label(main_screen , text = "MATH RACER" , fg = accent , bg = background_color , font = (TITLE_FONT , 58))
    title.pack(pady = (45 , 10))

    top_frame = Frame(main_screen , bg = background_color)
    top_frame.pack(pady = 25)

    settings_button = Button(top_frame , text = "Settings" , **plain_btn , command = settings_screen , font = BTN_FONT , width = 15 , height = 2)
    settings_button.pack(side = LEFT , padx = 25)

    leaderboard_button = Button(top_frame , text = "Leaderboard" , **plain_btn , command = leaderboard_screen , font = BTN_FONT , width = 15 , height = 2)
    leaderboard_button.pack(side = LEFT , padx = 25)

    play_button = Button(main_screen , text = "PLAY" , **accent_btn , command = lambda: start_race(current_level , current_user) , font = (FONT , 16 , "bold") , width = 18 , height = 2)
    play_button.pack(pady = 25)

    bottom_frame = Frame(main_screen , bg = background_color)
    bottom_frame.pack(pady = 25)

    difficulty_button = Button(bottom_frame , text = "Difficulty" , **plain_btn , command = difficulty_screen , font = BTN_FONT , width = 15 , height = 2)
    difficulty_button.pack(side = LEFT , padx = 25)

    quit_button = Button(bottom_frame , text = "Quit" , **plain_btn , command = close_program , font = BTN_FONT , width = 15 , height = 2)
    quit_button.pack(side = LEFT , padx = 25)

    signed_in_label = Label(main_screen , text = f"Signed in as {current_user}" , **dim_label , font = SMALL_FONT)
    signed_in_label.pack(pady = 15)

# Difficulty screen function draws a speedometer whose needle POINTS at the chosen level.
def difficulty_screen():
    clear_screen()

    title = Label(main_screen , text = "DIFFICULTY" , fg = accent , bg = background_color , font = HEAD_FONT)
    title.pack(pady = (25 , 0))

    canvas = Canvas(main_screen , width = 650 , height = 320 , bg = background_color , highlightthickness = 0)
    canvas.pack()

    # The square the gauge is drawn inside, worked out from its centre and radius.
    box = (GAUGE_X - GAUGE_RADIUS , GAUGE_Y - GAUGE_RADIUS , GAUGE_X + GAUGE_RADIUS , GAUGE_Y + GAUGE_RADIUS)

    # Drawing a coloured band for each difficulty, each one a third of the dial.
    canvas.create_arc(box , start = 120 , extent = 60 , style = ARC , width = GAUGE_BAND , outline = zones["Easy"])
    canvas.create_arc(box , start = 60 , extent = 60 , style = ARC , width = GAUGE_BAND , outline = zones["Medium"])
    canvas.create_arc(box , start = 0 , extent = 60 , style = ARC , width = GAUGE_BAND , outline = zones["Hard"])

    # Naming every band and printing what an answer is worth underneath it.
    canvas.create_text(168 , 198 , text = "EASY" , font = (TITLE_FONT , 22) , fill = zones["Easy"] , anchor = E)
    canvas.create_text(168 , 222 , text = f"{POINTS['Easy']} POINTS an answer" , font = SMALL_FONT , fill = dim_text , anchor = E)
    canvas.create_text(325 , 112 , text = "MEDIUM" , font = (TITLE_FONT , 22) , fill = zones["Medium"] , anchor = S)
    canvas.create_text(325 , 136 , text = f"{POINTS['Medium']} POINTS an answer" , font = SMALL_FONT , fill = dim_text , anchor = S)
    canvas.create_text(482 , 198 , text = "HARD" , font = (TITLE_FONT , 22) , fill = zones["Hard"] , anchor = W)
    canvas.create_text(482 , 222 , text = f"{POINTS['Hard']} POINTS an answer" , font = SMALL_FONT , fill = dim_text , anchor = W)

    # Working out where the tip of the needle goes with sine and cosine, then drawing it.
    radians = math.radians(ANGLES[current_level])
    tip_x = GAUGE_X + NEEDLE_LEN * math.cos(radians)
    tip_y = GAUGE_Y - NEEDLE_LEN * math.sin(radians)
    canvas.create_line(GAUGE_X , GAUGE_Y , tip_x , tip_y , width = 6 , fill = text_color , arrow = LAST , arrowshape = (18 , 22 , 7))
    canvas.create_oval(GAUGE_X - 13 , GAUGE_Y - 13 , GAUGE_X + 13 , GAUGE_Y + 13 , fill = background_color , outline = text_color , width = 3)

    # The wording under the dial that spells out what the needle is pointing at.
    chosen_label = Label(main_screen , text = f"{current_level.upper()}  -  {POINTS[current_level]} POINTS AN ANSWER" , **page_label , font = (FONT , 15 , "bold"))
    chosen_label.pack(pady = 10)

    # Remembers the difficulty a button stands for and draws the screen again with the needle moved.
    def pick(level):
        global current_level
        current_level = level
        difficulty_screen()

    button_frame = Frame(main_screen , bg = background_color)
    button_frame.pack(pady = 10)

    easy_button = Button(button_frame , text = "Easy" , fg = zones["Easy"] , bg = button_color , activebackground = button_active , activeforeground = zones["Easy"] , command = lambda: pick("Easy") , font = BTN_FONT , width = 11 , height = 2 , relief = FLAT)
    easy_button.pack(side = LEFT , padx = 12)

    medium_button = Button(button_frame , text = "Medium" , fg = zones["Medium"] , bg = button_color , activebackground = button_active , activeforeground = zones["Medium"] , command = lambda: pick("Medium") , font = BTN_FONT , width = 11 , height = 2 , relief = FLAT)
    medium_button.pack(side = LEFT , padx = 12)

    hard_button = Button(button_frame , text = "Hard" , fg = zones["Hard"] , bg = button_color , activebackground = button_active , activeforeground = zones["Hard"] , command = lambda: pick("Hard") , font = BTN_FONT , width = 11 , height = 2 , relief = FLAT)
    hard_button.pack(side = LEFT , padx = 12)

    back_button = Button(main_screen , text = "← Back" , **plain_btn , command = menu_screen , font = BTN_FONT , width = 12 , height = 2)
    back_button.pack(pady = 15)

# Settings screen function lets the player switch between the dark and light themes.
def settings_screen():
    clear_screen()

    title = Label(main_screen , text = "SETTINGS" , fg = accent , bg = background_color , font = HEAD_FONT)
    title.pack(pady = (45 , 30))

    theme_label = Label(main_screen , text = "Theme" , **dim_label , font = LABEL_FONT)
    theme_label.pack()

    theme_value = StringVar(main_screen , value = current_theme)

    theme_frame = Frame(main_screen , bg = background_color)
    theme_frame.pack(pady = 10)

    dark_button = Radiobutton(theme_frame , text = "Dark mode" , variable = theme_value , value = "Dark" , **page_label , activebackground = background_color , activeforeground = accent , selectcolor = button_color , font = BTN_FONT)
    dark_button.pack(side = LEFT , padx = 15)

    light_button = Radiobutton(theme_frame , text = "Light mode" , variable = theme_value , value = "Light" , **page_label , activebackground = background_color , activeforeground = accent , selectcolor = button_color , font = BTN_FONT)
    light_button.pack(side = LEFT , padx = 15)

    answer_label = Label(main_screen , text = "Answering" , **dim_label , font = LABEL_FONT)
    answer_label.pack(pady = (18 , 0))

    answer_value = StringVar(main_screen , value = answer_mode)

    answer_frame = Frame(main_screen , bg = background_color)
    answer_frame.pack(pady = 8)

    gates_button = Radiobutton(answer_frame , text = "Drive through the gates" , variable = answer_value , value = "Gates" , **page_label , activebackground = background_color , activeforeground = accent , selectcolor = button_color , font = BTN_FONT)
    gates_button.pack(side = LEFT , padx = 10)

    typing_button = Radiobutton(answer_frame , text = "Type the answer" , variable = answer_value , value = "Typing" , **page_label , activebackground = background_color , activeforeground = accent , selectcolor = button_color , font = BTN_FONT)
    typing_button.pack(side = LEFT , padx = 10)

    # The small text explaining what the theme buttons do.
    help_label = Label(main_screen , text = f"Light mode is easier to read in a bright room. Typing the answer lets you work it out yourself. Every race is {RACE_LENGTH} questions." , **dim_label , font = SMALL_FONT , wraplength = 520 , justify = CENTER)
    help_label.pack(pady = 18)

    # Saves the theme, then paints the screen again in the chosen colours.
    def save():
        global current_theme , answer_mode

        current_theme = theme_value.get()
        answer_mode = answer_value.get()
        save_settings()

        apply_theme()
        main_screen.configure(bg = background_color)
        settings_screen()

        messagebox.showinfo("Settings Saved" , "Your settings have been saved and will still be here next time you play.")

    button_frame = Frame(main_screen , bg = background_color)
    button_frame.pack(pady = 28)

    back_button = Button(button_frame , text = "← Back" , **plain_btn , command = menu_screen , font = BTN_FONT , width = 14 , height = 2)
    back_button.pack(side = LEFT , padx = 20)

    save_button = Button(button_frame , text = "Save" , **accent_btn , command = save , font = BTN_FONT , width = 14 , height = 2)
    save_button.pack(side = LEFT , padx = 20)

# Leaderboard screen function shows the best drivers for all three difficulties side by side.
def leaderboard_screen():
    clear_screen()

    title = Label(main_screen , text = "LEADERBOARD" , fg = accent , bg = background_color , font = HEAD_FONT)
    title.pack(pady = (30 , 20))

    boards_frame = Frame(main_screen , bg = background_color)
    boards_frame.pack()

    # Drawing one board for each difficulty, side by side across the screen.
    for level in RACE_QUESTIONS:
        column = Frame(boards_frame , bg = background_color)
        column.pack(side = LEFT , padx = 2 , anchor = N)

        # The heading of the board, written in that difficulty's colour.
        Label(column , text = level.upper() , fg = zones[level] , bg = background_color , font = (TITLE_FONT , 24)).pack()

        # The column headings, in a typewriter FONT so everything lines up.
        Label(column , text = f"{'':<3}{'DRIVER':<13}{'PTS':<4}TIME" , **dim_label , font = ("Consolas" , 8)).pack(pady = (5 , 8))

        drivers = best_records(level)

        # An empty board says so rather than leaving a blank column.
        if len(drivers) == 0:
            Label(column , text = "No races yet" , **dim_label , font = SMALL_FONT).pack(pady = 10)

        rank = 1

        for driver , score , seconds in drivers:
            # The driver who is signed in is picked out in the accent colour.
            if driver == current_user:
                row_color = accent
            else:
                row_color = text_color

            Label(column , text = f"{rank:<3}{driver:<13}{score:<4}{format_time(seconds)}" , fg = row_color , bg = background_color , font = ("Consolas" , 8)).pack()
            rank += 1

    # Explaining the ordering, since the biggest score always goes on top.
    Label(main_screen , text = "The best ten runs for each difficulty are shown, highest score first." , **dim_label , font = SMALL_FONT).pack(pady = 25)

    back_button = Button(main_screen , text = "← Back" , **plain_btn , command = menu_screen , font = BTN_FONT , width = 12 , height = 2)
    back_button.pack()

# Pad class is the working out pad that the pen button opens over the road.
class Pad:
    # Runs when the class is created and called.
    # Builds the paper, the three tools and the strip they sit on, then hides them all.
    def __init__(self , canvas):
        self.canvas = canvas
        self.open = False
        self.tool = "Pen"
        self.last_x = 0
        self.last_y = 0

        # A strip behind the tools so they do not float over the gates.
        self.bar = canvas.create_rectangle(PAD_LEFT , PAD_TOOLS_Y - 18 , PAD_LEFT + PAD_WIDTH , PAD_TOP , fill = background_color , outline = accent , width = 2)

        self.paper = Canvas(main_screen , width = PAD_WIDTH , height = PAD_HEIGHT , bg = pad_color , highlightthickness = 2 , highlightbackground = accent)
        self.paper_window = canvas.create_window(PAD_LEFT , PAD_TOP , anchor = NW , window = self.paper)

        # Following the tkinter whiteboard pattern, a press records where the stroke starts.
        self.paper.bind("<Button-1>" , self.press)
        self.paper.bind("<B1-Motion>" , self.drag)

        self.pen_tool = Button(main_screen , text = "Pen" , **plain_btn , command = self.use_pen , font = TOOL_FONT , width = 8)
        self.pen_window = canvas.create_window(170 , PAD_TOOLS_Y , anchor = CENTER , window = self.pen_tool)

        self.eraser_tool = Button(main_screen , text = "Eraser" , **plain_btn , command = self.use_eraser , font = TOOL_FONT , width = 8)
        self.eraser_window = canvas.create_window(325 , PAD_TOOLS_Y , anchor = CENTER , window = self.eraser_tool)

        clear_tool = Button(main_screen , text = "Clear" , **plain_btn , command = self.clear , font = TOOL_FONT , width = 8)
        self.clear_window = canvas.create_window(480 , PAD_TOOLS_Y , anchor = CENTER , window = clear_tool)

        self.pick_tool()
        self.show()

    # Opens or shuts the pad when the pen button is clicked.
    def toggle(self):
        self.open = not self.open
        self.show()

    # Shows or hides the paper and the three tools that go with it.
    def show(self):
        if self.open:
            showing = NORMAL
        else:
            showing = HIDDEN

        for item in [self.bar , self.paper_window , self.pen_window , self.eraser_window , self.clear_window]:
            self.canvas.itemconfig(item , state = showing)

    # Lights up whichever of the two tools is currently in use.
    def pick_tool(self):
        if self.tool == "Pen":
            self.pen_tool.config(fg = accent)
            self.eraser_tool.config(fg = button_text)
        else:
            self.pen_tool.config(fg = button_text)
            self.eraser_tool.config(fg = accent)

    # Switches to the pen so the mouse draws.
    def use_pen(self):
        self.tool = "Pen"
        self.pick_tool()

    # Switches to the eraser so the mouse rubs out.
    def use_eraser(self):
        self.tool = "Eraser"
        self.pick_tool()

    # Wipes the whole pad, the way the tkinter whiteboard tutorial does it.
    def clear(self):
        self.paper.delete("all")

    # Remembers where a stroke begins so the first drag has a point to join to.
    def press(self , event):
        self.last_x = event.x
        self.last_y = event.y

    # Joins the last point to the new one, or rubs out a square with the eraser.
    def drag(self , event):
        if self.tool == "Pen":
            self.paper.create_line(self.last_x , self.last_y , event.x , event.y , fill = pad_ink , width = PEN_WIDTH , capstyle = ROUND)
        else:
            self.paper.create_rectangle(event.x - ERASER_SIZE , event.y - ERASER_SIZE , event.x + ERASER_SIZE , event.y + ERASER_SIZE , fill = pad_color , outline = pad_color)

        self.last_x = event.x
        self.last_y = event.y

# Race class shows the questions on a road, checks answers and tracks the score.
class Race:
    # Runs when the class is created and called.
    # Defines all the variables used later on in the class and calls the show_question function.
    def __init__(self , difficulty , username):
        self.difficulty = difficulty
        self.username = username
        self.score = 0
        self.correct = 0
        self.question_no = 0
        self.questions = list(RACE_QUESTIONS[difficulty])

        # A race can never be longer than the number of questions there are to ask.
        self.total = min(RACE_LENGTH , len(self.questions))
        random.shuffle(self.questions)
        self.lane = 1
        self.moving = False
        self.drive_step = SPEEDS[difficulty] // DIVISOR
        self.time_taken = 0
        self.show_question()

        # Starting the clock, which then keeps itself going once a second.
        main_screen.after(TIMER_TICK , self.tick)

    # Show_question function draws the road and puts a gate in every lane.
    def show_question(self):
        clear_screen()

        self.canvas = Canvas(main_screen , width = 650 , height = 650 , bg = road_color , highlightthickness = 0)
        self.canvas.pack(pady = 5)

        # Painting the solid lines down either kerb of the road.
        self.canvas.create_line(ROAD_EDGE , ROAD_TOP , ROAD_EDGE , ROAD_BOTTOM , fill = lane_color , width = 6)
        self.canvas.create_line(650 - ROAD_EDGE , ROAD_TOP , 650 - ROAD_EDGE , ROAD_BOTTOM , fill = lane_color , width = 6)

        # Painting the dashed lines that divide the three lanes.
        self.lane_lines = []
        self.dash_offset = 0
        for divider in range(1 , LANE_COUNT):
            line_x = (LANE_X[divider - 1] + LANE_X[divider]) / 2
            self.lane_lines.append(self.canvas.create_line(line_x , ROAD_TOP , line_x , ROAD_BOTTOM , fill = lane_color , width = 4 , dash = LANE_DASH))

        # The bar across the top holding the question and the score.
        self.canvas.create_rectangle(0 , 0 , 650 , HEADER_Y , fill = background_color , outline = "")
        self.canvas.create_text(325 , QUESTION_Y , text = self.questions[self.question_no]["question"] , font = (FONT , 15 , "bold") , fill = text_color , width = 600 , justify = CENTER)
        self.scoreboard = self.canvas.create_text(325 , SCORE_Y , text = "" , font = (FONT , 9 , "bold") , fill = accent)
        if answer_mode == "Gates":
            self.canvas.create_text(325 , HELP_Y , text = HELP_TEXT , font = SMALL_FONT , fill = dim_text)
        else:
            self.canvas.create_text(325 , HELP_Y , text = TYPING_HELP , font = SMALL_FONT , fill = dim_text)

        # The bar that fills up as the race is worked through.
        self.canvas.create_rectangle(BAR_LEFT , BAR_TOP , BAR_RIGHT , BAR_BOTTOM , fill = button_color , outline = "")
        filled = BAR_LEFT + (BAR_RIGHT - BAR_LEFT) * self.question_no / self.total
        self.canvas.create_rectangle(BAR_LEFT , BAR_TOP , filled , BAR_BOTTOM , fill = accent , outline = "")

        # The matching bar along the bottom for the back button and the result.
        self.canvas.create_rectangle(0 , ROAD_BOTTOM , 650 , 650 , fill = background_color , outline = "")
        self.feedback = self.canvas.create_text(400 , FOOTER_Y , text = "" , font = TOOL_FONT , fill = text_color)

        # Shuffling the options so the right answer is not always in the same lane.
        self.options = self.questions[self.question_no]["options"]
        random.shuffle(self.options)

        self.gate_row = GATE_Y

        # The player either drives through a gate or types the answer, depending on the setting.
        if answer_mode == "Gates":
            self.build_gates()
        else:
            self.build_answer_box()

        # Loading the bike picture and keeping a reference so tkinter does not bin it.
        # Using a try and except block so a missing picture file does not stop the race.
        try:
            self.bike_img = ImageTk.PhotoImage(Image.open(os.path.join(FOLDER , "Bike.png")).resize((100 , 100)))
        except FileNotFoundError:
            self.bike_img = ""

        self.bike = self.canvas.create_image(LANE_X[self.lane] , BIKE_Y , anchor = CENTER , image = self.bike_img)

        # Lifting the numbers above the bike so the chosen answer stays readable.
        if answer_mode == "Gates":
            for lane in range(LANE_COUNT):
                self.canvas.tag_raise(self.gate_texts[lane])

        back_button = Button(main_screen , text = "← Back" , **plain_btn , command = self.leave_race , font = BTN_FONT , width = 10)
        self.canvas.create_window(85 , FOOTER_Y , anchor = CENTER , window = back_button)

        # Steering with the arrow keys and setting off with space or enter.
        if answer_mode == "Gates":
            main_screen.bind("<Left>" , self.go_left)
            main_screen.bind("<Right>" , self.go_right)
            main_screen.bind("<space>" , self.submit)
            main_screen.bind("<Return>" , self.submit)
            main_screen.focus_set()
        else:
            main_screen.bind("<Return>" , self.submit_typed)

        self.build_pad()

        if answer_mode == "Gates":
            self.highlight_lane()

        self.show_scoreboard()

    # Builds the three answer gates that the bike drives through.
    def build_gates(self):
        self.gates = []
        self.gate_texts = []

        for lane in range(LANE_COUNT):
            self.gates.append(self.canvas.create_rectangle(LANE_X[lane] - GATE_WIDTH / 2 , GATE_Y - GATE_HEIGHT / 2 , LANE_X[lane] + GATE_WIDTH / 2 , GATE_Y + GATE_HEIGHT / 2 , fill = gate_color , outline = lane_color , width = 3))
            self.gate_texts.append(self.canvas.create_text(LANE_X[lane] , GATE_Y , text = self.options[lane] , font = (FONT , 21 , "bold") , fill = text_color))

    # Builds the box the player types their answer into, used instead of the gates.
    def build_answer_box(self):
        self.canvas.create_text(325 , GATE_Y - 46 , text = "Type your answer" , font = LABEL_FONT , fill = lane_color)

        self.answer_entry = Entry(main_screen , width = 10 , font = (FONT , 24 , "bold") , justify = CENTER)
        self.canvas.create_window(325 , GATE_Y + 2 , anchor = CENTER , window = self.answer_entry)

        answer_button = Button(main_screen , text = "Check Answer" , **accent_btn , command = self.submit_typed , font = BTN_FONT , width = 14 , height = 1)
        self.canvas.create_window(325 , GATE_Y + 66 , anchor = CENTER , window = answer_button)

        self.answer_entry.focus_set()

    # Submit_typed function checks what was typed into the answer box and then marks it.
    def submit_typed(self , event = None):
        # The pad covers the answer box, so it has to be closed first.
        if self.pad.open:
            self.canvas.itemconfig(self.feedback , text = "Close the pad to answer" , fill = accent)
            return

        # Ignoring the key while an answer is being marked or the race is over stops a double start.
        if self.moving or self.question_no >= self.total:
            return

        typed = self.answer_entry.get().strip()

        # The checking function decides, and this function only shows what it says.
        problem = check_answer(typed)
        if problem != "":
            messagebox.showerror("Cannot Check Answer" , problem)
            return

        self.moving = True
        self.mark(typed)

    # Builds the working out pad and the pen button that opens it.
    def build_pad(self):
        self.pad = Pad(self.canvas)

        # The pen button stays on the road whether the pad is open or shut.
        pad_toggle = Button(main_screen , text = "✏️" , **plain_btn , command = self.pad.toggle , font = (EMOJI_FONT , 13) , width = 3)
        self.canvas.create_window(PEN_X , FOOTER_Y , anchor = CENTER , window = pad_toggle)

    # Tick function adds a second onto the race clock every 1000 ms.
    def tick(self):
        # If the canvas no longer exists the player has already left the race.
        if not self.canvas.winfo_exists():
            return

        # The clock stops as soon as the last question has been marked.
        if self.question_no >= self.total:
            return

        self.time_taken += 1
        self.show_scoreboard()
        main_screen.after(TIMER_TICK , self.tick)

    # Refreshes the score line at the top of the road.
    def show_scoreboard(self):
        # The number shown never goes past the total, because the counter has already moved on.
        showing = self.question_no + 1
        if showing > self.total:
            showing = self.total

        accuracy = 0
        if self.question_no > 0:
            accuracy = round(100 * self.correct / self.question_no)

        self.canvas.itemconfig(self.scoreboard , text = f"{self.difficulty.upper()}   QUESTION {showing} OF {self.total}   SCORE {self.score}   {accuracy}% CORRECT   TIME {format_time(self.time_taken)}")

    # Outlines the gate the bike is lined up with so the choice is obvious.
    def highlight_lane(self):
        for lane in range(LANE_COUNT):
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
        if self.moving:
            return

        if 0 <= lane < LANE_COUNT:
            self.lane = lane
            self.canvas.coords(self.bike , LANE_X[lane] , BIKE_Y)
            self.highlight_lane()

    # Submit function sets the gates off down the road towards the bike.
    def submit(self , event):
        # The pad covers the road, so it has to be closed before the bike sets off.
        if self.pad.open:
            self.canvas.itemconfig(self.feedback , text = "Close the pad to drive" , fill = accent)
            return

        # Ignoring the key while a run is under way or the race is over stops a double start.
        if self.moving or self.question_no >= self.total:
            return

        self.moving = True
        self.drive_down()

    # Drive_down function moves the gates one frame closer every 40 ms.
    def drive_down(self):
        # If the canvas no longer exists because the screen changed the run is called off.
        if not self.canvas.winfo_exists():
            return

        self.gate_row += self.drive_step

        # Shifting the lane markings makes the road look like it is streaming past.
        self.dash_offset += self.drive_step
        for line in self.lane_lines:
            self.canvas.itemconfig(line , dashoffset = self.dash_offset % DASH_CYCLE)

        # Keeping the gates coming until they have pulled up in front of the bike.
        if self.gate_row < GATE_STOP_Y:
            self.place_gates(self.gate_row)
            main_screen.after(FRAME_DELAY , self.drive_down)
        else:
            self.place_gates(GATE_STOP_Y)
            self.arrive()

    # Lines all three gates up across the road at the given height.
    def place_gates(self , row):
        for lane in range(LANE_COUNT):
            self.canvas.coords(self.gate_texts[lane] , LANE_X[lane] , row)
            self.canvas.coords(self.gates[lane] , LANE_X[lane] - GATE_WIDTH / 2 , row - GATE_HEIGHT / 2 , LANE_X[lane] + GATE_WIDTH / 2 , row + GATE_HEIGHT / 2)

    # Arrive function marks whichever gate reached the bike.
    def arrive(self):
        self.mark(self.options[self.lane])

    # Mark function marks one answer, moves the score and sets up the next question.
    def mark(self , chosen):
        # Marking twice would count a question that was never asked, so it is ignored.
        if self.question_no >= self.total:
            return

        right_answer = self.questions[self.question_no]["answer"]
        self.question_no += 1

        if chosen == right_answer:
            self.correct += 1
            self.score += POINTS[self.difficulty]
            self.canvas.itemconfig(self.feedback , text = "CORRECT" , fill = correct_color)
        else:
            # A wrong answer costs POINTS, but the score never drops below zero.
            self.score -= PENALTY
            if self.score < 0:
                self.score = 0

            self.canvas.itemconfig(self.feedback , text = f"WRONG, it was {right_answer}" , fill = wrong_color)

        # The gates are only on the road when the gates way of answering is being used.
        if answer_mode == "Gates":
            self.colour_gates(chosen , right_answer)

        self.show_scoreboard()

        # The message stays up for a moment so the last answer is not swallowed.
        if self.question_no >= self.total:
            main_screen.after(PAUSE , self.end)
        else:
            main_screen.after(PAUSE , self.next_question)

    # Colours the gate that was driven through and the gate that held the right answer.
    def colour_gates(self , chosen , right_answer):
        if chosen != right_answer:
            self.canvas.itemconfig(self.gates[self.lane] , fill = wrong_color)
            self.canvas.itemconfig(self.gate_texts[self.lane] , fill = on_accent)

        for lane in range(LANE_COUNT):
            if self.options[lane] == right_answer:
                self.canvas.itemconfig(self.gates[lane] , fill = correct_color)
                self.canvas.itemconfig(self.gate_texts[lane] , fill = on_accent)

    # Puts the next question on the road with a fresh set of gates.
    def next_question(self):
        # If the canvas no longer exists the player has already left the race.
        if not self.canvas.winfo_exists():
            return

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
        save_record(self.difficulty , self.username , self.score , self.time_taken)
        clear_screen()

        accuracy = round(100 * self.correct / self.total)

        # Choosing the closing message that matches how accurate the race was.
        if accuracy >= 90:
            message = "Superb driving. Almost everything right."
        elif accuracy >= 70:
            message = "A strong race, with only a few slips."
        elif accuracy >= 50:
            message = "A steady run. Worth another lap."
        elif accuracy >= 25:
            message = "Getting there. Keep practising these topics."
        else:
            message = "A tough race. Try an easier level to build up."

        Label(main_screen , text = "RACE COMPLETE" , fg = accent , bg = background_color , font = HEAD_FONT).pack(pady = (45 , 20))

        # The score itself, given the most room because it is the headline.
        Label(main_screen , text = "FINAL SCORE" , **dim_label , font = SMALL_FONT).pack()
        Label(main_screen , text = str(self.score) , fg = accent , bg = background_color , font = (TITLE_FONT , 64)).pack()

        stats_frame = Frame(main_screen , bg = background_color)
        stats_frame.pack(pady = 20)

        # Four figures underneath, each with its heading above the number.
        stats = [["DIFFICULTY" , self.difficulty] , ["CORRECT" , f"{self.correct} of {self.total}"] , ["ACCURACY" , f"{accuracy}%"] , ["TIME" , format_time(self.time_taken)]]

        for heading , value in stats:
            column = Frame(stats_frame , bg = background_color)
            column.pack(side = LEFT , padx = 22)
            Label(column , text = heading , **dim_label , font = SMALL_FONT).pack()
            Label(column , text = value , **page_label , font = (FONT , 19 , "bold")).pack()

        # A bar showing the accuracy, so the number has something to sit against.
        accuracy_bar = ttk.Progressbar(main_screen , orient = "horizontal" , length = 410 , mode = "determinate")
        accuracy_bar["maximum"] = 100
        accuracy_bar["value"] = accuracy
        accuracy_bar.pack(pady = (5 , 20))

        # A line of encouragement chosen from how the race actually went.
        Label(main_screen , text = message , **page_label , font = LABEL_FONT , wraplength = 460 , justify = CENTER).pack()

        button_frame = Frame(main_screen , bg = background_color)
        button_frame.pack(pady = 25)

        again_button = Button(button_frame , text = "Race Again" , **accent_btn , command = lambda: start_race(current_level , current_user) , font = BTN_FONT , width = 16 , height = 2)
        again_button.pack(side = LEFT , padx = 15)

        menu_button = Button(button_frame , text = "← Main Menu" , **plain_btn , command = menu_screen , font = BTN_FONT , width = 16 , height = 2)
        menu_button.pack(side = LEFT , padx = 15)

# Function to call the Race class which is called when the play button is pressed.
def start_race(difficulty , username):
    Race(difficulty , username)

# Saves one finished race onto the end of the records file.
def save_record(difficulty , username , score , seconds):
    filepath = os.path.join(FOLDER , "records.txt")

    with open(filepath , "a" , encoding = "utf-8") as file:
        file.write(f"{difficulty},{username},{score},{seconds}\n")

# Best records function reads every run saved for one difficulty and sorts them highest first.
def best_records(difficulty):
    filepath = os.path.join(FOLDER , "records.txt")

    drivers = []

    try:
        with open(filepath , "r" , encoding = "utf-8") as file:
            for line in file:
                parts = line.strip().split(",")

                # A row is only used when it has all four details, both numbers are numbers and the level matches.
                if len(parts) == 4 and parts[0] == difficulty and parts[2].isdigit() and parts[3].isdigit():
                    drivers.append([parts[1] , int(parts[2]) , int(parts[3])])
    except FileNotFoundError:
        pass

    # Sort the drivers list by the scores from highest to lowest.
    def get_score(player):
        return player[1]

    drivers.sort(key = get_score , reverse = True)

    return drivers[:BOARD_ROWS]

# Reads the saved theme, ignoring the file if it is missing or damaged.
def load_settings():
    global current_theme , answer_mode

    filepath = os.path.join(FOLDER , "settings.txt")

    try:
        with open(filepath , "r" , encoding = "utf-8") as file:
            # The theme is saved on the first line and the way of answering on the second.
            saved = file.read().split("\n")

            if len(saved) > 0 and saved[0].strip() in ["Dark" , "Light"]:
                current_theme = saved[0].strip()

            if len(saved) > 1 and saved[1].strip() in ["Gates" , "Typing"]:
                answer_mode = saved[1].strip()
    except FileNotFoundError:
        pass

# Writes the theme back out, replacing whatever was there before.
def save_settings():
    filepath = os.path.join(FOLDER , "settings.txt")

    with open(filepath , "w" , encoding = "utf-8") as file:
        file.write(f"{current_theme}\n{answer_mode}")

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

# Calling main() to open the sign in screen.
main()

main_screen.mainloop()
