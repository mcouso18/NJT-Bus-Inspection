import asyncio
import base64
import io
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk

from PIL import Image

# --- Core Change: Direct Imports and Path Correction ---
# Add the project root to the Python path to allow direct imports
# This assumes 'simple_gui_manus.py' is in the project root ('OpenManus v2 - Copy')
# and the 'app' directory is at the same level.
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.agent.manus import Manus
from app.logger import logger
# We will also need the excel function from main.py
from main import analyze_and_populate_excel


class SimpleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenManus GUI")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        self.main_frame = ttk.Frame(root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=0)

        self.conversation_display = scrolledtext.ScrolledText(
            self.main_frame, wrap=tk.WORD, state="disabled"
        )
        self.conversation_display.grid(row=0, column=0, sticky="nsew")

        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.grid(row=1, column=0, sticky="ew", pady=5)
        self.input_frame.columnconfigure(0, weight=1)

        self.prompt_input = scrolledtext.ScrolledText(self.input_frame, wrap=tk.WORD, height=4)
        self.prompt_input.grid(row=0, column=0, sticky="ew", padx=5)

        self.upload_button = ttk.Button(
            self.input_frame, text="Upload Images", command=self.upload_images
        )
        self.upload_button.grid(row=0, column=1, padx=5)

        self.send_button = ttk.Button(
            self.input_frame, text="Send Prompt", command=self.send_prompt
        )
        self.send_button.grid(row=0, column=2, padx=5)

    def send_prompt(self):
        prompt_text = self.prompt_input.get("1.0", tk.END).strip()
        if not prompt_text:
            self.append_to_conversation("⚠️ Please enter a prompt first.")
            return
        threading.Thread(target=lambda: asyncio.run(self.analyze_text(prompt_text))).start()

    def upload_images(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.webp *.gif")]
        )
        if not file_paths:
            return
        prompt_text = self.prompt_input.get("1.0", tk.END).strip() or "Please analyze these images."
        threading.Thread(target=lambda: asyncio.run(self.analyze_images(file_paths, prompt_text))).start()

    def append_to_conversation(self, text):
        self.conversation_display.configure(state="normal")
        self.conversation_display.insert(tk.END, text + "\n\n")
        self.conversation_display.configure(state="disabled")
        self.conversation_display.see(tk.END)

    async def analyze_text(self, prompt_text):
        agent = None
        try:
            agent = Manus()
            result = await agent.run(prompt_text)
            self.append_to_conversation(f"📝 Prompt: {prompt_text}\n🤖 Response: {result}")
        except Exception as e:
            logger.error(f"Error in analyze_text: {e}")
            self.append_to_conversation(f"❌ Error: {e}")

    async def analyze_images(self, file_paths, prompt_text):
        agent = None
        try:
            agent = Manus()
            all_analysis_results = {}

            async def process_image(path):
                try:
                    img = Image.open(path).convert("RGB")
                    img.thumbnail((1024, 1024))
                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG")
                    image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

                    vision_prompt = {
                        "type": "vision_analysis",
                        "text": prompt_text,
                        "image": {
                            "data": image_base64,
                            "media_type": "image/jpeg",
                            "filename": os.path.basename(path)
                        }
                    }

                    logger.info(f"Processing: {os.path.basename(path)}")
                    result = await agent.run_vision_analysis(vision_prompt)
                    self.append_to_conversation(f"🖼️ Image: {os.path.basename(path)}\n🤖 Response: {result}")
                    if isinstance(result, dict):
                        all_analysis_results.update(result)

                except Exception as e:
                    logger.error(f"Error processing {path}: {e}")
                    self.append_to_conversation(f"❌ Error processing {path}: {e}")

            await asyncio.gather(*(process_image(p) for p in file_paths))

            if all_analysis_results:
                logger.info("Aggregated analysis complete. Populating Excel...")
                template_path = "/home/ubuntu/upload/TemplateforAIOutput.xlsx" # Adjust this path as needed
                output_path = "/home/ubuntu/analysis/Bus_Analysis_Output_GUI.xlsx" # Adjust this path as needed
                analyze_and_populate_excel(template_path, output_path, all_analysis_results)
                self.append_to_conversation(f"✅ Excel file populated and saved to {output_path}")
            else:
                self.append_to_conversation("⚠️ No analysis results to populate Excel.")

        except Exception as e:
            logger.error(f"Error in analyze_images: {e}")
            self.append_to_conversation(f"❌ Error: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleGUI(root)
    root.mainloop()

