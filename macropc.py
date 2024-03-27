import tkinter as tk
from tkinter import simpledialog
from pynput import mouse, keyboard
import threading
import time
import json
import os

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
            self.recorded_actions.append(('keyboard', 'release', key, delay))
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
        # Convertir los objetos Key a string antes de guardar
        def default(o):
            if isinstance(o, keyboard.Key):
                return {'type': 'Key', 'key': o.name}
            elif isinstance(o, keyboard.KeyCode):
                return {'type': 'KeyCode', 'char': o.char, 'vk': o.vk}
            raise TypeError(f'Object of type {o.__class__.__name__} is not JSON serializable')


        with open(f'{name}.json', 'w') as file:
            json.dump(action_group, file, default=default)

    
    def load_action_group(self, name):
        try:
            with open(f'{name}.json', 'r') as file:
                self.recorded_actions = json.load(file)
                for action in self.recorded_actions:
                    if action.get('type') == 'Key':
                        key = keyboard.Key[action['key']]
                    elif action.get('type') == 'KeyCode':
                        if action.get('char'):
                            key = keyboard.KeyCode(char=action['char'])
                        else:
                            key = keyboard.KeyCode.from_vk(action['vk'])
                    self.recorded_actions.append(('keyboard', 'press', key, delay))

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
        # Lista de grupos
        self.group_list_label = tk.Label(self, text="Grupos de Acciones")
        self.group_list_label.grid(row=0, column=0, sticky='nsew')
        
        self.group_list = tk.Listbox(self, selectmode=tk.SINGLE)
        self.group_list.grid(row=1, column=0, rowspan=4, sticky='nsew')
        self.group_list.bind('<<ListboxSelect>>', self.load_selected_group)

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
        for i in range(6):
            self.grid_rowconfigure(i, weight=1)

    def start_recording(self):
        self.recorder.start_recording()
        self.record_button.config(text="Detener Grabación", command=self.stop_recording)

    def stop_recording(self):
        self.recorder.stop_recording()
        self.record_button.config(text="Grabar", command=self.start_recording)

    def play_recording(self):
        self.recorder.play_thread = threading.Thread(target=lambda: self.recorder.play_actions(self.update_playback))
        self.recorder.play_thread.start()

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
        if name:
            self.action_groups[name] = self.recorder.recorded_actions.copy()
            self.recorder.save_action_group(name, self.recorder.recorded_actions)
            self.group_list.insert(tk.END, name)



    def load_selected_group(self, event=None):
        selection = self.group_list.curselection()
        if selection:
            name = self.group_list.get(selection[0])
            self.recorder.load_action_group(name)
            self.action_list.delete(0, tk.END)
            for action in self.recorder.recorded_actions:
                self.update_list(action)

    def load_action_groups(self):
        for file in os.listdir():
            if file.endswith('.json'):
                name = file.replace('.json', '')
                self.group_list.insert(tk.END, name)  

app = Application()
app.mainloop()