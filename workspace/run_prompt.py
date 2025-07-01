"""
This script demonstrates how to use a separate window for prompting in Python.
Run this script directly to see the interactive prompt window in action.
"""

import tkinter as tk
from tkinter import simpledialog

class InteractivePrompt:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Interactive Prompt")
        self.root.geometry("400x200")
        
        # Create widgets
        self.label = tk.Label(self.root, text="Enter your command below:")
        self.label.pack(pady=10)
        
        self.entry = tk.Entry(self.root, width=50)
        self.entry.pack(pady=10)
        
        self.submit_button = tk.Button(self.root, text="Submit", command=self.submit)
        self.submit_button.pack(pady=10)
        
        self.result_label = tk.Label(self.root, text="")
        self.result_label.pack(pady=10)
        
        # Variable to store the result
        self.result = None
        self.submitted = tk.BooleanVar(value=False)
        
    def submit(self):
        self.result = self.entry.get()
        self.result_label.config(text=f"Submitted: {self.result}")
        self.submitted.set(True)
        self.entry.delete(0, tk.END)  # Clear the entry field
        
    def get_input(self, prompt_text="Enter your command:"):
        """Get input from the user"""
        self.label.config(text=prompt_text)
        self.submitted.set(False)
        self.result = None
        self.result_label.config(text="")
        
        # Wait for submission
        self.root.wait_variable(self.submitted)
        return self.result
        
    def run(self):
        """Start the main loop"""
        self.root.mainloop()
        
    def close(self):
        """Close the window"""
        self.root.destroy()

def main():
    print("Starting the interactive prompt example...")
    
    # Create the prompt window
    prompt = InteractivePrompt()
    
    # Get some input from the user
    name = prompt.get_input("What is your name?")
    print(f"You entered: {name}")
    
    # Get more input
    favorite_language = prompt.get_input("What is your favorite programming language?")
    print(f"Your favorite programming language is: {favorite_language}")
    
    # Close the window when done
    prompt.close()
    
    print("Example completed!")

if __name__ == "__main__":
    main()