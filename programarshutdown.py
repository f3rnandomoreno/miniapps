import tkinter as tk
from tkinter import ttk
import os
import sys
import subprocess

def schedule_shutdown():
    try:
        minutes = int(minutes_entry.get())
        seconds = minutes * 60
        if sys.platform == "win32":
            subprocess.run(["shutdown", "/s", "/t", str(seconds)])
        elif sys.platform == "linux" or sys.platform == "linux2":
            subprocess.run(["shutdown", "-h", "+" + str(minutes)])
        else:
            print("Unsupported OS")
    except ValueError:
        print("Please enter a valid number of minutes")

def cancel_shutdown():
    if sys.platform == "win32":
        subprocess.run(["shutdown", "/a"])
    elif sys.platform == "linux" or sys.platform == "linux2":
        subprocess.run(["shutdown", "-c"])
    else:
        print("Unsupported OS")

app = tk.Tk()
app.title("Programar Apagado")

minutes_label = ttk.Label(app, text="Minutos hasta el apagado:")
minutes_label.pack()

minutes_entry = ttk.Entry(app)
minutes_entry.insert(0, "60")  # Set default value to 60 minutes
minutes_entry.pack()

shutdown_button = ttk.Button(app, text="Programar Apagado", command=schedule_shutdown)
shutdown_button.pack()

cancel_button = ttk.Button(app, text="Cancelar Apagado", command=cancel_shutdown)
cancel_button.pack()

app.mainloop()
