"""
A self-contained script that demonstrates how to use dialog boxes for prompting in Python.
Run this script directly to see the dialog boxes in action.
"""

import tkinter as tk
from tkinter import simpledialog

def main():
    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    print("Starting the dialog prompt example...")
    
    # First dialog
    name = simpledialog.askstring("Name Input", "What is your name?")
    if name:
        print(f"Hello, {name}!")
    else:
        print("You didn't enter a name.")
    
    # Second dialog
    age = simpledialog.askinteger("Age Input", "How old are you?")
    if age:
        print(f"You are {age} years old.")
    else:
        print("You didn't enter your age.")
    
    # Third dialog
    favorite_color = simpledialog.askstring("Color Input", "What is your favorite color?")
    if favorite_color:
        print(f"Your favorite color is {favorite_color}.")
    else:
        print("You didn't enter a favorite color.")
    
    # Clean up
    root.destroy()
    
    print("Example completed!")

if __name__ == "__main__":
    main()