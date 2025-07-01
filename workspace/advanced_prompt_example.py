import threading
import time
from interactive_prompt import InteractivePrompt

def background_task():
    """A function that simulates a long-running background task"""
    for i in range(10):
        print(f"Background task: step {i+1}/10")
        time.sleep(1)
    print("Background task completed!")

def main():
    print("Starting the advanced interactive prompt example...")
    
    # Create the prompt window
    prompt = InteractivePrompt()
    
    # Start the prompt window in a separate thread
    prompt_thread = threading.Thread(target=prompt.run)
    prompt_thread.daemon = True  # This makes the thread exit when the main program exits
    prompt_thread.start()
    
    # Give the window time to initialize
    time.sleep(0.5)
    
    # Start a background task
    bg_thread = threading.Thread(target=background_task)
    bg_thread.start()
    
    # While the background task is running, we can still get user input
    name = prompt.get_input("What is your name?")
    print(f"Hello, {name}!")
    
    # Wait for the background task to complete
    bg_thread.join()
    
    # Get more input after the background task is done
    feedback = prompt.get_input("How was your experience with this program?")
    print(f"User feedback: {feedback}")
    
    # Close the window when done
    prompt.close()
    
    print("Advanced example completed!")

if __name__ == "__main__":
    main()