import tkinter as tk
from tkinter import ttk
import sys
import subprocess
import threading
import time

def schedule_shutdown(minutes):
    global shutdown_time
    shutdown_time = time.time() + minutes * 60
    update_countdown()
    if sys.platform == "win32":
        subprocess.run(["shutdown", "/s", "/t", str(minutes * 60)])
    elif sys.platform in ["linux", "linux2"]:
        subprocess.run(["shutdown", "-h", "+" + str(minutes)])
    else:
        print("Unsupported OS")

def cancel_shutdown():
    global shutdown_time
    shutdown_time = None
    update_countdown()
    if sys.platform == "win32":
        subprocess.run(["shutdown", "/a"])
    elif sys.platform in ["linux", "linux2"]:
        subprocess.run(["shutdown", "-c"])
    else:
        print("Unsupported OS")

def update_countdown():
    remaining = int(shutdown_time - time.time()) if shutdown_time else 0
    if remaining > 0:
        countdown_label.config(text=f"Tiempo restante: {remaining//60} min {remaining%60} seg")
        app.after(1000, update_countdown)
    else:
        countdown_label.config(text="No hay apagado programado")

app = tk.Tk()
app.title("Programar Apagado")

# Initialize shutdown_time
shutdown_time = None

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

# Etiqueta para mostrar la cuenta atrás
countdown_label = ttk.Label(app, text="No hay apagado programado")
countdown_label.pack()

app.mainloop()
