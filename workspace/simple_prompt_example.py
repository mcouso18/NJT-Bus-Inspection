from interactive_prompt import InteractivePrompt

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