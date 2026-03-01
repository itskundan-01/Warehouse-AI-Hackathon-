import google.generativeai as genai
import os
import time

# --- Configuration ---
# IMPORTANT: Set up your API key via environment variable.
# Run `export GOOGLE_API_KEY="YOUR_API_KEY"` in your terminal before running the script.
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable")

# The path to the video file you want to analyze
VIDEO_FILE_PATH = "data/videos/puthuru_ch4_20250509071306_20250509071531.mp4" 

# The model to use. 'gemini-1.5-flash' is fast and cost-effective for video.
MODEL_NAME = "gemini-1.5-flash"

# The prompt that tells the model what to do. Be as specific as possible!
PROMPT = """
You are an expert inventory and logistics analyst. Your task is to accurately count the number of sacks/gunny bags being carried by workers from the truck area into the warehouse in this video.

Follow these rules very carefully:
1.  Identify each person carrying a sack on their shoulder or back.
2.  Count a sack ONLY ONCE, at the exact moment the person carrying it fully crosses the warehouse entrance threshold.
3.  Do not count sacks that are still on the truck or sitting on the ground.
4.  Do not double-count a sack if a person hesitates, pauses, or moves back-and-forth near the entrance. Only count upon successful entry.
5.  Provide only the final total count of sacks that successfully entered the warehouse. If you are uncertain, provide your best estimate and mention the uncertainty.

Analyze the entire video and give the final count.
"""

# --- Main Script Logic ---
def main():
    """The main function to run the video analysis."""
    print("--- Gemini Video Analysis Script ---")

    # 1. Configure the API
    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        print(f"Error configuring API: {e}")
        print("Please make sure you have set your GOOGLE_API_KEY correctly.")
        return

    # 2. Check if the video file exists
    if not os.path.exists(VIDEO_FILE_PATH):
        print(f"Error: Video file not found at '{VIDEO_FILE_PATH}'")
        print("Please make sure the video file is in the same directory as the script, or provide the full path.")
        return

    # 3. Upload the video file to the Gemini API (using the new SDK method)
    print(f"Uploading video '{VIDEO_FILE_PATH}' to the API. This may take a moment...")
    try:
        # Use the new SDK method for uploading files (as of 2024)
        video_file = genai.upload_file(path=VIDEO_FILE_PATH)
        print(f"Video uploaded successfully. File URI: {video_file.uri}")
    except Exception as e:
        print(f"Error uploading file: {e}")
        return

    # 4. Wait for the file to be processed
    while getattr(video_file, 'state', None) and getattr(video_file.state, 'name', None) == "PROCESSING":
        print("Waiting for the video to be processed...")
        time.sleep(10)
        video_file = genai.get_file(video_file.name)

    if getattr(video_file, 'state', None) and getattr(video_file.state, 'name', None) == "FAILED":
        print("Video processing failed.")
        return

    # 5. Create the generative model instance (use gemini-1.5-flash or gemini-2.0-flash)
    model = genai.GenerativeModel(model_name=MODEL_NAME)

    # 6. Send the prompt and the video to the model
    print("\nSending prompt to Gemini. The model is now analyzing the video...")
    print("This can take several minutes depending on the video length.")
    try:
        response = model.generate_content([PROMPT, video_file], request_options={"timeout": 1200})
        print("\n--- Analysis Result ---")
        print(response.text)
        print("-----------------------")
    except Exception as e:
        print(f"\nAn error occurred while generating content: {e}")
    finally:
        # 8. Clean up by deleting the uploaded file from the server
        print("\nDeleting uploaded file from the server...")
        try:
            genai.delete_file(video_file.name)
            print("File deleted.")
        except Exception as e:
            print(f"Error deleting file: {e}")

if __name__ == "__main__":
    main()