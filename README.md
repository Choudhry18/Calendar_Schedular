# Schedule to ICS Converter
## Overview
The Schedule to ICS Converter is a Python program that takes a picture of a class schedule as input and generates an ICS (iCalendar) file. This ICS file can be imported into calendar applications such as Google Calendar, Apple Calendar, or Microsoft Outlook to create events for each class from the schedule.


## Prerequisites
Before you can use this program, make sure you have the following prerequisites installed on your system:

Python 3.x
Tesseract OCR (Optical Character Recognition) - You can download and install Tesseract from here.
Installation
Clone this repository to your local machine using Git:

git clone https://github.com/yourusername/schedule-to-ics.git
Navigate to the project directory:

cd schedule-to-ics
Install the required Python packages using pip:

pip install -r requirements.txt
Usage
Screenshot a picture of your class schedule. Make sure the text is clear.

Place the image file in the input directory of this repository.

Run the convert_schedule.py script:

python convert_schedule.py
The program will process the image, extract the schedule information, and generate an ICS file in the output directory.

Import the generated ICS file into your calendar application of choice. The events for your classes should now be visible in your calendar.


## License
This project is licensed under the MIT License - see the LICENSE file for details.

