import cv2
import time
import os
from inference_sdk import InferenceHTTPClient
# import time
# time.sleep(0.5)

# Initialize inference client - API key should be set via ROBOFLOW_API_KEY environment variable
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=os.getenv("ROBOFLOW_API_KEY", "YOUR_API_KEY_HERE")
)

# Open video file or webcam
video_path = "data/videos/unloading.mp4"  # Update with your actual video path
cap = cv2.VideoCapture(video_path)  # Use 0 for webcam live feed

# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Define codec and create VideoWriter object to save output
output_path = "output_detection.mp4"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    start_time = time.time()  # Track frame processing time

    # Save frame temporarily
    frame_path = "temp_frame.jpg"
    cv2.imwrite(frame_path, frame)

    # Run inference on the frame
    result = CLIENT.infer(frame_path, model_id="gunny-bag-detection-ygbox/2")

    # Draw detections on the frame
    for detection in result['predictions']:
        x, y, w, h = detection['x'], detection['y'], detection['width'], detection['height']
        label = detection['class']
        confidence = detection['confidence']

        # Calculate rectangle coordinates
        start_point = (int(x - w/2), int(y - h/2))
        end_point = (int(x + w/2), int(y + h/2))

        # Draw bounding box
        color = (0, 255, 0) if label == "Gunny Bag" else (255, 0, 0)  # Different colors for classes
        cv2.rectangle(frame, start_point, end_point, color, 3)
        cv2.putText(frame, f"{label} ({confidence:.2f})", (start_point[0], start_point[1]-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Calculate FPS
    fps = 1 / (time.time() - start_time)
    cv2.putText(frame, f"FPS: {fps:.2f}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Display the frame with detections
    cv2.imshow('Gunny Bag Detection - Live', frame)

    # Write frame to output video file
    out.write(frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()  # Save the final video
cv2.destroyAllWindows()
