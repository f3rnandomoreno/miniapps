import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import pandas as pd
import os
import chardet

class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Viewer")

        self.search_var = tk.StringVar()
        self.data = []
        self.filtered_data = []

        self.create_widgets()
        self.setup_dnd()

    def create_widgets(self):
        # Crear barra de menú
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open CSV", command=self.load_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Crear barra de búsqueda
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        search_label = tk.Label(search_frame, text="Search:")
        search_label.pack(side=tk.LEFT, padx=(0, 10))

        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(fill=tk.X, expand=True)
        search_entry.bind("<KeyRelease>", self.update_text_widget)

        # Crear Text widget y scrollbar
        self.text_widget = tk.Text(self.root, wrap=tk.NONE)
        self.text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar_y = tk.Scrollbar(self.text_widget, orient=tk.VERTICAL)
        scrollbar_y.config(command=self.text_widget.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        scrollbar_x = tk.Scrollbar(self.text_widget, orient=tk.HORIZONTAL)
        scrollbar_x.config(command=self.text_widget.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.text_widget.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Bind double-click event
        self.text_widget.bind("<Double-1>", self.show_full_csv)

    def setup_dnd(self):
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

    def load_csv(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                # Limpiar la ruta del archivo
                file_path = file_path.strip().replace('{', '').replace('}', '')

                # Verificar si la ruta del archivo es válida
                if os.path.isfile(file_path):
                    # Detectar la codificación del archivo
                    with open(file_path, 'rb') as file:
                        raw_data = file.read()
                        result = chardet.detect(raw_data)
                        encoding = result['encoding']

                    # Leer el archivo CSV con la codificación detectada
                    df = pd.read_csv(file_path, header=None, encoding=encoding)
                    df = df.drop_duplicates()  # Eliminar duplicados
                    self.data = df.apply(lambda row: ', '.join(row.astype(str)), axis=1).tolist()
                    self.data.sort()
                    self.update_text_widget()
                    messagebox.showinfo("Éxito", f"Archivo cargado correctamente. Codificación detectada: {encoding}")
                else:
                    raise FileNotFoundError(f"No existe el archivo: '{file_path}'")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el archivo CSV: {e}")

    def on_drop(self, event):
        file_path = event.data
        if file_path:
            self.load_csv(file_path)

    def update_text_widget(self, event=None):
        search_term = self.search_var.get().lower()
        self.text_widget.delete(1.0, tk.END)
        self.filtered_data = [line for line in self.data if search_term in line.lower()]
        for line in self.filtered_data:
            self.text_widget.insert(tk.END, line + '\n')
        
        # Eliminar la etiqueta "highlight" si existe
        self.text_widget.tag_remove("highlight", "1.0", tk.END)

    def show_full_csv(self, event):
        # Obtener el índice de la línea donde se hizo doble clic
        index = self.text_widget.index("@%d,%d" % (event.x, event.y))
        line_number = int(index.split(".")[0])
        line_text = self.text_widget.get(f"{line_number}.0", f"{line_number}.end").strip()

        # Encontrar el índice de la línea en self.data
        try:
            original_index = self.data.index(line_text)
        except ValueError:
            return  # Si no se encuentra la línea, salir

        # Mostrar todas las líneas en el Text widget
        self.text_widget.delete(1.0, tk.END)
        for i, line in enumerate(self.data):
            self.text_widget.insert(tk.END, line + '\n')
            if i == original_index:
                self.text_widget.tag_add("highlight", f"{i+1}.0", f"{i+1}.end")

        # Configurar la etiqueta "highlight" para resaltar la línea seleccionada
        self.text_widget.tag_config("highlight", background="yellow")

        # Mantener el foco del scroll en la línea donde se hizo doble clic
        self.text_widget.see(f"{original_index + 1}.0")

        # Limpiar la barra de búsqueda
        self.search_var.set("")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = CSVViewerApp(root)
    root.mainloop()
