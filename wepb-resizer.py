import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os
from tkinter.ttk import Progressbar
from tqdm import tqdm

# Función para seleccionar imágenes
def seleccionar_imagenes():
    archivos = filedialog.askopenfilenames(
        title="Selecciona las imágenes",
        filetypes=[("Imágenes WebP", "*.webp")])
    
    if archivos:
        lista_imagenes.delete(0, tk.END)  # Limpiar lista
        for archivo in archivos:
            lista_imagenes.insert(tk.END, archivo)

# Función para redimensionar las imágenes
def redimensionar_imagenes():
    try:
        # Obtener la nueva anchura
        nueva_anchura = int(entry_anchura.get())
    except ValueError:
        messagebox.showerror("Error", "Por favor, introduce un valor numérico válido para la anchura.")
        return

    archivos = lista_imagenes.get(0, tk.END)
    if not archivos:
        messagebox.showwarning("Advertencia", "No se han seleccionado imágenes.")
        return

    # Directorio de guardado
    directorio_guardado = filedialog.askdirectory(title="Selecciona el directorio para guardar las imágenes redimensionadas")
    if not directorio_guardado:
        return

    # Barra de progreso
    progress_bar["maximum"] = len(archivos)
    progress_bar["value"] = 0

    for i, archivo in enumerate(tqdm(archivos)):
        try:
            img = Image.open(archivo)
            ratio = nueva_anchura / float(img.size[0])
            nueva_altura = int((float(img.size[1]) * float(ratio)))
            
            # Redimensionar imagen
            img_redimensionada = img.resize((nueva_anchura, nueva_altura), Image.Resampling.LANCZOS)

            
            # Guardar la nueva imagen
            nombre_archivo = os.path.basename(archivo)
            ruta_guardado = os.path.join(directorio_guardado, nombre_archivo)
            img_redimensionada.save(ruta_guardado)
            
            progress_bar["value"] += 1
            root.update_idletasks()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al redimensionar la imagen {archivo}.\nError: {str(e)}")
            return

    messagebox.showinfo("Finalizado", "Las imágenes han sido redimensionadas correctamente.")

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Redimensionador de imágenes WebP")
root.geometry("500x400")

# Frame para selección de imágenes
frame_seleccion = tk.Frame(root)
frame_seleccion.pack(pady=10)

btn_seleccionar = tk.Button(frame_seleccion, text="Seleccionar imágenes", command=seleccionar_imagenes)
btn_seleccionar.pack()

lista_imagenes = tk.Listbox(root, width=60, height=10)
lista_imagenes.pack(pady=10)

# Frame para redimensionar
frame_redimension = tk.Frame(root)
frame_redimension.pack(pady=10)

label_anchura = tk.Label(frame_redimension, text="Nueva anchura (px):")
label_anchura.pack(side=tk.LEFT)

entry_anchura = tk.Entry(frame_redimension)
entry_anchura.pack(side=tk.LEFT)

btn_redimensionar = tk.Button(root, text="Redimensionar imágenes", command=redimensionar_imagenes)
btn_redimensionar.pack(pady=10)

# Barra de progreso
progress_bar = Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='determinate')
progress_bar.pack(pady=10)

# Iniciar la aplicación
root.mainloop()
