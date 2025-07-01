# Interactive Prompt Window for Python

This package provides a simple way to create separate windows for prompting user input while your Python program is running.

## Files Included

1. `interactive_prompt.py` - The main class that creates an interactive prompt window
2. `simple_prompt_example.py` - A basic example of using the interactive prompt
3. `advanced_prompt_example.py` - An advanced example showing how to use the prompt alongside background tasks
4. `prompt_window.py` - A simpler dialog-based prompt window

## How to Use

### Basic Usage

The simplest way to use the interactive prompt is to run the `simple_prompt_example.py` script:

```bash
python simple_prompt_example.py
```

This will create a window where you can enter text in response to prompts.

### Advanced Usage

For more advanced usage, check out the `advanced_prompt_example.py` script:

```bash
python advanced_prompt_example.py
```

This demonstrates how to:
- Run the prompt window in a separate thread
- Perform background tasks while waiting for user input
- Get user input at different points in your program

### In Your Own Code

To use the interactive prompt in your own code:

1. Import the `InteractivePrompt` class:
   ```python
   from interactive_prompt import InteractivePrompt
   ```

2. Create an instance of the prompt window:
   ```python
   prompt = InteractivePrompt()
   ```

3. Get input from the user:
   ```python
   user_input = prompt.get_input("Enter some text:")
   print(f"User entered: {user_input}")
   ```

4. Close the window when done:
   ```python
   prompt.close()
   ```

For more advanced usage with threading:

```python
import threading
from interactive_prompt import InteractivePrompt

# Create the prompt window
prompt = InteractivePrompt()

# Start the prompt window in a separate thread
prompt_thread = threading.Thread(target=prompt.run)
prompt_thread.daemon = True
prompt_thread.start()

# Now you can get input while your main program continues to run
user_input = prompt.get_input("Enter some text:")
```

## Requirements

- Python 3.x
- tkinter (usually included with Python installations)