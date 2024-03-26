import tkinter as tk
from pynput import mouse, keyboard
import threading
import time

def get_key_from_string(key_str):
    try:
        # Para teclas especiales como 'Key.f1', 'Key.space', etc.
        if key_str.startswith('Key.'):
            return getattr(keyboard.Key, key_str.split('.')[1])
        # Para caracteres individuales como letras y números
        else:
            return keyboard.KeyCode.from_char(key_str)
    except AttributeError:
        # En caso de que la tecla no sea reconocida
        return None


class MouseKeyboardRecorder:
    def __init__(self, update_callback):
        self.recorded_actions = []
        self.recording = False
        self.update_callback = update_callback
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)

    def on_click(self, x, y, button, pressed):
        if self.recording:
            action = ('mouse', x, y, str(button), pressed)
            self.recorded_actions.append(action)
            self.update_callback(action)

    def on_press(self, key):
        if self.recording:
            action = ('keyboard', str(key))
            self.recorded_actions.append(action)
            self.update_callback(action)

    def start_recording(self):
        self.recording = True
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop_recording(self):
        self.recording = False
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

    def play_actions(self, update_playback):
        mouse_controller = mouse.Controller()
        keyboard_controller = keyboard.Controller()

        for i, action in enumerate(self.recorded_actions):
            update_playback(i)
            if action[0] == 'mouse':
                _, x, y, button, pressed = action
                mouse_controller.position = (x, y)
                if pressed:
                    mouse_controller.press(eval('mouse.' + button))
                else:
                    mouse_controller.release(eval('mouse.' + button))

            elif action[0] == 'keyboard':
                _, key_str = action
                key = get_key_from_string(key_str)
                if key:
                    keyboard_controller.press(key)
                    keyboard_controller.release(key)
            time.sleep(0.1)  # Delay for demonstration purposes

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.recorder = MouseKeyboardRecorder(self.update_list)
        self.create_widgets()
        self.playback_index = None

    def create_widgets(self):
        self.record_button = tk.Button(self, text="Grabar", command=self.start_recording)
        self.record_button.pack()

        self.play_button = tk.Button(self, text="Reproducir", command=self.play_recording)
        self.play_button.pack()

        self.action_list = tk.Listbox(self)
        self.action_list.pack()

        self.clear_button = tk.Button(self, text="Borrar todas las acciones", command=self.clear_actions)
        self.clear_button.pack()

        self.delete_button = tk.Button(self, text="Borrar acción seleccionada", command=self.delete_selected_action)
        self.delete_button.pack()

    def start_recording(self):
        self.recorder.start_recording()
        self.record_button.config(text="Detener Grabación", command=self.stop_recording)
        self.clear_actions()

    def stop_recording(self):
        self.recorder.stop_recording()
        self.record_button.config(text="Grabar", command=self.start_recording)

    def play_recording(self):
        play_thread = threading.Thread(target=lambda: self.recorder.play_actions(self.update_playback))
        play_thread.start()

    def update_list(self, action):
        self.action_list.insert(tk.END, f"{action[0]}: {action[1:]}")

    def update_playback(self, index):
        if self.playback_index is not None:
            self.action_list.itemconfig(self.playback_index, {'bg': 'white'})
        self.playback_index = index
        self.action_list.itemconfig(index, {'bg': 'lightgreen'})
        self.action_list.see(index)

    def clear_actions(self):
        self.recorder.recorded_actions.clear()
        self.action_list.delete(0, tk.END)

    def delete_selected_action(self):
        selection = self.action_list.curselection()
        if selection:
            index = selection[0]
            del self.recorder.recorded_actions[index]
            self.action_list.delete(index)

app = Application()
app.mainloop()
