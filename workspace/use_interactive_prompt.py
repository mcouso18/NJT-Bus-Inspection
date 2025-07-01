import tkinter as tk
import threading
import time

# Import our interactive prompt class
from interactive_prompt import InteractivePrompt

def main():
    # Create the interactive prompt in a separate thread
    prompt_window = InteractivePrompt()
    prompt_thread = threading.Thread(target=prompt_window.run)
    prompt_thread.daemon = True  # This makes the thread exit when the main program exits
    prompt_thread.start()
    
    # Give the window time to initialize
    time.sleep(1)
    
    # Your main program logic here
    print("Main program is running...")
    
    # Example of getting input from the prompt window
    name = prompt_window.get_input("What is your name?")
    print(f"Hello, {name}!")
    
    age = prompt_window.get_input("How old are you?")
    print(f"You are {age} years old.")
    
    favorite_color = prompt_window.get_input("What is your favorite color?")
    print(f"Your favorite color is {favorite_color}.")
    
    # Close the prompt window when done
    prompt_window.close()
    
    print("Program completed.")

if __name__ == "__main__":
    main()