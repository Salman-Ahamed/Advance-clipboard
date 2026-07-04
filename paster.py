import time

def paste_text(text):
    import pyperclip
    import keyboard
    pyperclip.copy(text)
    time.sleep(0.1)
    keyboard.send("ctrl+v")

def smart_paste(text, monitor=None):
    import pyperclip
    import keyboard
    if monitor:
        monitor.stop()
    pyperclip.copy(text)
    time.sleep(0.05)
    keyboard.send("ctrl+v")
    time.sleep(0.1)
    if monitor:
        monitor.start()

def type_text(text):
    import keyboard
    keyboard.write(text, delay=0.005)
