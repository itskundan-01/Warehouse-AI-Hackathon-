# from inference_sdk import InferenceHTTPClient

# # create an inference client
# CLIENT = InferenceHTTPClient(
#     api_url="https://detect.roboflow.com",
#     api_key="s0XLgHrjbUd1F0thbHHs"  # <-- Replace with your Roboflow API key
# )

# # run inference on a local image
# result = CLIENT.infer(
#     "your_image.jpg",  # <-- Replace with your local image path
#     model_id="gunny-bag-detection-ygbox/2"
# )

# print(result)

import cv2
import os
from inference_sdk import InferenceHTTPClient

# Initialize inference client - API key should be set via ROBOFLOW_API_KEY environment variable
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=os.getenv("ROBOFLOW_API_KEY", "YOUR_API_KEY_HERE")
)

# Open video file
video_path = "data/videos/unloading.mp4"  # Update with your video file path
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Save frame temporarily
    frame_path = "temp_frame.jpg"
    cv2.imwrite(frame_path, frame)

    # Run inference on the frame
    result = CLIENT.infer(frame_path, model_id="gunny-bag-detection-ygbox/2")
    print(result)

    # (Optional) Overlay detections on the frame using OpenCV before displaying
    
cap.release()
cv2.destroyAllWindows()
