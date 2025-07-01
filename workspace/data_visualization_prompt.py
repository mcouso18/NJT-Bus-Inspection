import sys
import os
import threading
import time
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

# Add parent directory to path to import InteractivePrompt
parent_dir = os.path.dirname(os.getcwd())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from interactive_prompt import InteractivePrompt

class DataVisualizationPrompt(InteractivePrompt):
    def __init__(self):
        # Initialize the parent class
        super().__init__()
        
        # Resize the window to accommodate the visualization
        self.root.geometry("800x600")
        self.root.title("Data Visualization Prompt")
        
        # Create a frame for the visualization
        self.viz_frame = ttk.Frame(self.root)
        self.viz_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create a matplotlib figure
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize with empty data
        self.data = []
        self.update_plot()
        
        # Add buttons for data operations
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(fill=tk.X, pady=5)
        
        self.add_data_button = ttk.Button(self.button_frame, text="Add Random Data", 
                                         command=self.add_random_data)
        self.add_data_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(self.button_frame, text="Clear Data", 
                                      command=self.clear_data)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Modify the existing widgets
        self.label.config(text="Enter a command or data value:")
        
    def update_plot(self):
        """Update the plot with current data"""
        self.ax.clear()
        if self.data:
            self.ax.plot(range(len(self.data)), self.data, 'b-o')
            self.ax.set_title(f"Data Points: {len(self.data)}")
            self.ax.set_xlabel("Index")
            self.ax.set_ylabel("Value")
            self.ax.grid(True)
        else:
            self.ax.set_title("No Data Available")
            self.ax.text(0.5, 0.5, "Use 'Add Random Data' or enter values", 
                        horizontalalignment='center', verticalalignment='center',
                        transform=self.ax.transAxes)
        
        self.canvas.draw()
    
    def add_random_data(self):
        """Add random data points to the plot"""
        for _ in range(5):
            self.data.append(random.uniform(0, 100))
        self.update_plot()
        
    def clear_data(self):
        """Clear all data points"""
        self.data = []
        self.update_plot()
        
    def submit(self):
        """Override submit to handle data input"""
        input_text = self.entry.get()
        self.result = input_text
        self.result_label.config(text=f"Submitted: {input_text}")
        
        # Try to parse as a number and add to data
        try:
            value = float(input_text)
            self.data.append(value)
            self.update_plot()
            self.result_label.config(text=f"Added value: {value}")
        except ValueError:
            # Handle as a command
            if input_text.lower() == "clear":
                self.clear_data()
                self.result_label.config(text="Data cleared")
            elif input_text.lower() == "random":
                self.add_random_data()
                self.result_label.config(text="Added random data")
        
        self.submitted.set(True)
        self.entry.delete(0, tk.END)  # Clear the entry field

def main():
    print("Starting the data visualization prompt...")
    
    # Create the enhanced prompt window
    prompt = DataVisualizationPrompt()
    
    # Start the prompt in a separate thread
    prompt_thread = threading.Thread(target=prompt.run)
    prompt_thread.daemon = True
    prompt_thread.start()
    
    # Simulate some background processing
    for i in range(3):
        print(f"Background process running... ({i+1}/3)")
        time.sleep(1)
    
    # Get input from the user
    name = prompt.get_input("What's your name?")
    print(f"Hello, {name}!")
    
    # Prompt for data analysis preference
    analysis_type = prompt.get_input("What type of data would you like to analyze? (random/custom)")
    
    if analysis_type.lower() == "random":
        print("Generating random data...")
        prompt.add_random_data()
    else:
        value = prompt.get_input("Enter a numeric value to add to the plot:")
        try:
            prompt.data.append(float(value))
            prompt.update_plot()
        except ValueError:
            print("Invalid numeric value. Using random data instead.")
            prompt.add_random_data()
    
    # Let the user interact with the visualization
    prompt.get_input("Interact with the visualization. Type 'continue' when done.")
    
    # Final message
    prompt.get_input("Press Enter to close the application.")
    
    # Close the window
    prompt.close()
    print("Application closed.")

if __name__ == "__main__":
    main()