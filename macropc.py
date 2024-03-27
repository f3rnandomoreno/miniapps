import tkinter as tk
from tkinter import ttk
from pynput import mouse, keyboard
import threading
import time

class MouseKeyboardRecorder:
    def __init__(self, update_callback):
        self.recorded_actions = []
        self.recording = False
        self.playing = False
        self.update_callback = update_callback
        self.mouse_listener = None
        self.keyboard_listener = None
        self.play_thread = None

    def on_click(self, x, y, button, pressed):
        if self.recording:
            self.recorded_actions.append(('mouse', x, y, str(button), pressed))
            self.update_callback(self.recorded_actions[-1])

    def on_press(self, key):
        if self.recording:
            self.recorded_actions.append(('keyboard', 'press', key))
            self.update_callback(self.recorded_actions[-1])

    def on_release(self, key):
        if self.recording:
            self.recorded_actions.append(('keyboard', 'release', key))
            self.update_callback(self.recorded_actions[-1])

    def start_recording(self):
        self.recording = True
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop_recording(self):
        self.recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()

    def play_actions(self, update_playback):
        self.playing = True
        mouse_controller = mouse.Controller()
        keyboard_controller = keyboard.Controller()

        for action in self.recorded_actions:
            if not self.playing:
                break
            update_playback(action)  # Pasar la acción en lugar del índice
            action_type, *details = action

            if action_type == 'mouse':
                x, y, button, pressed = details
                mouse_controller.position = (x, y)
                if pressed:
                    mouse_controller.press(eval('mouse.' + button))
                else:
                    mouse_controller.release(eval('mouse.' + button))

            elif action_type == 'keyboard':
                press_or_release, key = details
                try:
                    if press_or_release == 'press':
                        keyboard_controller.press(key)
                    else:
                        keyboard_controller.release(key)
                except Exception as e:
                    print(f"Error al simular la tecla: {e}")
            time.sleep(0.1)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.recorder = MouseKeyboardRecorder(self.update_list)
        self.playback_index = None
        self.configure_grid()
        self.action_id_map = {}  # Añadir un nuevo diccionario para mapear los ID de los elementos a las acciones
        self.create_widgets()

    def create_widgets(self):
        self.record_button = tk.Button(self, text="Grabar", command=self.start_recording)
        self.record_button.grid(row=0, column=0, sticky='nsew')

        self.play_button = tk.Button(self, text="Reproducir", command=self.play_recording)
        self.play_button.grid(row=1, column=0, sticky='nsew')

        self.action_tree = ttk.Treeview(self)
        self.action_tree.grid(row=3, column=0, sticky='nsew')
        self.action_tree.bind('<Delete>', self.delete_selected_action)
        self.action_tree["columns"]=("one","two","three","four")
        self.action_tree.column("#0", width=100 )
        self.action_tree.column("one", width=100 )
        self.action_tree.column("two", width=100)
        self.action_tree.column("three", width=100)
        self.action_tree.column("four", width=100)
        self.action_tree.heading("#0",text="Tipo")
        self.action_tree.heading("one", text="Detalle 1")
        self.action_tree.heading("two", text="Detalle 2")
        self.action_tree.heading("three", text="Detalle 3")
        self.action_tree.heading("four", text="Detalle 4")

        # Inicializar el último tipo de acción y el último elemento padre a None
        self.last_action_type = None
        self.last_parent = None

        # Crear elementos padre para cada tipo de acción
        # self.mouse_parent = self.action_tree.insert('', 'end', text='mouse')
        # self.keyboard_parent = self.action_tree.insert('', 'end', text='keyboard')

        self.clear_button = tk.Button(self, text="Borrar todas las acciones", command=self.clear_actions)
        self.clear_button.grid(row=5, column=0, sticky='nsew')

        self.delete_button = tk.Button(self, text="Borrar acción seleccionada", command=self.delete_selected_action)
        self.delete_button.grid(row=4, column=0, sticky='nsew')

    def configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        for i in range(6):
            self.grid_rowconfigure(i, weight=1)

    def start_recording(self):
        self.recorder.start_recording()
        self.record_button.config(text="Detener Grabación", command=self.stop_recording)

    def stop_recording(self):
        self.recorder.stop_recording()
        self.record_button.config(text="Grabar", command=self.start_recording)

    def play_recording(self):
        self.last_action_type = None
        self.last_parent = None
        self.recorder.play_thread = threading.Thread(target=lambda: self.recorder.play_actions(self.update_playback))
        self.recorder.play_thread.start()

    def update_list(self, action):
        action_type, *details = action
        if action_type != self.last_action_type:
            self.last_parent = self.action_tree.insert('', 'end', text=action_type)
            self.last_action_type = action_type
        new_item = self.action_tree.insert(self.last_parent, 'end', text=action_type, values=details)
        self.action_tree.item(self.last_parent, open=True)
        self.action_tree.see(new_item)
        self.action_id_map[new_item] = action

    def update_playback(self, action):
        action_type, *details = action
        if action_type != self.last_action_type:
            # Si el tipo de acción ha cambiado, crear un nuevo elemento padre
            self.last_parent = self.action_tree.insert('', 'end', text=action_type)
            self.last_action_type = action_type
        # Insertar la acción como un elemento hijo del último elemento padre
        new_item = self.action_tree.insert(self.last_parent, 'end', text=action_type, values=details)
        # Desplegar el elemento padre
        self.action_tree.item(self.last_parent, open=True)
        # Desplazarse hacia abajo hasta el nuevo elemento
        self.action_tree.see(new_item)

    def clear_actions(self):
        self.recorder.recorded_actions.clear()
        for item in self.action_tree.get_children():
            self.action_tree.delete(item)
        self.action_id_map.clear()  # Clear the action_id_map as well
        self.playback_index = None

    def delete_selected_action(self, event=None):
        selected_items = self.action_tree.selection()
        for item_id in selected_items:
            if item_id in self.action_id_map:
                action = self.action_id_map[item_id]
                self.recorder.recorded_actions.remove(action)
                self.action_tree.delete(item_id)
                del self.action_id_map[item_id]
        self.playback_index = None

app = Application()
app.mainloop()