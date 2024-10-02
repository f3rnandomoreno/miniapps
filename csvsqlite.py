import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import sqlite3
import pandas as pd

# Función para explorar archivo CSV
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, file_path)

# Función para cargar el archivo CSV en SQLite
def create_table_from_csv():
    file_path = entry_file_path.get()
    table_name = entry_table_name.get()
    
    if not file_path or not table_name:
        messagebox.showerror("Error", "Debe seleccionar un archivo CSV y especificar el nombre de la tabla.")
        return
    
    try:
        # Leer el archivo CSV
        df = pd.read_csv(file_path)
        
        # Conectar a la base de datos SQLite (crea la base si no existe)
        conn = sqlite3.connect('database.db')
        
        # Cargar el DataFrame a SQLite
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        conn.close()
        messagebox.showinfo("Éxito", f"Tabla '{table_name}' creada correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el archivo CSV: {str(e)}")

# Función para ejecutar la consulta SQL
def execute_query():
    query = text_query.get("1.0", tk.END).strip()
    
    if not query:
        messagebox.showerror("Error", "Debe ingresar una consulta SQL.")
        return
    
    try:
        # Conectar a la base de datos SQLite
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Ejecutar la consulta
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        # Mostrar los resultados en el Text widget
        text_result.delete("1.0", tk.END)
        text_result.insert(tk.END, "\t".join(columns) + "\n")
        for row in rows:
            text_result.insert(tk.END, "\t".join(str(value) for value in row) + "\n")
        
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error al ejecutar la consulta: {str(e)}")

# Crear la ventana principal
root = tk.Tk()
root.title("CSV a SQLite")
root.geometry("600x500")

# Etiqueta y campo para el archivo CSV
label_file_path = tk.Label(root, text="Selecciona el archivo CSV:")
label_file_path.pack(pady=5)

entry_file_path = tk.Entry(root, width=50)
entry_file_path.pack(pady=5)

button_browse = tk.Button(root, text="Browse", command=browse_file)
button_browse.pack(pady=5)

# Etiqueta y campo para el nombre de la tabla
label_table_name = tk.Label(root, text="Nombre de la tabla:")
label_table_name.pack(pady=5)

entry_table_name = tk.Entry(root, width=30)
entry_table_name.pack(pady=5)

# Botón para crear la tabla
button_create_table = tk.Button(root, text="Crear Tabla", command=create_table_from_csv)
button_create_table.pack(pady=10)

# Área de texto para ingresar la consulta SQL
label_query = tk.Label(root, text="Escribe tu consulta SQL:")
label_query.pack(pady=5)

text_query = tk.Text(root, height=5, width=60)
text_query.pack(pady=5)

# Botón para ejecutar la consulta SQL
button_execute_query = tk.Button(root, text="Ejecutar Consulta", command=execute_query)
button_execute_query.pack(pady=10)

# Área de texto para mostrar los resultados
label_result = tk.Label(root, text="Resultados de la consulta:")
label_result.pack(pady=5)

text_result = tk.Text(root, height=10, width=60)
text_result.pack(pady=5)

# Ejecutar el bucle principal de la ventana
root.mainloop()
