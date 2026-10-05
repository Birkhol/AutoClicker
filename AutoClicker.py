import tkinter as tk
import time
import threading
import json
import os
import sys

from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode, Key


# --------------------------
# Configuration
# --------------------------

DEFAULT_DELAY = 0.01
MIN_DELAY = 0.009

delay = DEFAULT_DELAY
click_duration = 0.008
button = Button.left

DEFAULT_KEY = KeyCode(char="r")

start_stop_key = DEFAULT_KEY

binding_key = False
waiting_for_release = False

# --------------------------
# Resources
# --------------------------

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(
        base_path,
        relative_path
    )


# --------------------------
# Settings
# --------------------------

app_data = os.getenv("APPDATA")

if app_data:
    SETTINGS_DIR = os.path.join(app_data, "AutoClicker")
else:
    SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))

SETTINGS_FILE = os.path.join(
    SETTINGS_DIR,
    "settings.json"
)


def serialize_key(key):
    if isinstance(key, KeyCode):
        return {
            "type": "char",
            "value": key.char
        }

    return {
        "type": "special",
        "value": key.name
    }


def deserialize_key(data):
    try:
        if data["type"] == "char":
            return KeyCode(char=data["value"])

        if data["type"] == "special":
            return getattr(Key, data["value"])

    except (KeyError, AttributeError, TypeError):
        pass

    return DEFAULT_KEY


def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as file:
            settings = json.load(file)

        loaded_delay = float(
            settings.get(
                "click_interval",
                DEFAULT_DELAY
            )
        )

        if loaded_delay < MIN_DELAY:
            loaded_delay = DEFAULT_DELAY

        loaded_key = deserialize_key(
            settings.get(
                "start_stop_key",
                serialize_key(DEFAULT_KEY)
            )
        )

        return loaded_delay, loaded_key

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        ValueError
    ):
        return DEFAULT_DELAY, DEFAULT_KEY


# Load settings before creating the clicker
delay, start_stop_key = load_settings()


# --------------------------
# Auto Clicker
# --------------------------

class ClickMouse(threading.Thread):

    def __init__(self, delay, button):
        super().__init__(daemon=True)

        self.delay = delay
        self.button = button
        self.running = False
        self.program_running = True

    def start_clicking(self):
        self.running = True

    def stop_clicking(self):
        self.running = False

    def exit(self):
        self.stop_clicking()
        self.program_running = False

    def run(self):
        while self.program_running:

            while self.running and self.program_running:
                cycle_start = time.perf_counter()

                mouse.press(self.button)

                time.sleep(click_duration)

                mouse.release(self.button)

                elapsed = time.perf_counter() - cycle_start

                remaining = self.delay - elapsed

                if remaining > 0:
                    time.sleep(remaining)

            time.sleep(0.1)


mouse = Controller()

click_thread = ClickMouse(
    delay,
    button
)

click_thread.start()


# --------------------------
# Save Settings
# --------------------------

def save_settings():
    os.makedirs(
        SETTINGS_DIR,
        exist_ok=True
    )

    settings = {
        "click_interval": click_thread.delay,
        "start_stop_key": serialize_key(start_stop_key)
    }

    with open(SETTINGS_FILE, "w") as file:
        json.dump(
            settings,
            file,
            indent=4
        )


# --------------------------
# GUI
# --------------------------

root = tk.Tk()

root.title("Auto Clicker")
root.minsize(200, 200)
root.maxsize(600, 500)
root.geometry("400x250+50+50")

root.columnconfigure(
    0,
    weight=1
)

try:
    root.iconbitmap(
        resource_path("AutoClicker.ico")
    )
except tk.TclError:
    pass


# --------------------------
# GUI Functions
# --------------------------

def submit_input():
    user_text = entry.get()

    if user_text == "":
        output_label.config(
            text="Please enter an interval"
        )
        return

    try:
        new_delay = float(user_text)

    except ValueError:
        output_label.config(
            text="Please enter a valid number"
        )
        return

    if new_delay < MIN_DELAY:
        output_label.config(
            text=f"Minimum interval is {MIN_DELAY} seconds"
        )
        return

    click_thread.delay = new_delay

    save_settings()

    output_label.config(
        text="Settings saved"
    )


def only_numbers(value):
    if value == "":
        return True

    try:
        float(value)
        return True

    except ValueError:
        return False


def start_key_binding():
    global binding_key

    binding_key = True

    key_label.config(
        text="Press any key..."
    )

    output_label.config(
        text="Press ESC to cancel"
    )


def update_key_label(key):
    key_name = get_key_name(key)

    key_label.config(
        text=key_name
    )

    output_label.config(
        text=f"Press {key_name} to start/stop clicking"
    )

    # Save new keybind
    save_settings()


def cancel_key_binding():
    key_name = get_key_name(start_stop_key)

    key_label.config(
        text=key_name
    )

    output_label.config(
        text="Keybinding cancelled"
    )


def get_key_name(key):
    if isinstance(key, KeyCode):
        if key.char:
            return key.char.upper()

        return "UNKNOWN"

    return str(key).replace(
        "Key.",
        ""
    ).upper()


def update_status():
    if click_thread.running:
        status_label.config(
            text="● Clicking",
            fg="green"
        )

    else:
        status_label.config(
            text="● Stopped",
            fg="red"
        )


# --------------------------
# Keyboard Controls
# --------------------------

def on_press(key):
    global start_stop_key
    global binding_key
    global waiting_for_release

    # Currently choosing a new keybind
    if binding_key:

        # ESC cancels keybinding
        if key == Key.esc:
            binding_key = False

            root.after(
                0,
                cancel_key_binding
            )

            return

        start_stop_key = key

        binding_key = False
        waiting_for_release = True

        root.after(
            0,
            update_key_label,
            key
        )

        return

    if waiting_for_release:
        return

    # Start / stop clicking
    if key == start_stop_key:

        if click_thread.running:
            click_thread.stop_clicking()

            print(
                "[INFO] Clicker stopped"
            )

        else:
            click_thread.start_clicking()

            print(
                "[INFO] Clicker started"
            )

        root.after(
            0,
            update_status
        )


def on_release(key):
    global waiting_for_release

    if (
        waiting_for_release
        and key == start_stop_key
    ):
        waiting_for_release = False


listener = Listener(
    on_press=on_press,
    on_release=on_release
)

listener.start()


# --------------------------
# Close Program
# --------------------------

def close_program():
    click_thread.exit()

    listener.stop()

    root.destroy()


root.protocol(
    "WM_DELETE_WINDOW",
    close_program
)


# --------------------------
# GUI Components
# --------------------------

validate_numbers = root.register(
    only_numbers
)


# Interval
input_frame = tk.Frame(root)

input_frame.grid(
    row=0,
    column=0,
    pady=10
)


delay_label = tk.Label(
    input_frame,
    text="Interval between clicks:"
)

delay_label.grid(
    row=0,
    column=0,
    padx=5,
    pady=10
)


entry = tk.Entry(
    input_frame,

    validate="key",

    validatecommand=(
        validate_numbers,
        "%P"
    ),

    width=10,
    insertbackground="black"
)

entry.grid(
    row=0,
    column=1,
    padx=5,
    pady=10
)


entry.insert(
    0,
    str(delay)
)


submit_button = tk.Button(
    input_frame,
    text="Save",
    command=submit_input
)

submit_button.grid(
    row=0,
    column=2,
    padx=5,
    pady=10
)


# --------------------------
# Keybinding
# --------------------------

keybind_frame = tk.Frame(root)

keybind_frame.grid(
    row=1,
    column=0,
    pady=10
)


keybind_text = tk.Label(
    keybind_frame,
    text="Start/Stop key:"
)

keybind_text.grid(
    row=0,
    column=0,
    padx=5
)


# Use saved keybind
key_label = tk.Label(
    keybind_frame,
    text=get_key_name(start_stop_key),
    width=8,
    relief="sunken"
)

key_label.grid(
    row=0,
    column=1,
    padx=5
)


bind_button = tk.Button(
    keybind_frame,
    text="Bind Key",
    command=start_key_binding
)

bind_button.grid(
    row=0,
    column=2,
    padx=5
)


# --------------------------
# Information
# --------------------------

output_label = tk.Label(
    root,
    text=(
        f"Press {get_key_name(start_stop_key)} "
        "to start/stop clicking"
    )
)

output_label.grid(
    row=3,
    column=0,
    pady=20
)


status_label = tk.Label(
    root,
    text="● Stopped",
    fg="red"
)

status_label.grid(
    row=4,
    column=0,
    pady=8
)


# --------------------------
# Start GUI
# --------------------------

root.mainloop()