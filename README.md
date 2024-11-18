# Keylogging Program
This Python script is a multi-functional keylogger that records keystrokes, captures screenshots, records audio, tracks clipboard data, and logs the active browser window. 
Everything is compiled and sent via email with the recorded information as attachments.

The libraries and reasons for using the libraries:
- `sounddevice` – for recording audio.
- `scipy` – for saving audio data in `.wav` format.
- `pyperclip` – for accessing the clipboard.
- `pynput` – for keylogging
- `Pillow` – for taking screenshots.
- `pygetwindow` – for capturing the currently active window
- `smtplib` – for sending emails with attachments.
- `cryptography` – for encryption

