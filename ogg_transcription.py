import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment
import speech_recognition as sr
import os

def convert_and_transcribe():
    # Abrir diálogo para seleccionar archivo
    file_path = filedialog.askopenfilename(
        filetypes=[("OGG files", "*.ogg"), ("All files", "*.*")]
    )
    
    if not file_path:
        return

    try:
        # Convertir OGG a WAV
        audio = AudioSegment.from_ogg(file_path)
        wav_path = file_path.replace(".ogg", ".wav")
        audio.export(wav_path, format="wav")
        
        # Transcribir el archivo de audio
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="es-ES")
        
        # Guardar la transcripción en un archivo .txt
        txt_path = file_path.replace(".ogg", ".txt")
        with open(txt_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(text)
        
        # Mostrar un mensaje de confirmación
        messagebox.showinfo("Éxito", f"Transcripción guardada en: {txt_path}")
        
        # Eliminar archivo WAV temporal
        os.remove(wav_path)
    
    except Exception as e:
        messagebox.showerror("Error", f"Algo salió mal: {str(e)}")

# Crear la ventana principal
root = tk.Tk()
root.title("Conversor y Transcriptor de Audio")

# Añadir un botón para seleccionar el archivo y ejecutar la transcripción
btn_transcribir = tk.Button(root, text="Seleccionar archivo OGG y transcribir", command=convert_and_transcribe)
btn_transcribir.pack(pady=20)

# Ejecutar la aplicación
root.mainloop()
