from tkinter import *
import tkinter as tk
import random
from PIL import Image, ImageTk



# Set up the main window and resize it.
root = tk.Tk()
root.title("Math Racer")
root.geometry("700x700")


# Set up the canvas widget.
canvas = Canvas(root, width = 650, height = 650, bg = "black")
canvas.pack(pady = 5)
main_txt = canvas.create_text(340, 50, text="MATH RACER", font=("font", 70, "bold"), fill="white")

# Open and resize bike image.
bike = Image.open(("Bike.png"))
resize_bike = bike.resize((100, 100))
bike_img = ImageTk.PhotoImage(resize_bike)

font = "Impact"

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
    move_distance = 10

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

    difficulty_win = tk.Toplevel(root)
    difficulty_win.title("Difficulty Window")
    difficulty_win.geometry("700x700")

    root.destroy()




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