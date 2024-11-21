import cv2
import numpy as np
import os
import datetime
import time

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Parameters
motion_threshold = 500  # Threshold for amount of change to consider as motion
save_folder = "captured_changes"
os.makedirs(save_folder, exist_ok=True)

# Initialize the first frame
ret, previous_frame = cap.read()
if not ret:
    print("Error: Could not read from camera.")
    cap.release()
    exit()

# Convert to grayscale for better comparison
previous_gray = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)

while True:
    # Capture the current frame
    ret, current_frame = cap.read()
    if not ret:
        print("Error: Could not read from camera.")
        break

    # Convert the current frame to grayscale
    current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

    # Compute the absolute difference between the current and previous frame
    frame_diff = cv2.absdiff(previous_gray, current_gray)

    # Apply a threshold to highlight the differences
    _, thresh_diff = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)

    # Calculate the amount of change
    change_amount = np.sum(thresh_diff) // 255  # Counts the number of white pixels

    # Check if the change exceeds the threshold
    if change_amount > motion_threshold:
        # Save the current frame as an image
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(save_folder, f"motion_{timestamp}.jpg")
        cv2.imwrite(image_path, current_frame)
        print(f"Motion detected! Image saved at: {image_path}")

    # Display the difference for visualization (optional)
    cv2.imshow("Motion Detection", thresh_diff)

    # Update previous frame
    previous_gray = current_gray
    
    time.sleep(0.5)

    # Exit on pressing 'q'
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
