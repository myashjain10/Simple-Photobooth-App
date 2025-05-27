# PhotoBooth App
This is a simple photobooth app made using python.

### Requirments
- **SumatraPDF** - A open source PDF reader. It has command line control as well that's why we are using for controlling print settings.
- **External Libraries** - Libraries mentioned in requirements.txt. 

- SumatraPDF should be installed on the device on which you are running this app.
- Compile the *photoBooth.py* file to an executable using pyinstaller or some other utility.
- Create a folder on your device(preferrably on desktop) and place this executable inside it.
- Also copy the *config.json* file provided in the repo in the same folder where the executable is.
- This *config.json* file has few variables:
  - `sumatra_pdf_path` : This is the location of SumatraPDF app on your device. Usually in this format -> "C:\\Users\\<device_name>\\AppData\\Local\\SumatraPDF\\SumatraPDF.exe"
  - `background_image_path`: This is the location of background image that would be applied in place of green screen. If you leave this blank like this "", no background will be applied.
  - `camera_number`: Default camera (usually webcam) is "0". For external cameras, try "1", "2" or "3".

NOTE: More settings/variables from the code can be exposed using *config.json* file.

- When running the executable file, the app will create a *images* folder where it will store all the captured images (with and without background applied)
- The images with name ending with "BGA" have background applied to them.

### IMPORTANT 
- The photo will be printed with default printer settings. To configure these settings you can either change it from the printer app (epson printer software) or you can change the settings in the code (just search "print settings" in the code).
- Preferred way would be to change the default printer settings from the Printer Software.
- the size has been fixed to 4 x 6 inches. You can change the size in the code where the photo is converted to pdf (in the print_image function)