import tkinter as tk
from tkinter import filedialog, messagebox
import os
import chardet

class TextViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Viewer")
        self.root.state("zoomed")

        self.filter_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.data = []
        self.filtered_data = []
        self.search_positions = []
        self.current_search_index = -1

        self.create_widgets()
        self.setup_shortcuts()

    def create_widgets(self):
        # Crear barra de menú
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Text File", command=self.load_text_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Crear marco de búsqueda y filtro
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        # Crear etiqueta y entrada para el filtro
        filter_label = tk.Label(search_frame, text="Filter:")
        filter_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W)

        filter_entry = tk.Entry(search_frame, textvariable=self.filter_var)
        filter_entry.grid(row=0, column=1, padx=(0, 10), pady=5, sticky=tk.EW)
        filter_entry.bind("<KeyRelease>", self.update_text_widget)

        # Crear etiqueta y entrada para la búsqueda
        search_label = tk.Label(search_frame, text="Search:")
        search_label.grid(row=0, column=2, padx=(10, 10), pady=5, sticky=tk.W)

        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=3, padx=(0, 10), pady=5, sticky=tk.EW)
        search_entry.bind("<KeyRelease>", self.highlight_search_term)

        search_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(3, weight=1)

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

        # Bind events
        self.text_widget.bind("<Double-1>", self.show_full_csv)
        self.text_widget.bind("<Button-1>", self.click_search_result)

    def setup_shortcuts(self):
        self.root.bind('<Control-o>', lambda event: self.load_text_file())
        self.root.bind('<Control-v>', lambda event: self.paste_text())
        self.root.bind('<Alt-Right>', self.focus_next_search_result)
        self.root.bind('<Alt-Left>', self.focus_previous_search_result)

    def load_text_file(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    raw_data = file.read()
                    result = chardet.detect(raw_data)
                    encoding = result['encoding']

                with open(file_path, 'r', encoding=encoding) as file:
                    content = file.read()
                
                self.process_text(content)
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el archivo de texto: {e}")

    def paste_text(self, event=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("Paste Text")
        dialog.geometry("600x400")

        text_input = tk.Text(dialog, wrap=tk.WORD)
        text_input.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        def submit():
            content = text_input.get("1.0", tk.END).strip()
            if content:
                self.process_text(content)
            dialog.destroy()

        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(button_frame, text="OK", command=submit).pack(side=tk.RIGHT)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=10)

        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

    def process_text(self, content):
        # Dividir el contenido en líneas y eliminar líneas vacías
        self.data = [line.strip() for line in content.split('\n') if line.strip()]
        self.data.sort()
        self.update_text_widget()

    def update_text_widget(self, event=None):
        filter_term = self.filter_var.get().lower()
        self.text_widget.delete(1.0, tk.END)
        self.filtered_data = [line for line in self.data if filter_term in line.lower()]
        for line in self.filtered_data:
            self.text_widget.insert(tk.END, line + '\n')

        # Eliminar la etiqueta "highlight" si existe
        self.text_widget.tag_remove("highlight", "1.0", tk.END)
        self.highlight_search_term()

    def highlight_search_term(self, event=None):
        search_term = self.search_var.get().lower()
        self.text_widget.tag_remove("search_highlight", "1.0", tk.END)
        self.search_positions = []
        if search_term:
            start_pos = "1.0"
            while True:
                start_pos = self.text_widget.search(search_term, start_pos, tk.END, nocase=1)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(search_term)}c"
                self.text_widget.tag_add("search_highlight", start_pos, end_pos)
                self.search_positions.append((start_pos, end_pos))
                start_pos = end_pos

            self.text_widget.tag_config("search_highlight", background="blue", foreground="white")

        self.current_search_index = -1

    def focus_next_search_result(self, event=None):
        if self.search_positions:
            self.current_search_index = (self.current_search_index + 1) % len(self.search_positions)
            start_pos, end_pos = self.search_positions[self.current_search_index]
            self.text_widget.see(start_pos)
            self.text_widget.tag_remove("current_search", "1.0", tk.END)
            self.text_widget.tag_add("current_search", start_pos, end_pos)
            self.text_widget.tag_config("current_search", background="green", foreground="white")

    def focus_previous_search_result(self, event=None):
        if self.search_positions:
            self.current_search_index = (self.current_search_index - 1) % len(self.search_positions)
            start_pos, end_pos = self.search_positions[self.current_search_index]
            self.text_widget.see(start_pos)
            self.text_widget.tag_remove("current_search", "1.0", tk.END)
            self.text_widget.tag_add("current_search", start_pos, end_pos)
            self.text_widget.tag_config("current_search", background="green", foreground="white")

    def click_search_result(self, event):
        # Obtener el índice de la posición donde se hizo clic
        index = self.text_widget.index(f"@{event.x},{event.y}")
        # Buscar la etiqueta "search_highlight" en esa posición
        tags = self.text_widget.tag_names(index)
        if "search_highlight" in tags:
            self.text_widget.tag_remove("current_search", "1.0", tk.END)
            for i, (start_pos, end_pos) in enumerate(self.search_positions):
                if self.text_widget.compare(start_pos, "<=", index) and self.text_widget.compare(end_pos, ">", index):
                    self.current_search_index = i
                    self.text_widget.tag_add("current_search", start_pos, end_pos)
                    self.text_widget.tag_config("current_search", background="green", foreground="white")
                    break

    def show_full_csv(self, event):
        # Obtener el índice de la línea donde se hizo doble clic
        index = self.text_widget.index(f"@{event.x},{event.y}")
        line_number = int(index.split(".")[0])
        line_text = self.text_widget.get(f"{line_number}.0", f"{line_number}.end").strip()

        # Verificar si hay un bloque seleccionado dentro de la fila
        selected_tag_ranges = self.text_widget.tag_ranges("current_search")
        selected_in_line = False
        for i in range(0, len(selected_tag_ranges), 2):
            start = selected_tag_ranges[i]
            end = selected_tag_ranges[i + 1]
            if self.text_widget.compare(start, ">=", f"{line_number}.0") and self.text_widget.compare(end, "<=", f"{line_number}.end"):
                selected_in_line = True
                break

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

        # Volver a resaltar los términos de búsqueda actuales
        self.highlight_search_term()

        # Si había un bloque seleccionado dentro de la fila, resaltarlo
        if selected_in_line:
            self.text_widget.tag_remove("current_search", "1.0", tk.END)
            self.text_widget.tag_add("current_search", start, end)
            self.text_widget.tag_config("current_search", background="green", foreground="white")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextViewerApp(root)
    root.mainloop()
