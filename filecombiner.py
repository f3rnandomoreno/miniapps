import tkinter as tk
from tkinter import filedialog
import os
from datetime import datetime

def seleccionar_directorio():
    directorio = filedialog.askdirectory()
    if directorio:
        combinar_archivos(directorio)

def combinar_archivos(directorio):
    # Obtén la fecha y hora actuales y formatea como cadena
    ahora = datetime.now()
    fecha_hora = ahora.strftime("%Y%m%d_%H%M%S")
    
    # Agrega la fecha y hora al nombre del archivo de salida
    nombre_fichero_salida = f'ficheros_{fecha_hora}.txt'
    
    with open(nombre_fichero_salida, 'w') as fichero_salida:
        for ruta, _, archivos in os.walk(directorio):
            for nombre_archivo in archivos:
                ruta_archivo = os.path.join(ruta, nombre_archivo)
                if os.path.isfile(ruta_archivo):
                    fichero_salida.write(f"### {nombre_archivo}\n")
                    with open(ruta_archivo, 'r', errors='ignore') as fichero_entrada:
                        contenido = fichero_entrada.read()
                        fichero_salida.write(contenido + "\n\n")

root = tk.Tk()
root.title("FileCombiner")

boton = tk.Button(root, text="Seleccionar Directorio", command=seleccionar_directorio)
boton.pack(pady=20)

root.mainloop()