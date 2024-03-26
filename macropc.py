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

        for i, action in enumerate(self.recorded_actions):
            if not self.playing:
                break
            update_playback(i)
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
        action_desc = f"{action[0]}: {action[1:]}" if action[0] == 'mouse' else f"{action[0]}: {action[1]}, {action[2]}"
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
        # Ordenar las selecciones en orden inverso para evitar problemas de índice
        selections = sorted(selections, reverse=True)
        for index in selections:
            del self.recorder.recorded_actions[index]
            self.action_list.delete(index)
        if self.playback_index is not None and index <= self.playback_index:
            self.playback_index = None

app = Application()
app.mainloop()