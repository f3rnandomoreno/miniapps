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
            action = ('mouse', x, y, str(button), pressed)
            self.recorded_actions.append(action)
            self.update_callback(action)

    def on_press(self, key):
        if self.recording:
            action = ('keyboard', 'press', key)
            self.recorded_actions.append(action)
            self.update_callback(action)

    def on_release(self, key):
        if self.recording:
            action = ('keyboard', 'release', key)
            self.recorded_actions.append(action)
            self.update_callback(action)

    def start_recording(self):
        self.stop_playing()
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

    def stop_playing(self):
        self.playing = False
        if self.play_thread:
            self.play_thread.join()
            self.play_thread = None

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

        self.stop_play_button = tk.Button(self, text="Detener Reproducción", command=self.stop_playing)
        self.stop_play_button.pack()

        self.action_list = tk.Listbox(self)
        self.action_list.pack()

        self.clear_button = tk.Button(self, text="Borrar todas las acciones", command=self.clear_actions)
        self.clear_button.pack()

        self.delete_button = tk.Button(self, text="Borrar acción seleccionada", command=self.delete_selected_action)
        self.delete_button.pack()

    def start_recording(self):
        self.recorder.start_recording()
        self.record_button.config(text="Detener Grabación", command=self.stop_recording)

    def stop_recording(self):
        self.recorder.stop_recording()
        self.record_button.config(text="Grabar", command=self.start_recording)

    def play_recording(self):
        self.recorder.stop_playing()
        self.recorder.play_thread = threading.Thread(target=lambda: self.recorder.play_actions(self.update_playback))
        self.recorder.play_thread.start()

    def stop_playing(self):
        self.recorder.stop_playing()

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
        self.recorder.stop_playing()
        self.recorder.recorded_actions.clear()
        self.action_list.delete(0, tk.END)

    def delete_selected_action(self):
        self.recorder.stop_playing()
        selection = self.action_list.curselection()
        if selection:
            index = selection[0]
            del self.recorder.recorded_actions[index]
            self.action_list.delete(index)

app = Application()
app.mainloop()
