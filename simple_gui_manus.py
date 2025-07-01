import asyncio
import importlib.util
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk

from PIL import Image, ImageTk


# This will dynamically import your main.py module
def import_main_module(path):
    spec = importlib.util.spec_from_file_location("main_module", path)
    main_module = importlib.util.module_from_spec(spec)
    sys.modules["main_module"] = main_module
    spec.loader.exec_module(main_module)
    return main_module

# Try to find and import the main.py file
main_module = None
main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
if os.path.exists(main_path):
    main_module = import_main_module(main_path)
else:
    print(f"Warning: Could not find main.py at {main_path}")
    print("Please specify the correct path to main.py when running this script")
    print("Example: python simple_gui_manus.py /path/to/main.py")
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        main_module = import_main_module(sys.argv[1])

class SimpleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenManus GUI")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        # Configure the grid layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Configure the main frame's grid
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=0)

        # Create conversation display area
        self.conversation_frame = ttk.Frame(self.main_frame)
        self.conversation_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.conversation_frame.columnconfigure(0, weight=1)
        self.conversation_frame.rowconfigure(0, weight=1)

        # Create scrolled text widget for conversation
        self.conversation_display = scrolledtext.ScrolledText(
            self.conversation_frame, wrap=tk.WORD, state="disabled"
        )
        self.conversation_display.grid(row=0, column=0, sticky="nsew")

        # Create input area frame
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.input_frame.columnconfigure(0, weight=1)

        # Create prompt input area
        self.prompt_input = scrolledtext.ScrolledText(
            self.input_frame, wrap=tk.WORD, height=4
        )
        self.prompt_input.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Create buttons frame
        self.buttons_frame = ttk.Frame(self.input_frame)
        self.buttons_frame.grid(row=1, column=0, sticky="ew")

        # Upload image button
        self.upload_button = ttk.Button(
            self.buttons_frame, text="Upload Image", command=self.upload_image
        )
        self.upload_button.pack(side=tk.LEFT, padx=5)

        # Send button
        self.send_button = ttk.Button(
            self.buttons_frame, text="Send", command=self.send_prompt
        )
        self.send_button.pack(side=tk.RIGHT, padx=5)

        # Clear button
        self.clear_button = ttk.Button(
            self.buttons_frame, text="Clear", command=self.clear_input
        )
        self.clear_button.pack(side=tk.RIGHT, padx=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.grid(row=1, column=0, sticky="ew")

        # Image preview frame (initially hidden)
        self.image_preview_frame = ttk.LabelFrame(self.input_frame, text="Image Preview")
        self.image_label = ttk.Label(self.image_preview_frame)
        self.image_label.pack(padx=5, pady=5)

        # Bind Enter key to send message
        self.prompt_input.bind("<Control-Return>", lambda event: self.send_prompt())

        # Initialize variables
        self.loop = asyncio.new_event_loop()
        self.agent = None
        self.uploaded_image_path = None
        self.thumbnail = None

        # Start the asyncio event loop in a separate thread
        self.thread = threading.Thread(target=self._start_background_loop, daemon=True)
        self.thread.start()

        # Initialize the agent
        self.root.after(100, self._initialize_agent)

    def _start_background_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _initialize_agent(self):
        """Initialize the Manus agent asynchronously."""
        async def init_agent():
            try:
                # Import from the main module if available
                if main_module and hasattr(main_module, 'Manus'):
                    Manus = getattr(main_module, 'Manus')
                    self.agent = await Manus.create()
                    self.status_var.set("Agent initialized and ready")
                else:
                    self.status_var.set("Warning: Could not initialize agent from main.py")
            except Exception as e:
                self.status_var.set(f"Error initializing agent: {str(e)}")
                print(f"Error initializing agent: {str(e)}")

        asyncio.run_coroutine_threadsafe(init_agent(), self.loop)

    def upload_image(self):
        """Handle image upload."""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            try:
                # Save the path for sending with the prompt
                self.uploaded_image_path = file_path

                # Create a thumbnail for preview
                img = Image.open(file_path)
                img.thumbnail((200, 200))  # Resize for preview
                self.thumbnail = ImageTk.PhotoImage(img)

                # Update the image preview
                self.image_label.configure(image=self.thumbnail)
                self.image_preview_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

                self.status_var.set(f"Image uploaded: {os.path.basename(file_path)}")

                # Add to conversation display
                self._add_to_display("System", f"Image uploaded: {os.path.basename(file_path)}")
            except Exception as e:
                self.status_var.set(f"Error loading image: {str(e)}")

    def clear_input(self):
        """Clear the input area and image preview."""
        self.prompt_input.delete(1.0, tk.END)
        self.uploaded_image_path = None
        self.image_preview_frame.grid_forget()
        self.status_var.set("Input cleared")

    def send_prompt(self):
        """Send the prompt to the agent."""
        prompt = self.prompt_input.get(1.0, tk.END).strip()

        if not prompt:
            self.status_var.set("Please enter a prompt")
            return

        # Disable the send button while processing
        self.send_button.configure(state="disabled")
        self.status_var.set("Processing request...")

        # Add user message to conversation display
        self._add_to_display("You", prompt)

        # Process the request asynchronously
        asyncio.run_coroutine_threadsafe(
            self._process_request(prompt, self.uploaded_image_path),
            self.loop
        )

        # Clear the input area after sending
        self.prompt_input.delete(1.0, tk.END)
        self.uploaded_image_path = None
        self.image_preview_frame.grid_forget()

    async def _process_request(self, prompt, image_path=None):
        """Process the request asynchronously by calling the main module's run function."""
        try:
            if self.agent:
                if image_path:
                    # Call the image analysis function directly
                    if main_module and hasattr(main_module, 'analyze_image_with_prompt'):
                        await main_module.analyze_image_with_prompt(self.agent, image_path, prompt)
                        self.root.after(0, lambda: self._add_to_display(
                            "System", f"Image analysis request sent for {os.path.basename(image_path)}"
                        ))
                    else:
                        self.root.after(0, lambda: self._add_to_display(
                            "System", "Error: analyze_image_with_prompt not found in main.py"
                        ))
                else:
                    # Regular text prompt
                    await self.agent.run(prompt)

                    # Since the original main.py might not return a response,
                    # we'll add a generic confirmation
                    self.root.after(0, lambda: self._add_to_display(
                        "System", "Text prompt processed by Manus agent"
                    ))
            else:
                self.root.after(0, lambda: self._add_to_display(
                    "System", "Agent not initialized. Please check main.py path."
                ))
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            self.root.after(0, lambda: self._add_to_display("System", error_msg))
            print(error_msg)
        finally:
            # Re-enable the send button
            self.root.after(0, lambda: self.send_button.configure(state="normal"))
            self.root.after(0, lambda: self.status_var.set("Ready"))

    def _add_to_display(self, sender, message):
        """Add a message to the conversation display."""
        # Enable the text widget for editing
        self.conversation_display.configure(state="normal")

        # Add a separator if there are already messages
        if self.conversation_display.get(1.0, tk.END).strip():
            self.conversation_display.insert(tk.END, "\n\n")

        # Add timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        if sender == "You":
            self.conversation_display.insert(tk.END, f"[{timestamp}] {sender}: ", "user")
        elif sender == "System":
            self.conversation_display.insert(tk.END, f"[{timestamp}] {sender}: ", "system")
        else:
            self.conversation_display.insert(tk.END, f"[{timestamp}] {sender}: ", "agent")

        self.conversation_display.insert(tk.END, message)

        # Configure tags for different message types
        self.conversation_display.tag_configure("user", foreground="blue")
        self.conversation_display.tag_configure("agent", foreground="green")
        self.conversation_display.tag_configure("system", foreground="red")

        # Disable the text widget again
        self.conversation_display.configure(state="disabled")

        # Scroll to the bottom
        self.conversation_display.see(tk.END)

    async def cleanup(self):
        """Clean up resources before closing."""
        if self.agent:
            try:
                await self.agent.cleanup()
            except Exception as e:
                print(f"Error during cleanup: {str(e)}")


def main():
    # Check if a custom path to main.py was provided
    if len(sys.argv) > 1 and not os.path.exists(sys.argv[1]):
        print(f"Error: Could not find main.py at {sys.argv[1]}")
        print("Please provide the correct path to main.py")
        return

    root = tk.Tk()
    app = SimpleGUI(root)

    # Handle window close event
    def on_closing():
        # Stop the asyncio event loop
        app.loop.call_soon_threadsafe(app.loop.stop)

        # Run cleanup in a separate thread to avoid blocking
        cleanup_thread = threading.Thread(
            target=lambda: asyncio.run(app.cleanup())
        )
        cleanup_thread.start()
        cleanup_thread.join(timeout=1.0)  # Wait for cleanup with timeout

        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
