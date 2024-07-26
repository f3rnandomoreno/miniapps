import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import pandas as pd
import os

class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Viewer")

        self.search_var = tk.StringVar()
        self.data = []

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
                    df = pd.read_csv(file_path, header=None)
                    df = df.drop_duplicates()  # Eliminar duplicados
                    self.data = df.astype(str).values.flatten().tolist()
                    self.data.sort()
                    self.update_text_widget()
                else:
                    raise FileNotFoundError(f"No such file: '{file_path}'")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV file: {e}")

    def on_drop(self, event):
        file_path = event.data
        if file_path:
            self.load_csv(file_path)

    def update_text_widget(self, event=None):
        search_term = self.search_var.get().lower()
        self.text_widget.delete(1.0, tk.END)
        for line in self.data:
            if search_term in line.lower():
                self.text_widget.insert(tk.END, line + '\n')

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = CSVViewerApp(root)
    root.mainloop()