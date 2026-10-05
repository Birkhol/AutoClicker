import tkinter as tk

root = tk.Tk()

root.title("Auto Clicker")
root.minsize(200, 200)
root.maxsize(600, 500)
root.geometry("400x300+50+50")
root.iconbitmap("AutoClicker.ico")


def submit_input():
    user_text = entry.get()
    output_label.config(text=f"You entered: {user_text}")

def only_numbers(value):
    if value == "":
        return True

    try:
        float(value)
        return True
    except ValueError:
        return False

validate_numbers = root.register(only_numbers)

entry = tk.Entry(
    root, 
    validate="key", 
    validatecommand=(validate_numbers, "%P"), 
    width=25
)
entry.pack(pady=10)

submit_button = tk.Button(root, text="Save", command=submit_input)
submit_button.pack(pady=5)

output_label = tk.Label(root, text="Save settings")
output_label.pack(pady=10)



root.mainloop()