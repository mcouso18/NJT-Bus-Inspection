"""
This script demonstrates how to use tkinter's simpledialog for prompting.
This is a simpler alternative that doesn't require a persistent window.
"""

import tkinter as tk
from tkinter import simpledialog

def get_input(prompt="Enter your input:", title="Input Dialog"):
    """
    Show a dialog box to get user input
    
    Args:
        prompt (str): The prompt text to display
        title (str): The title of the dialog box
        
    Returns:
        str: The user's input, or None if canceled
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    # Show the dialog and get input
    result = simpledialog.askstring(title, prompt)
    
    # Clean up
    root.destroy()
    
    return result

def main():
    print("Starting the simple dialog example...")
    
    # Get some input from the user
    name = get_input("What is your name?", "Name Input")
    print(f"You entered: {name}")
    
    # Get more input
    favorite_language = get_input("What is your favorite programming language?", "Language Input")
    print(f"Your favorite programming language is: {favorite_language}")
    
    print("Example completed!")

if __name__ == "__main__":
    main()