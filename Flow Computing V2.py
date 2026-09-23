from tkinter import *
from tkinter import messagebox
import tkinter as tk
import random
import hashlib
import secrets
from PIL import Image, ImageTk



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

# The tick symbol that shows which difficulty has been picked.
TICK = "✓"

# How far the bike moves each keypress on each difficulty, so harder is faster.
SPEEDS = {"Easy": 10, "Medium": 20, "Hard": 30}

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
            messagebox.showerror("Cannot Create Account", problem)
            return

        # Stop the user taking a username that somebody else already has.
        accounts = load_accounts()
        if username in accounts:
            messagebox.showerror("Cannot Create Account", "The username " + username + " is already taken. Please choose a different username.")
            return

        # Apply the length, number and capital letter rules.
        problem = check_password(password)
        if problem != "":
            messagebox.showerror("Cannot Create Account", problem)
            return

        # Make sure the two password boxes were typed the same.
        if confirm != password:
            messagebox.showerror("Cannot Create Account", "Your two passwords do not match. Please type exactly the same password into both boxes.")
            return

        # Save the account with a scrambled password instead of the real one.
        salt = secrets.token_hex(SALT_LENGTH)
        save_account(username, salt, hash_password(password, salt))
        messagebox.showinfo("Account Created", "Welcome " + username + ". Your account has been saved, so next time you can just sign in.")
        open_menu(username)

    # Function for the sign in button.
    def sign_in():
        username = username_entry.get()
        password = password_entry.get()

        if username == "":
            messagebox.showerror("Cannot Sign In", "You have not typed a username. Please type the username you signed up with.")
            return

        if password == "":
            messagebox.showerror("Cannot Sign In", "You have not typed a password. Please type the password you signed up with.")
            return

        # Reload from disk each time, so an account made this session is found.
        accounts = load_accounts()
        if username not in accounts:
            messagebox.showerror("Cannot Sign In", "There is no account saved with the username " + username + ". Please check your spelling, or use Create an account instead to make a new one.")
            return

        # Scramble what was typed and compare it against the scrambled password saved.
        salt, scrambled = accounts[username]
        if hash_password(password, salt) != scrambled:
            messagebox.showerror("Cannot Sign In", "That password does not match the one saved for " + username + ". Please try typing it again.")
            return

        messagebox.showinfo("Signed In", "Welcome back " + username + ".")
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
    print("Hi")

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
    difficulty_txt = difficulty_canvas.create_text(325, 60, text="DIFFICULTY", font=("font", 50, "bold"), fill="white")

    # Set up the three ticks. show_tick fills the correct one in below.
    easy_tick = difficulty_canvas.create_text(460, 220, text="", font=("font", 40, "bold"), fill="green")
    medium_tick = difficulty_canvas.create_text(460, 330, text="", font=("font", 40, "bold"), fill="green")
    hard_tick = difficulty_canvas.create_text(460, 440, text="", font=("font", 40, "bold"), fill="green")

    # Wipe every tick so that only one difficulty is ever ticked at a time.
    def clear_ticks():
        difficulty_canvas.itemconfig(easy_tick, text="")
        difficulty_canvas.itemconfig(medium_tick, text="")
        difficulty_canvas.itemconfig(hard_tick, text="")

    # Put the tick back on whichever difficulty is currently saved.
    def show_tick():
        clear_ticks()
        if difficulty_picked == "Easy":
            difficulty_canvas.itemconfig(easy_tick, text=TICK)
        elif difficulty_picked == "Medium":
            difficulty_canvas.itemconfig(medium_tick, text=TICK)
        else:
            difficulty_canvas.itemconfig(hard_tick, text=TICK)

    # Function for the easy button.
    def easy():
        global difficulty_picked
        difficulty_picked = "Easy"
        show_tick()

    # Function for the medium button.
    def medium():
        global difficulty_picked
        difficulty_picked = "Medium"
        show_tick()

    # Function for the hard button.
    def hard():
        global difficulty_picked
        difficulty_picked = "Hard"
        show_tick()

    # Function for the back button, which closes this window and brings the menu back.
    def back():
        difficulty_win.destroy()
        root.deiconify()

    # Set up the three difficulty buttons.
    easy_btn = Button(difficulty_win, text="Easy", font=("font", 12), width=14, height=2, command=easy)
    easy_win = difficulty_canvas.create_window(300, 220, anchor=CENTER, window=easy_btn)
    medium_btn = Button(difficulty_win, text="Medium", font=("font", 12), width=14, height=2, command=medium)
    medium_win = difficulty_canvas.create_window(300, 330, anchor=CENTER, window=medium_btn)
    hard_btn = Button(difficulty_win, text="Hard", font=("font", 12), width=14, height=2, command=hard)
    hard_win = difficulty_canvas.create_window(300, 440, anchor=CENTER, window=hard_btn)

    # Set up the back button, using the arrow image next to the word Back.
    back_btn = Button(difficulty_win, text=" Back", font=("font", 12), image=back_img, compound=LEFT, command=back)
    back_win = difficulty_canvas.create_window(100, 580, anchor=CENTER, window=back_btn)

    # Send the window X button through the back function so the menu cannot get stranded.
    difficulty_win.protocol("WM_DELETE_WINDOW", back)

    # Show the saved difficulty as soon as the window opens.
    show_tick()




# Set up buttons for main menu.
play_btn = Button(root, text="Play", font=("font", 12), width=25, height=3, command=bike)
play = canvas.create_window(350, 350, anchor=CENTER, window=play_btn)
quit_btn = Button(root, text="Quit", font=("font", 12), width=14, command=quit)
quit = canvas.create_window(500, 525, anchor=CENTER, window=quit_btn)
leaderboard_btn = Button(root, text="Leaderboard", font=("font", 12), width=14, command=leaderboard)
leaderboard = canvas.create_window(500, 225, anchor=CENTER, window=leaderboard_btn)
settings_btn = Button(root, text="Setting", font=("font", 12), width=14, command=settings)
settings = canvas.create_window(200, 225, anchor=CENTER, window=settings_btn)
difficulty_btn = Button(root, text="Difficulty", font=("font", 12), width=14, command=difficulty)
difficulty = canvas.create_window(200, 525, anchor=CENTER, window=difficulty_btn)




# Hide the main menu and make the user sign in before they can reach it.
root.withdraw()
login()

root.mainloop()