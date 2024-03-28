import tkinter as tk
from tkinter import simpledialog
from pynput import mouse, keyboard
import threading
import time
import os
import pickle

class MouseKeyboardRecorder:
    def __init__(self, update_callback):
        self.recorded_actions = []
        self.recording = False
        self.playing = False
        self.update_callback = update_callback
        self.mouse_listener = None
        self.keyboard_listener = None
        self.play_thread = None
        self.start_time = None  # Tiempo de inicio de la reproducción
        self.last_action_time = None  # Tiempo de la última acción

    def on_click(self, x, y, button, pressed):
        if self.recording:
            current_time = time.time()
            if self.last_action_time is not None:
                delay = current_time - self.last_action_time
            else:
                delay = 0
            self.recorded_actions.append(('mouse', x, y, str(button), pressed, delay))
            self.update_callback(self.recorded_actions[-1])
            self.last_action_time = current_time  # Actualizar el tiempo de la última acción

    def on_press(self, key):
        if self.recording:
            current_time = time.time()
            delay = current_time - self.last_action_time if self.last_action_time is not None else 0
            self.recorded_actions.append(('keyboard', 'press', key, delay))  # Cambiado 'release' a 'press'
            self.update_callback(self.recorded_actions[-1])
            self.last_action_time = current_time


    def on_release(self, key):
        if self.recording:
            current_time = time.time()
            if self.last_action_time is not None:
                delay = current_time - self.last_action_time
            else:
                delay = 0
            self.recorded_actions.append(('keyboard', 'release', key, delay))
            self.update_callback(self.recorded_actions[-1])
            self.last_action_time = current_time  # Actualizar el tiempo de la última acción

    def start_recording(self):
        self.recording = True
        self.last_action_time = time.time()  # Establecer el tiempo inicial de grabación
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

        self.start_time = time.time()  # Guardar el tiempo de inicio de la reproducción

        for i, action in enumerate(self.recorded_actions):
            if not self.playing:
                break
            update_playback(i)
            action_type, *details, recorded_delay = action

            if action_type == 'mouse':
                x, y, button, pressed = details
                time.sleep(recorded_delay)
                mouse_controller.position = (x, y)
                try:
                    if pressed:  # Si se debe presionar el botón
                        if button == 'Button.left':
                            mouse_controller.press(mouse.Button.left)
                            mouse_controller.release(mouse.Button.left)
                        elif button == 'Button.right':
                            mouse_controller.press(mouse.Button.right)
                            mouse_controller.release(mouse.Button.right)
                except Exception as e:
                    print(f"Error en la acción del ratón: {e}")

            elif action_type == 'keyboard':
                press_or_release, key = details
                time.sleep(recorded_delay)
                try:
                    if press_or_release == 'press':
                        keyboard_controller.press(key)
                    else:
                        keyboard_controller.release(key)
                except Exception as e:
                    print(f"Error al simular la tecla: {e}")
    
    def save_action_group(self, name, action_group):
        with open(f'{name}.auto', 'wb') as file:  # Guardar en formato binario con extensión .auto
            pickle.dump(action_group, file)

    
    def load_action_group(self, name):
        try:
            with open(f'{name}.auto', 'rb') as file:
                action_group = pickle.load(file)
            # Limpiar la lista de acciones actual antes de cargar las nuevas
            self.recorded_actions.clear()
            self.recorded_actions.extend(action_group)  # Cargar las nuevas acciones
        except Exception as e:
            print(f"Error al cargar el grupo de acciones: {e}")



class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("1024x600")
        self.title("Grabador de Acciones de Teclado y Ratón")
        self.recorder = MouseKeyboardRecorder(self.update_list)
        self.action_groups = {}
        self.create_widgets()
        self.playback_index = None
        self.configure_grid()
        self.load_action_groups()

    def create_widgets(self):         
        # Barra de búsqueda
        self.search_var = tk.StringVar()
        self.search_bar = tk.Entry(self, textvariable=self.search_var)
        self.search_bar.grid(row=0, column=0, sticky='nsew')
        self.search_bar.bind('<KeyRelease>', self.on_search)  # Evento para actualizar la lista mientras escribes

        # Etiqueta de lista de grupos
        self.group_list_label = tk.Label(self, text="Grupos de Acciones")
        self.group_list_label.grid(row=1, column=0, sticky='nsew')

        # Lista de grupos actualizada
        self.group_list = tk.Listbox(self, selectmode=tk.SINGLE)
        self.group_list.grid(row=2, column=0, rowspan=4, sticky='nsew')
        self.group_list.bind('<<ListboxSelect>>', self.load_selected_group)
        self.group_list.bind('<Return>', self.play_selected_group)  # Evento para reproducir al presionar Enter

        self.save_group_button = tk.Button(self, text="Guardar Grupo Actual", command=self.save_action_group)
        self.save_group_button.grid(row=5, column=0, sticky='nsew')

        # Controles de grabación y reproducción
        self.record_button = tk.Button(self, text="Iniciar Grabación", command=self.start_recording)
        self.record_button.grid(row=0, column=1, sticky='nsew')

        self.stop_button = tk.Button(self, text="Detener Grabación", command=self.stop_recording)
        self.stop_button.grid(row=1, column=1, sticky='nsew')

        self.play_button = tk.Button(self, text="Reproducir", command=self.play_recording)
        self.play_button.grid(row=2, column=1, sticky='nsew')

        # Lista de acciones
        self.action_list_label = tk.Label(self, text="Acciones Grabadas")
        self.action_list_label.grid(row=3, column=1, sticky='nsew')

        self.action_list = tk.Listbox(self, selectmode=tk.EXTENDED)
        self.action_list.grid(row=4, column=1, sticky='nsew')
        self.action_list.bind('<Delete>', self.delete_selected_action)

        self.clear_button = tk.Button(self, text="Borrar Todas las Acciones", command=self.clear_actions)
        self.clear_button.grid(row=5, column=1, sticky='nsew')

    def configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        for i in range(6):
            self.grid_rowconfigure(i, weight=1)

    # Función para actualizar la lista de grupos basada en la búsqueda
    def on_search(self, event=None):
        search_term = self.search_var.get().lower()
        self.group_list.delete(0, tk.END)  # Limpia la lista antes de la búsqueda

        # Vamos a buscar dentro de los nombres de archivo guardados en lugar de un diccionario
        # porque no se estaba llenando el diccionario en ningún otro lugar del código.
        for file in os.listdir():
            if file.endswith('.auto'):
                group_name = file.replace('.auto', '')
                if search_term in group_name.lower():
                    self.group_list.insert(tk.END, group_name)
    
    # Función para reproducir el grupo seleccionado
    def play_selected_group(self, event=None):
        selection = self.group_list.curselection()
        if selection:
            name = self.group_list.get(selection[0])
            self.recorder.load_action_group(name)
            self.play_recording()

    def start_recording(self):
        self.recorder.start_recording()
        self.record_button.config(text="Detener Grabación", command=self.stop_recording)
        self.iconify()

    def stop_recording(self):
        self.recorder.stop_recording()
        self.record_button.config(text="Grabar", command=self.start_recording)

    def play_recording(self):
        self.playback_index = 0  # Restablece el índice de reproducción al inicio
        self.recorder.play_thread = threading.Thread(target=lambda: self.recorder.play_actions(self.update_playback))
        self.recorder.play_thread.start()
        self.iconify()


    def update_list(self, action):
        action_type, *action_details, action_delay = action
        formatted_delay = "{:.4f}".format(action_delay)  # Esto formateará el delay a 4 dígitos decimales
        if action_type == 'mouse':
            x, y, button, pressed = action_details
            action_desc = f"Mouse ({x}, {y}, {button}, {pressed}) with delay {formatted_delay} seconds"
        elif action_type == 'keyboard':
            press_or_release, key = action_details
            action_desc = f"Keyboard ({press_or_release}, {key}) with delay {formatted_delay} seconds"
        self.action_list.insert(tk.END, action_desc)

    def update_playback(self, index):
        if self.playback_index is not None:
            self.action_list.itemconfig(self.playback_index, {'bg': 'white'})
        self.playback_index = index
        self.action_list.itemconfig(index, {'bg': 'lightgreen'})
        self.action_list.see(index)

    def clear_actions(self):
        self.recorder.recorded_actions.clear()
        self.action_list.delete(0, tk.END)
        self.playback_index = None

    def delete_selected_action(self, event=None):
        selections = self.action_list.curselection()
        selections = sorted(selections, reverse=True)
        for index in selections:
            del self.recorder.recorded_actions[index]
            self.action_list.delete(index)
        if self.playback_index is not None and index <= self.playback_index:
            self.playback_index = None
    
    def save_action_group(self):
        name = simpledialog.askstring("Guardar Grupo", "Nombre del grupo de acciones:", parent=self)
        if name:  # Verifica si el usuario proporcionó un nombre
            self.recorder.save_action_group(name, self.recorder.recorded_actions)
            self.group_list.insert(tk.END, name)  # Agrega el nuevo grupo a la lista de grupos
            self.action_groups[name] = self.recorder.recorded_actions.copy()  # Almacena las acciones grabadas en el diccionario
            self.on_search()  # Actualiza la lista de búsqueda

    def load_action_group(self, name):
        try:
            with open(f'{name}.auto', 'rb') as file:  # Usamos 'rb' para leer en modo binario
                action_group = pickle.load(file)
                
            self.recorded_actions = []
            for action in action_group:
                action_type, *details, delay = action
                if action_type == 'keyboard':
                    press_or_release, key = details
                    if isinstance(key, dict):
                        # Reconstruimos el objeto Key o KeyCode
                        if key['type'] == 'Key':
                            key = keyboard.Key[key['key']]
                        elif key['type'] == 'KeyCode':
                            char = key.get('char')
                            vk = key.get('vk')
                            key = keyboard.KeyCode(char=char, vk=vk)
                    # Aquí asumimos que el formato de acción es ('keyboard', 'press/release', key, delay)
                    self.recorded_actions.append((action_type, press_or_release, key, delay))

        except Exception as e:
            print(f"Error al cargar el grupo de acciones: {e}")

    def load_selected_group(self, event=None):
        selection = self.group_list.curselection()
        if selection:
            name = self.group_list.get(selection[0])
            self.recorder.load_action_group(name)
            self.action_list.delete(0, tk.END)  # Limpiar la lista de acciones actual
            # Actualizar la lista de acciones con las nuevas acciones cargadas
            for action in self.recorder.recorded_actions:
                self.update_list(action)

    def load_action_groups(self):
        for file in os.listdir():
            if file.endswith('.auto'):  # Cambiamos de .json a .auto
                name = file.replace('.auto', '')  # Aquí también
                self.group_list.insert(tk.END, name) 

app = Application()
app.mainloop()