import tkinter as tk
from pynput import mouse, keyboard
import threading

class MouseKeyboardRecorder:
    def __init__(self):
        self.recorded_actions = []
        self.recording = False
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)

    def on_click(self, x, y, button, pressed):
        if self.recording:
            self.recorded_actions.append(('mouse', x, y, button, pressed))

    def on_press(self, key):
        if self.recording:
            self.recorded_actions.append(('keyboard', key))

    def start_recording(self):
        self.recording = True
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop_recording(self):
        self.recording = False
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

    def play_actions(self):
        for action in self.recorded_actions:
            if action[0] == 'mouse':
                _, x, y, button, pressed = action
                with mouse.Controller() as mouse_controller:
                    mouse_controller.position = (x, y)
                    if pressed:
                        mouse_controller.press(button)
                    else:
                        mouse_controller.release(button)

            elif action[0] == 'keyboard':
                _, key = action
                with keyboard.Controller() as keyboard_controller:
                    keyboard_controller.press(key)
                    keyboard_controller.release(key)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.recorder = MouseKeyboardRecorder()
        self.create_widgets()

    def create_widgets(self):
        self.record_button = tk.Button(self, text="Grabar", command=self.start_recording)
        self.record_button.pack()

        self.play_button = tk.Button(self, text="Reproducir", command=self.play_recording)
        self.play_button.pack()

    def start_recording(self):
        self.recorder.start_recording()
        self.record_button.config(text="Detener Grabación", command=self.stop_recording)

    def stop_recording(self):
        self.recorder.stop_recording()
        self.record_button.config(text="Grabar", command=self.start_recording)

    def play_recording(self):
        play_thread = threading.Thread(target=self.recorder.play_actions)
        play_thread.start()

app = Application()
app.mainloop()