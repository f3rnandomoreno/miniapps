import os
import tkinter as tk
from tkinter import filedialog, messagebox

def es_archivo_texto(archivo):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            f.read(1024)  # Intentamos leer los primeros 1024 bytes
        return True
    except UnicodeDecodeError:
        return False

def obtener_nombre_archivo_salida(base_nombre):
    contador = 1
    while os.path.exists(f"{base_nombre}_{contador}.txt"):
        contador += 1
    return f"{base_nombre}_{contador}.txt"

def procesar_directorio(directorio, limite_tamano_mb):
    limite_tamano = limite_tamano_mb * 1024 * 1024  # Convertir MB a bytes
    archivos_salida = []
    contenido_actual = ""
    tamano_actual = 0

    for raiz, _, archivos in os.walk(directorio):
        for archivo in archivos:
            ruta_completa = os.path.join(raiz, archivo)
            if es_archivo_texto(ruta_completa):
                ruta_relativa = os.path.relpath(ruta_completa, directorio)
                with open(ruta_completa, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                nuevo_contenido = f"<file>{ruta_relativa}</file>\n<file_content>{contenido}</file_content>\n\n"
                
                # Si agregar el nuevo contenido excederá el límite, guardamos el archivo actual y empezamos uno nuevo
                if tamano_actual + len(nuevo_contenido) > limite_tamano and tamano_actual > 0:
                    nombre_archivo = obtener_nombre_archivo_salida("salida")
                    with open(nombre_archivo, 'w', encoding='utf-8') as f:
                        f.write(contenido_actual)
                    archivos_salida.append(nombre_archivo)
                    
                    contenido_actual = ""
                    tamano_actual = 0
                
                contenido_actual += nuevo_contenido
                tamano_actual += len(nuevo_contenido)

    # Guardar el último archivo si queda contenido
    if contenido_actual:
        nombre_archivo = obtener_nombre_archivo_salida("salida")
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write(contenido_actual)
        archivos_salida.append(nombre_archivo)

    return archivos_salida

def seleccionar_directorio():
    directorio = filedialog.askdirectory()
    if directorio:
        try:
            limite_tamano_mb = float(entrada_limite.get())
            if limite_tamano_mb <= 0:
                raise ValueError("El límite debe ser un número positivo")
            archivos_generados = procesar_directorio(directorio, limite_tamano_mb)
            resultado = f"Archivos generados: {', '.join(archivos_generados)}"
            resultado_label.config(text=resultado)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Procesador de Archivos de Texto")
root.geometry("400x250")

# Frame para el límite de tamaño
frame_limite = tk.Frame(root)
frame_limite.pack(pady=10)

tk.Label(frame_limite, text="Límite de tamaño (MB):").pack(side=tk.LEFT)
entrada_limite = tk.Entry(frame_limite)
entrada_limite.pack(side=tk.LEFT)

boton_seleccionar = tk.Button(root, text="Seleccionar Directorio", command=seleccionar_directorio)
boton_seleccionar.pack(pady=10)

resultado_label = tk.Label(root, text="", wraplength=380)
resultado_label.pack(pady=10)

root.mainloop()