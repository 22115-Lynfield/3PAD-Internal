from tkinter import *
import tkinter as tk
import random
from PIL import Image, ImageTk



# Set up the main window and resize it.
root = tk.Tk()
root.title("Math Racer")
root.geometry("700x700")


# Set up the canvas widget.
canvas = Canvas(root, width = 650, height = 650, bg = "yellow")
canvas.pack(pady = 5)
main_txt = canvas.create_text(340, 50, text="MATH RACER", font=("font", 70, "bold"), fill="white")

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

    # Set up the ticks, which start empty because nothing is picked yet.
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




root.mainloop()