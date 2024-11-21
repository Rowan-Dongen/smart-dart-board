import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import cv2
import numpy as np

class ImageCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Capture Tool")
        
        # Input fields for number of datasets and images per dataset
        tk.Label(root, text="Number of Datasets:").grid(row=0, column=0, padx=10, pady=5)
        tk.Label(root, text="Images per Dataset:").grid(row=1, column=0, padx=10, pady=5)
        
        self.num_datasets = tk.Entry(root)
        self.num_datasets.grid(row=0, column=1, padx=10, pady=5)
        
        self.images_per_dataset = tk.Entry(root)
        self.images_per_dataset.grid(row=1, column=1, padx=10, pady=5)

        # Input fields for image resolution
        tk.Label(root, text="Image Width:").grid(row=2, column=0, padx=10, pady=5)
        tk.Label(root, text="Image Height:").grid(row=3, column=0, padx=10, pady=5)
        
        self.image_width = tk.Entry(root)
        self.image_width.grid(row=2, column=1, padx=10, pady=5)
        
        self.image_height = tk.Entry(root)
        self.image_height.grid(row=3, column=1, padx=10, pady=5)
        
        # Button to start capturing images
        self.start_button = tk.Button(root, text="Start Capturing Images", command=self.start_capture)
        self.start_button.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Label to show the current progress of datasets and images
        self.status_label = tk.Label(root, text="")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Capture button (disabled initially)
        self.capture_button = tk.Button(root, text="Capture Image", command=self.capture_image, state="disabled")
        self.capture_button.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Video preview label
        self.preview_label = tk.Label(root)
        self.preview_label.grid(row=7, column=0, columnspan=2)
        
        # Variables to store the current progress
        self.dataset_count = 1
        self.image_count = 0
        self.cap = None

    def start_capture(self):
        # Retrieve and validate user inputs
        try:
            self.total_datasets = int(self.num_datasets.get())
            self.total_images = int(self.images_per_dataset.get())
            self.res_width = int(self.image_width.get())
            self.res_height = int(self.image_height.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid integers.")
            return
        
        if self.total_datasets <= 0 or self.total_images <= 0 or self.res_width <= 0 or self.res_height <= 0:
            messagebox.showerror("Input Error", "All numbers should be greater than zero.")
            return
        
        # Reset counters
        self.dataset_count = 1
        self.image_count = 0

        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Camera Error", "Unable to access the camera.")
            return

        # Start the video preview loop
        self.update_status()
        self.capture_button.config(state="normal")
        self.capture_loop()  # Start the live preview

    def capture_loop(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Convert frame to PIL format for tkinter display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                
                # Update preview label
                self.preview_label.imgtk = imgtk
                self.preview_label.configure(image=imgtk)
                
            # Schedule the next frame update
            self.root.after(10, self.capture_loop)
        
    def capture_image(self):
        # Capture frame from camera
        ret, frame = self.cap.read()
        if not ret:
            messagebox.showerror("Capture Error", "Failed to capture image.")
            return
        
        # Prepare directory for the dataset
        dataset_folder = f"dataset_{self.dataset_count}"
        if not os.path.exists(dataset_folder):
            os.makedirs(dataset_folder)
        
        # Set to higher resolution to ensure good quality cropping
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, max(self.res_width, self.res_height))
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, max(self.res_width, self.res_height))

        # Center crop the image to the specified resolution
        frame = self.center_crop(frame, self.res_width, self.res_height)
        
        # Save image with an incremented name in the current dataset folder
        self.image_count += 1
        image_path = os.path.join(dataset_folder, f"image_{self.image_count}.jpg")
        cv2.imwrite(image_path, frame)
        
        # Show confirmation in console (optional)
        print(f"Captured {image_path}")

        # Update counts and check if we need to move to the next dataset
        if self.image_count >= self.total_images:
            self.dataset_count += 1
            self.image_count = 0
            
            # Check if all datasets are completed
            if self.dataset_count > self.total_datasets:
                self.end_capture()
                return
        
        # Update status label with new dataset/image count
        self.update_status()


    def center_crop(self, img, crop_width, crop_height):
        # Get current dimensions
        height, width = img.shape[:2]
        
        # Calculate the coordinates for center cropping
        start_x = max(0, (width - crop_width) // 2)
        start_y = max(0, (height - crop_height) // 2)
        
        # Perform the crop
        cropped_img = img[start_y:start_y + crop_height, start_x:start_x + crop_width]
        return cropped_img
    
    def update_status(self):
        # Display the current dataset and image count in the label
        self.status_label.config(text=f"Dataset {self.dataset_count} / {self.total_datasets} - Image {self.image_count + 1} / {self.total_images}")
        
    def end_capture(self):
        # Stop capture, release camera, and clean up
        self.cap.release()
        cv2.destroyAllWindows()
        self.capture_button.config(state="disabled")
        messagebox.showinfo("Capture Complete", "All datasets and images have been captured.")
        self.status_label.config(text="Capture complete!")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCaptureApp(root)
    root.mainloop()
