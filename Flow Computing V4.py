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



# Set up the main window and resize it.
root = tk.Tk()
root.title("Math Racer")
root.geometry("700x700")


# Set up the canvas widget.
canvas = Canvas(root, width = 650, height = 650, bg = "yellow")
canvas.pack(pady = 5)
main_txt = canvas.create_text(340, 50, text="MATH RACER", font=("font", 70, "bold"), fill="white")
user_txt = canvas.create_text(325, 620, text="", font=("font", 12), fill="white")

# Open and resize bike image.
bike = Image.open(("Bike.png"))
resize_bike = bike.resize((100, 100))
bike_img = ImageTk.PhotoImage(resize_bike)

# Open and resize back arrow image.
back = Image.open(("Back.png"))
resize_back = back.resize((25, 25))
back_img = ImageTk.PhotoImage(resize_back)

font = "Impact"

# How far the bike moves each keypress on each difficulty, so harder is faster.
SPEEDS = {"Easy": 10, "Medium": 20, "Hard": 30}

# The speedometer that the difficulty window is drawn as.
GAUGE_X = 325
GAUGE_Y = 395
GAUGE_RADIUS = 170
GAUGE_BAND = 24
NEEDLE_LENGTH = 132

# Where the needle points for each difficulty, in degrees round the gauge.
# 180 is due left and 0 is due right, so Easy sits low and Hard sits high.
NEEDLE_ANGLES = {"Easy": 150, "Medium": 90, "Hard": 30}

# Darker shades than a real dashboard would use, because pale colours are
# hard to read against the yellow background.
ZONE_COLOURS = {"Easy": "#1b7a3d", "Medium": "#c26a00", "Hard": "#a01818"}

# Where each band's wording sits, placed by hand so it clears the dial.
LABEL_SPOTS = {"Easy": (145, 285, E), "Medium": (325, 170, S), "Hard": (505, 285, W)}

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

# Function for the sign in window, which opens before the main menu.
def login():

    # Default to sign in, since returning users outnumber new ones.
    global login_mode
    login_mode = "Sign In"

    login_win = tk.Toplevel(root)
    login_win.title("Sign In")
    login_win.geometry("700x700")

    # Set up the canvas widget for the sign in window.
    login_canvas = Canvas(login_win, width=650, height=650, bg="yellow")
    login_canvas.pack(pady=5)
    title_txt = login_canvas.create_text(325, 70, text="SIGN IN", font=("font", 45, "bold"), fill="white")

    # Set up the username label and entry box.
    username_txt = login_canvas.create_text(230, 200, text="Username", font=("font", 14, "bold"), fill="white", anchor=E)
    username_entry = Entry(login_win, font=("font", 14), width=20)
    username_win = login_canvas.create_window(250, 200, anchor=W, window=username_entry)

    # Set up the password label and entry box, hiding the letters as they are typed.
    password_txt = login_canvas.create_text(230, 260, text="Password", font=("font", 14, "bold"), fill="white", anchor=E)
    password_entry = Entry(login_win, font=("font", 14), width=20, show="*")
    password_win = login_canvas.create_window(250, 260, anchor=W, window=password_entry)

    # Set up the confirm password row, which is only needed when making an account.
    confirm_txt = login_canvas.create_text(230, 320, text="Confirm Password", font=("font", 14, "bold"), fill="white", anchor=E)
    confirm_entry = Entry(login_win, font=("font", 14), width=20, show="*")
    confirm_win = login_canvas.create_window(250, 320, anchor=W, window=confirm_entry)

    # Password rules, shown only while an account is being created.
    rules_txt = login_canvas.create_text(325, 380, text=PASSWORD_RULES, font=("font", 10), fill="white", width=420)

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
    action_btn = Button(login_win, text="Sign In", font=("font", 12), width=20, height=2, command=sign_in)
    action_win = login_canvas.create_window(325, 450, anchor=CENTER, window=action_btn)

    # Set up the button that swaps between the two modes.
    switch_btn = Button(login_win, text="Create an account instead", font=("font", 10), width=24, command=switch_mode)
    switch_win = login_canvas.create_window(325, 520, anchor=CENTER, window=switch_btn)

    # Closing this window with the X quits, because the menu is hidden behind it.
    login_win.protocol("WM_DELETE_WINDOW", root.destroy)

    # Draw the form before the window is shown.
    update_form()

# Function for bike
def bike():

    # Destroy all main menu buttons.
    play_btn.destroy()
    quit_btn.destroy()
    leaderboard_btn.destroy()
    settings_btn.destroy()
    difficulty_btn.destroy()
    canvas.delete(main_txt)
        
    # Add bike image.
    img = canvas.create_image(200,450, anchor=CENTER, image=bike_img)

# Allow the bike to move using keybind
    move_distance = SPEEDS[difficulty_picked]

    def left(event):
        canvas.move(img, - move_distance, 0)

    def right(event):
        canvas.move(img, move_distance, 0)

    def up(event):
        canvas.move(img, 0, -move_distance)

    def down(event):
        canvas.move(img, 0, move_distance)

    root.bind("<Left>", left)
    root.bind("<Right>", right)
    root.bind("<Up>", up)
    root.bind("<Down>", down)
    root.focus_set()

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
    settings_canvas = Canvas(settings_win, width=650, height=650, bg="yellow")
    settings_canvas.pack(pady=5)
    settings_txt = settings_canvas.create_text(325, 60, text="SETTINGS", font=("font", 50, "bold"), fill="white")

    # Set up the sound row, ticked when sound is currently switched on.
    sound_txt = settings_canvas.create_text(280, 210, text="Sound", font=("font", 14, "bold"), fill="white", anchor=E)
    sound_value = IntVar(settings_win, value=int(sound_on))
    sound_check = Checkbutton(settings_win, text="On", font=("font", 12), variable=sound_value)
    sound_win = settings_canvas.create_window(300, 210, anchor=W, window=sound_check)

    # Set up the questions per race box, the one setting that is typed in.
    questions_txt = settings_canvas.create_text(280, 300, text="Questions per race", font=("font", 14, "bold"), fill="white", anchor=E)
    questions_entry = Entry(settings_win, font=("font", 14), width=6)
    questions_win = settings_canvas.create_window(300, 300, anchor=W, window=questions_entry)
    questions_entry.insert(0, str(questions_per_race))

    # Set up the small text explaining what the box will accept.
    questions_rule_txt = settings_canvas.create_text(325, 350, text="Choose a whole number between " + str(QUESTIONS_MIN) + " and " + str(QUESTIONS_MAX) + ".", font=("font", 10), fill="white")

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
    save_btn = Button(settings_win, text="Save", font=("font", 12), width=14, height=2, command=save)
    save_win = settings_canvas.create_window(450, 470, anchor=CENTER, window=save_btn)
    back_btn = Button(settings_win, text=" Back", font=("font", 12), image=back_img, compound=LEFT, command=back)
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
    difficulty_canvas = Canvas(difficulty_win, width=650, height=650, bg="yellow")
    difficulty_canvas.pack(pady=5)
    difficulty_txt = difficulty_canvas.create_text(325, 55, text="DIFFICULTY", font=("font", 50, "bold"), fill="white")

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
        difficulty_canvas.create_text(spot_x, spot_y, text=level.upper(), font=("font", 19, "bold"), fill=ZONE_COLOURS[level], anchor=spot_anchor)
        difficulty_canvas.create_text(spot_x, spot_y + 23, text="Speed " + str(SPEEDS[level]), font=("font", 11), fill="black", anchor=spot_anchor)

    # Draw the needle straight up for now. show_needle swings it round below.
    needle = difficulty_canvas.create_line(GAUGE_X, GAUGE_Y, GAUGE_X, GAUGE_Y - NEEDLE_LENGTH, width=6, fill="black", arrow=LAST, arrowshape=(18, 22, 7))
    hub = difficulty_canvas.create_oval(GAUGE_X - 14, GAUGE_Y - 14, GAUGE_X + 14, GAUGE_Y + 14, fill="black", outline="white", width=3)

    # The wording under the dial that spells out what the needle is pointing at.
    chosen_txt = difficulty_canvas.create_text(325, 450, text="", font=("font", 17, "bold"), fill="black")

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
    easy_btn = Button(difficulty_win, text="Easy", font=("font", 12), width=11, height=2, command=easy)
    easy_win = difficulty_canvas.create_window(120, 520, anchor=CENTER, window=easy_btn)
    medium_btn = Button(difficulty_win, text="Medium", font=("font", 12), width=11, height=2, command=medium)
    medium_win = difficulty_canvas.create_window(325, 520, anchor=CENTER, window=medium_btn)
    hard_btn = Button(difficulty_win, text="Hard", font=("font", 12), width=11, height=2, command=hard)
    hard_win = difficulty_canvas.create_window(530, 520, anchor=CENTER, window=hard_btn)

    # Set up the back button, using the arrow image next to the word Back.
    back_btn = Button(difficulty_win, text=" Back", font=("font", 12), image=back_img, compound=LEFT, command=back)
    back_win = difficulty_canvas.create_window(110, 600, anchor=CENTER, window=back_btn)

    # Send the window X button through the back function so the menu cannot get stranded.
    difficulty_win.protocol("WM_DELETE_WINDOW", back)

    # Sweep the needle round to the saved difficulty as the window opens.
    show_needle()



# Set up buttons for main menu.
play_btn = Button(root, text="Play", font=("font", 12), width=25, height=3, command=bike)
menu_play_win = canvas.create_window(350, 350, anchor=CENTER, window=play_btn)
quit_btn = Button(root, text="Quit", font=("font", 12), width=14, command=quit)
menu_quit_win = canvas.create_window(500, 525, anchor=CENTER, window=quit_btn)
leaderboard_btn = Button(root, text="Leaderboard", font=("font", 12), width=14, command=leaderboard)
menu_leaderboard_win = canvas.create_window(500, 225, anchor=CENTER, window=leaderboard_btn)
settings_btn = Button(root, text="Setting", font=("font", 12), width=14, command=settings)
menu_settings_win = canvas.create_window(200, 225, anchor=CENTER, window=settings_btn)
difficulty_btn = Button(root, text="Difficulty", font=("font", 12), width=14, command=difficulty)
menu_difficulty_win = canvas.create_window(200, 525, anchor=CENTER, window=difficulty_btn)




# Load the saved settings before the menu is shown.
load_settings()

# Hide the main menu and make the user sign in before they can reach it.
root.withdraw()
login()

root.mainloop()