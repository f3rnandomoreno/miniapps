import tkinter as tk
from tkinter import ttk
import sys
import subprocess

def schedule_shutdown(minutes):
    seconds = minutes * 60
    if sys.platform == "win32":
        subprocess.run(["shutdown", "/s", "/t", str(seconds)])
    elif sys.platform == "linux" or sys.platform == "linux2":
        subprocess.run(["shutdown", "-h", "+" + str(minutes)])
    else:
        print("Unsupported OS")

def cancel_shutdown():
    if sys.platform == "win32":
        subprocess.run(["shutdown", "/a"])
    elif sys.platform == "linux" or sys.platform == "linux2":
        subprocess.run(["shutdown", "-c"])
    else:
        print("Unsupported OS")

app = tk.Tk()
app.title("Programar Apagado")

# Función para crear un botón de programación de apagado
def create_shutdown_button(text, minutes):
    return ttk.Button(app, text=text, command=lambda: schedule_shutdown(minutes))

# Crear botones para diferentes intervalos de tiempo
button_15min = create_shutdown_button("15 minutos", 15)
button_15min.pack()

button_30min = create_shutdown_button("30 minutos", 30)
button_30min.pack()

button_60min = create_shutdown_button("60 minutos", 60)
button_60min.pack()

button_90min = create_shutdown_button("90 minutos", 90)
button_90min.pack()

button_120min = create_shutdown_button("120 minutos", 120)
button_120min.pack()

# Botón para cancelar el apagado
cancel_button = ttk.Button(app, text="Cancelar Apagado", command=cancel_shutdown)
cancel_button.pack()

app.mainloop()
