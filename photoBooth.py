import datetime
import os
import cv2
import time
import threading
import tkinter as tk
from tkinter import Button
from PIL import Image, ImageTk, ImageWin
from reportlab.lib.pagesizes import inch, landscape
from reportlab.pdfgen import canvas
import subprocess
import numpy as np
import json

# opening config file
with open("config.json", "r") as file:
    config = json.load(file)
 
#***** vars *******
sumatra_path = config["sumatra_pdf_path"]
background_filepath = config["background_image_path"]
camera_num = config["camera_number"]
filepath = "test.jpeg" # global image file path variable (default test.jpg)


# Create images directory if it doesn't exist
images_dir = "images"
if not os.path.exists(images_dir):
  os.makedirs(images_dir)
  print(f"Created directory: {images_dir}")


# Initialize the webcam for video capture. The argument '0' specifies the default camera (webcam).
imgcapture = cv2.VideoCapture(int(camera_num)) 
imgcapture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
imgcapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

countdown_text = ""
capturing = False
result = True
frame_rgb = None


def countdown(n):
    global countdown_text, capturing
    while n > 0:
        countdown_text = str(n)
        time.sleep(1)
        n -= 1
    countdown_text = ""
    capturing = True


def apply_background(image_path, background_path):
    if background_path == "":
        return image_path
    
    img = cv2.imread(image_path)  # Read the captured image
    bg = cv2.imread(background_path)  # Read the background image

    # Resize background to match the captured image dimensions
    bg = cv2.resize(bg, (img.shape[1], img.shape[0]))

    # Simulate segmentation by converting to HSV and creating a mask
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_green = np.array([30, 80, 80])  # Lower boundary (Hue, Saturation, Value)
    upper_green = np.array([90, 255, 255])  # Upper boundary (Hue, Saturation, Value)

    mask = cv2.inRange(hsv, lower_green, upper_green)  # Create mask for green color
    
    mask_inv = cv2.bitwise_not(mask)  # Invert the mask
    img_bg = cv2.bitwise_and(img, img, mask=mask_inv)  # Extract the foreground
    bg_fg = cv2.bitwise_and(bg, bg, mask=mask)  # Extract the background
    combined = cv2.add(img_bg, bg_fg)  # Combine foreground and background

    # Construct the output path with "BGA" added to the filename
    directory, filename = os.path.split(image_path)  # Get directory and filename
    name, ext = os.path.splitext(filename)  # Split filename and extension
    output_filename = f"{name}_BGA{ext}"  # Append "BGA" to the filename
    output_path = os.path.join(directory, output_filename)  # Construct output path

    # Save the combined image
    cv2.imwrite(output_path, combined)
    
    return output_path  # Return the path of the combined image

def print_image():
    
    # add background to image
    # input image = filepath 
    # output image = filepath_BGA
    image_file = apply_background(filepath, background_filepath)


    print("creating the pdf file")
    pdf_file = "output.pdf"

    # Set page size to true landscape mode (6x4 inches)
    pdf_width, pdf_height = 6 * inch, 4 * inch
    c = canvas.Canvas(pdf_file, pagesize=landscape((4*inch, 6*inch)))

    # Load the image
    image = Image.open(image_file)
    img_width, img_height = image.size

    # Scale the image to fit the full width OR height of the page 
    # This will ensure the image extends to at least one edge of the page
    scale = max(pdf_width / img_width, pdf_height / img_height)
    scaled_width = img_width * scale
    scaled_height = img_height * scale

    # Center the image within the PDF page (will allow white borders on opposite sides)
    x_offset = (pdf_width - scaled_width) / 2
    y_offset = (pdf_height - scaled_height) / 2

    # Draw the image without stretching
    c.drawImage(image_file, x_offset, y_offset, scaled_width, scaled_height)

    # Save the PDF
    c.showPage()
    c.save()
    
# *****************SYSTEM-SPECIFIC********************
    # Path to SumatraPDF - update this to your installation location 
    global sumatra_path
# ****************************************************
    print("pdf sent to printer")
    #*******PRINT THE PDF*********
    try:
        # Create startupinfo to hide window
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE flag
        
        # First, check if SumatraPDF is already running and kill it if necessary
        os.system('taskkill /f /im SumatraPDF.exe 2>nul')
        time.sleep(1)  # Give it a moment to close

        #PRINT SETTINGS
        # Print with 4x6 photo paper settings or default settings
        subprocess.run([
            sumatra_path,
            "-print-to-default",
            pdf_file
        ], 
        check=True,
        startupinfo=startupinfo)
        
        print("Print job sent successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error printing: {e}")
    except FileNotFoundError:
        print("Could not find SumatraPDF. Please check the path.")
    

def retake_image():
    global capturing, result
    capturing = False
    result = True
    btn_print.pack_forget()
    btn_retake.pack_forget()
    btn_capture.pack(side=tk.BOTTOM, pady=20)  # Show the Capture button again
    show_frame()

def show_frame():
    global countdown_text, capturing, result, frame_rgb
    ret, frame = imgcapture.read()  # Capture a frame from the webcam
    frame = cv2.flip(frame, 1)  # Mirror the frame

    if countdown_text:
        # Get frame dimensions dynamically
        frame_height, frame_width, _ = frame.shape

        # Get text size to position it in the center
        font_scale = 7
        font_thickness = 12
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(countdown_text, font, font_scale, font_thickness)[0]

        text_x = (frame_width - text_size[0]) // 2
        text_y = (frame_height + text_size[1]) // 2  # Adjusting for better vertical alignment

        frame = cv2.putText(frame, countdown_text, (text_x, text_y), font, font_scale, (0, 255, 255), font_thickness, cv2.LINE_AA)

    # Resize the frame to cover 90% of the screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    frame = cv2.resize(frame, (int(screen_width * 0.9), int(screen_height * 0.9)))

    # Convert the frame to PIL format for Tkinter
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    imgtk = ImageTk.PhotoImage(image=img)
    
    # Show the frame in the Tkinter window
    lbl_video.imgtk = imgtk
    lbl_video.configure(image=imgtk)

    if capturing:
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        #****IMAGE NAME*****
        filename = f"image_{timestamp}.jpeg"

        #*****IMAGE LOCATION*****
        global filepath
        filepath = os.path.join(images_dir, filename) 

        # Capture a new frame without the countdown text
        frame_rgb = cv2.cvtColor(imgcapture.read()[1], cv2.COLOR_BGR2RGB)
        cv2.imwrite(filepath, cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR))
        print(f"Image captured as {filename}")
        capturing = False
        # Resize the captured frame to make it bigger
        frame_rgb = cv2.resize(frame_rgb, (int(screen_width * 0.8), int(screen_height * 0.8)))
        # Show the captured frame
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)
        # Hide the Capture button and show Print and Retake buttons
        btn_capture.pack_forget()
        btn_print.pack(side=tk.LEFT, padx=10, pady=10)
        btn_retake.pack(side=tk.RIGHT, padx=10, pady=10)
    else:
        # Continue showing frames if not capturing
        if result:
            lbl_video.after(10, show_frame)

def capture_image():
    countdown_thread = threading.Thread(target=countdown, args=(5,))
    countdown_thread.start()

def exit_app():
    root.quit()

# Initialize the Tkinter window
root = tk.Tk()
root.title("Webcam Preview")
root.attributes('-fullscreen', True)  # Set the window to fullscreen
root.configure(bg='#000000')  # Set background color to black
lbl_video = tk.Label(root, bg='#000000')
lbl_video.pack(expand=True, fill=tk.BOTH)

# Create Capture, Print, Retake, and Exit buttons with appropriate styles
btn_capture = Button(root, text="Capture", command=capture_image, font=("Helvetica", 24), padx=20, pady=10, bg='#008000', fg='#FFFFFF')
btn_print = Button(root, text="Print", command=print_image, font=("Helvetica", 24), padx=20, pady=10, bg='#8B0000', fg='#FFFFFF')
btn_retake = Button(root, text="Retake", command=retake_image, font=("Helvetica", 24), padx=20, pady=10, bg='#8B0000', fg='#FFFFFF')
btn_exit = Button(root, text="X", command=exit_app, font=("Helvetica", 18), bg='#FF0000', fg='#FFFFFF')

# Position the Capture button at the bottom center
btn_capture.pack(side=tk.BOTTOM, pady=20)
# Hide the Print and Retake buttons initially
btn_print.pack_forget()
btn_retake.pack_forget()
# Position the Exit button in the top right corner
btn_exit.place(x=root.winfo_screenwidth()-50, y=10)

# Start showing the webcam preview
show_frame()

# Start the Tkinter event loop
root.mainloop()

# Release the webcam resource and destroy the OpenCV windows
imgcapture.release()
cv2.destroyAllWindows()
