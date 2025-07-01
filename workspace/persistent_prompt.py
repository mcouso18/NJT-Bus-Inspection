"""
A self-contained script that demonstrates how to use a persistent prompt window in Python.
This window stays open while your program runs, allowing for input at any time.
"""

import tkinter as tk
import threading
import time

class PromptWindow:
    def __init__(self):
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Persistent Prompt Window")
        self.root.geometry("500x300")
        
        # Create the widgets
        self.title_label = tk.Label(self.root, text="Persistent Prompt Window", font=("Arial", 16))
        self.title_label.pack(pady=10)
        
        self.prompt_label = tk.Label(self.root, text="Enter your input below:", font=("Arial", 12))
        self.prompt_label.pack(pady=5)
        
        self.entry = tk.Entry(self.root, width=50)
        self.entry.pack(pady=10)
        
        self.submit_button = tk.Button(self.root, text="Submit", command=self.submit)
        self.submit_button.pack(pady=5)
        
        self.status_label = tk.Label(self.root, text="Status: Ready", font=("Arial", 10))
        self.status_label.pack(pady=10)
        
        # Variables for tracking input
        self.input_value = None
        self.input_ready = tk.BooleanVar(value=False)
    
    def submit(self):
        """Handle the submit button click"""
        self.input_value = self.entry.get()
        self.status_label.config(text=f"Status: Submitted - '{self.input_value}'")
        self.input_ready.set(True)
        self.entry.delete(0, tk.END)  # Clear the entry
    
    def get_input(self, prompt_text="Enter your input:"):
        """Get input from the user"""
        # Update the prompt text
        self.prompt_label.config(text=prompt_text)
        self.status_label.config(text="Status: Waiting for input...")
        
        # Reset the input state
        self.input_value = None
        self.input_ready.set(False)
        
        # Wait for input
        self.root.wait_variable(self.input_ready)
        
        return self.input_value
    
    def start(self):
        """Start the window's main loop"""
        self.root.mainloop()
    
    def close(self):
        """Close the window"""
        self.root.destroy()

def background_task(status_callback):
    """A function that simulates a background task"""
    for i in range(5):
        status_callback(f"Background task: step {i+1}/5")
        time.sleep(2)
    status_callback("Background task completed!")

def main():
    print("Starting the persistent prompt window example...")
    
    # Create the prompt window
    prompt = PromptWindow()
    
    # Start the window in a separate thread
    window_thread = threading.Thread(target=prompt.start)
    window_thread.daemon = True  # This makes the thread exit when the main program exits
    window_thread.start()
    
    # Give the window time to initialize
    time.sleep(0.5)
    
    # Get initial input
    name = prompt.get_input("What is your name?")
    print(f"Hello, {name}!")
    
    # Start a background task
    def update_status(message):
        print(message)
    
    bg_thread = threading.Thread(target=background_task, args=(update_status,))
    bg_thread.start()
    
    # While the background task is running, we can still get more input
    favorite_food = prompt.get_input("What is your favorite food?")
    print(f"Your favorite food is {favorite_food}.")
    
    # Wait for the background task to complete
    bg_thread.join()
    
    # Get final input
    feedback = prompt.get_input("How was your experience with this program?")
    print(f"Your feedback: {feedback}")
    
    # Close the window
    prompt.close()
    
    print("Example completed!")

if __name__ == "__main__":
    main()