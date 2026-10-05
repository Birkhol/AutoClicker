import tkinter as tk
import time
import threading
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode, Key

#--------------------------
# Configuration
#--------------------------
delay = 0.01
click_duration = 0.008
button = Button.left

start_stop_key = KeyCode(char="r")
binding_key = False
waiting_for_release = False
exit_key = KeyCode(char="t")

#--------------------------
# Auto Clicker
#--------------------------
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

            while self.running:
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
click_thread = ClickMouse(delay, button)
click_thread.start()

#--------------------------
# Keyboard controls
#--------------------------
def on_press(key):
    global start_stop_key
    global binding_key
    global waiting_for_release

    if binding_key:
        if key == Key.esc:
            binding_key = False
            root.after(0, cancel_key_binding)
            return
        
        start_stop_key = key
        binding_key = False
        waiting_for_release = True

        root.after(0, update_key_label, key)

    if waiting_for_release:
        return

    if key == start_stop_key:

        if click_thread.running:
            click_thread.stop_clicking()
            print("[INFO] Clicker stopped")

        else:
            click_thread.start_clicking()
            print("[INFO] Clicker started")

    elif key == exit_key:
        click_thread.exit()
        listener.stop()
        print("[INFO] Program exiting")

def on_release(key):
    global waiting_for_release

    if waiting_for_release and key == start_stop_key:
        waiting_for_release = False

listener = Listener(
    on_press=on_press,
    on_release=on_release
)
listener.start()

#--------------------------
# GUI
#--------------------------
root = tk.Tk()

root.title("Auto Clicker")
root.minsize(200, 200)
root.maxsize(600, 500)
root.geometry("400x300+50+50")
root.columnconfigure(0, weight=1)
root.iconbitmap("AutoClicker.ico")

def close_program():
    click_thread.exit()
    listener.stop()
    root.destroy()
root.protocol("WM_DELETE_WINDOW", close_program)

#--------------------------
# GUI Functions
#--------------------------
def submit_input():
    user_text = entry.get()

    if user_text == "":
        output_label.config(text="Please enter an interval")
        return

    new_delay = float(user_text)

    if new_delay < 0.009:
        output_label.config(
            text="Minimum interval is 0.009 seconds"
        )
        return

    click_thread.delay = new_delay

    output_label.config(text=f"Interval saved: {new_delay} seconds")

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
    key_label.config(text="Press any key...")

def update_key_label(key):
    key_name = get_key_name(key)

    key_label.config(text=key_name)

    output_label.config(
        text=f"Press {key_name} to start/stop"
    )

def cancel_key_binding():
    key_label.config(text=get_key_name(start_stop_key))

    output_label.config(
        text=f"Keybinding cancelled"
    )

def get_key_name(key):
    if isinstance(key, KeyCode):
        return key.char.upper()
    else:
        return str(key).replace("Key.", "").upper()

#--------------------------
# GUI Components
#--------------------------
validate_numbers = root.register(only_numbers)

input_frame = tk.Frame(root)
input_frame.grid(row=0, column=0, pady=10)

delay_label = tk.Label(
    input_frame, 
    text="Interval between clicks:"
)
delay_label.grid(row=0, column=0, padx=5, pady=10)

entry = tk.Entry(
    input_frame,
    validate="key",
    validatecommand=(validate_numbers, "%P"),

    width=10,
    insertbackground="white"
)
entry.grid(row=0, column=1, padx=5, pady=10)

submit_button = tk.Button(
    input_frame, 
    text="Save", 
    command=submit_input,


)
submit_button.grid(row=0, column=2, padx=5, pady=10)

entry.insert(0, str(delay))

keybind_frame = tk.Frame(root)
keybind_frame.grid(row=1, column=0, pady=10)

keybind_text = tk.Label(
    keybind_frame,
    text="Start/Stop key:"
)
keybind_text.grid(row=0, column=0, padx=5)

key_label = tk.Label(
    keybind_frame,
    text="R",
    width=6,
    relief="sunken"
)
key_label.grid(row=0, column=1, padx=5)

bind_button = tk.Button(
    keybind_frame,
    text="Bind Key",
    command=start_key_binding
)
bind_button.grid(row=0, column=2, padx=5)

output_label = tk.Label(
    root, 
    text="Press R to start/stop clicking"
)
output_label.grid(row=3, column=0, pady=30)

#--------------------------
# Start GUI
#--------------------------
root.mainloop()
