import tkinter as tk
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
            if self.last_action_time is not None:
                delay = current_time - self.last_action_time
            else:
                delay = 0
            self.recorded_actions.append(('keyboard', 'press', key, delay))
            self.update_callback(self.recorded_actions[-1])
            self.last_action_time = current_time  # Actualizar el tiempo de la última acción

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
                press_or_release, key = details  # Cambio aquí
                time.sleep(recorded_delay)  # Utilizar el tiempo registrado
                try:
                    key_action = eval(key) if isinstance(key, str) else key
                    if press_or_release == 'press':
                        keyboard_controller.press(key_action)
                    else:
                        keyboard_controller.release(key_action)
                except Exception as e:
                    print(f"Error al simular la tecla: {e}")

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.recorder = MouseKeyboardRecorder(self.update_list)
        self.create_widgets()
        self.playback_index = None
        self.configure_grid()

    def create_widgets(self):
        self.record_button = tk.Button(self, text="Grabar", command=self.start_recording)
        self.record_button.grid(row=0, column=0, sticky='nsew')

        self.play_button = tk.Button(self, text="Reproducir", command=self.play_recording)
        self.play_button.grid(row=1, column=0, sticky='nsew')

        self.action_list = tk.Listbox(self, selectmode=tk.EXTENDED)
        self.action_list.grid(row=3, column=0, sticky='nsew')
        self.action_list.bind('<Delete>', self.delete_selected_action)

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

app = Application()
app.mainloop()