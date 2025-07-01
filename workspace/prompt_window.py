import tkinter as tk
from tkinter import simpledialog

class PromptWindow:
    def __init__(self, root=None):
        # Create a root window if not provided
        if root is None:
            self.root = tk.Tk()
            self.root.withdraw()  # Hide the main window
        else:
            self.root = root
            
    def get_input(self, title="Input", prompt="Enter your prompt:"):
        """Show a dialog window to get user input"""
        result = simpledialog.askstring(title, prompt)
        return result
        
    def close(self):
        """Close the window"""
        self.root.destroy()

# Example usage
if __name__ == "__main__":
    prompt_window = PromptWindow()
    
    # Get user input
    user_input = prompt_window.get_input("Python Prompt", "Enter your command or text:")
    
    # Do something with the input
    if user_input:
        print(f"You entered: {user_input}")
    else:
        print("No input provided")
    
    # You can ask for multiple inputs
    another_input = prompt_window.get_input("Another Prompt", "Enter more text:")
    if another_input:
        print(f"You entered: {another_input}")
        
    # Close the window when done
    prompt_window.close()