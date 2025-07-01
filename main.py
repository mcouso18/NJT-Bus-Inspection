import asyncio
import base64
import os
from pathlib import Path

from app.agent.manus import Manus
from app.logger import logger
from interactive_prompt import InteractivePrompt


async def analyze_image_with_prompt(agent, image_path: str, text_prompt: str = None):
    """
    Analyze an image using the Manus agent with Claude's vision capabilities

    Args:
        agent: The Manus agent instance
        image_path: Path to the image file
        text_prompt: Optional text prompt to accompany the image
    """
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return

        # Get file size for validation
        file_size = os.path.getsize(image_path)
        if file_size > 5 * 1024 * 1024:  # 5MB limit
            logger.error(f"Image file too large: {file_size / (1024*1024):.1f}MB (max 5MB)")
            return

        # Read and encode image
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        # Determine media type
        file_extension = Path(image_path).suffix.lower()
        media_type_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif"
        }

        media_type = media_type_map.get(file_extension)
        if not media_type:
            logger.error(f"Unsupported image format: {file_extension}")
            return

        # Create the combined prompt with image and text
        if text_prompt:
            combined_prompt = f"Image analysis request: {text_prompt}"
        else:
            combined_prompt = "Please analyze this image and describe what you see in detail."

        logger.info(f"Analyzing image: {os.path.basename(image_path)} ({file_size / 1024:.1f}KB)")

        # Create a special prompt that includes image data for the agent
        vision_prompt = {
            "type": "vision_analysis",
            "text": combined_prompt,
            "image": {
                "data": image_base64,
                "media_type": media_type,
                "filename": os.path.basename(image_path)
            }
        }

        # Run the agent with the vision prompt
        await agent.run_vision_analysis(vision_prompt)

    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")


def detect_image_in_prompt(prompt: str):
    """
    Detect if the prompt contains an image path
    Returns (is_image_prompt, image_path, text_part)
    """
    # Common image extensions
    image_extensions = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff"}

    words = prompt.split()
    for word in words:
        # Check if word looks like a file path with image extension
        if any(word.lower().endswith(ext) for ext in image_extensions):
            # Check if file exists
            if os.path.exists(word):
                # Extract the text part (everything except the file path)
                text_part = prompt.replace(word, "").strip()
                return True, word, text_part

    return False, None, prompt


async def main():
    # Create and initialize Manus agent
    agent = await Manus.create()
    try:
        prompt = input("Enter your prompt (or image path + description): ").strip()
        if not prompt:
            logger.warning("Empty prompt provided.")
            return

        logger.info("Processing your request...")

        # Check if the prompt contains an image path
        is_image_prompt, image_path, text_part = detect_image_in_prompt(prompt)

        if is_image_prompt:
            logger.info(f"Image detected: {image_path}")
            await analyze_image_with_prompt(agent, image_path, text_part)
        else:
            # Regular text prompt
            await agent.run(prompt)

        logger.info("Request processing completed.")

    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
    finally:
        # Ensure agent resources are cleaned up before exiting
        await agent.cleanup()


# Alternative: Interactive mode with explicit image/text choice
async def interactive_main():
    """
    Interactive version that explicitly asks for image or text input
    """
    agent = await Manus.create()
    try:
        print("\nManus Agent - Vision & Text Analysis")
        print("1. Text prompt")
        print("2. Image analysis")
        print("3. Image + text prompt")

        choice = input("Choose option (1-3): ").strip()

        if choice == "1":
            prompt = input("Enter your text prompt: ").strip()
            if prompt:
                await agent.run(prompt)

        elif choice == "2":
            image_path = input("Enter image path: ").strip()
            if image_path:
                await analyze_image_with_prompt(agent, image_path)

        elif choice == "3":
            image_path = input("Enter image path: ").strip()
            text_prompt = input("Enter your prompt about the image: ").strip()
            if image_path:
                await analyze_image_with_prompt(agent, image_path, text_prompt)

        else:
            logger.warning("Invalid choice.")

    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    except Exception as e:
        logger.error(f"Error in interactive main: {str(e)}")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    # Choose which version to run
    mode = input("Run in (a)uto-detect or (i)nteractive mode? [a/i]: ").strip().lower()

    if mode == 'i':
        asyncio.run(interactive_main())
    else:
        asyncio.run(main())


