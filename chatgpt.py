import tkinter as tk
from tkinter import messagebox, simpledialog
import openai

class OpenAIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenAI Chat App")

        self.token = None
        self.models = []
        self.conversation = []
        self.max_tokens = 128000  # 128k tokens by default

        self.setup_ui()
    
    def setup_ui(self):
        self.token_label = tk.Label(self.root, text="API Token:")
        self.token_label.pack()

        self.token_entry = tk.Entry(self.root, show="*")
        self.token_entry.pack()

        self.token_button = tk.Button(self.root, text="Set Token", command=self.set_token)
        self.token_button.pack()

        self.model_label = tk.Label(self.root, text="Model:")
        self.model_label.pack()

        self.model_var = tk.StringVar(self.root)
        self.model_dropdown = tk.OptionMenu(self.root, self.model_var, "")
        self.model_dropdown.pack()

        self.model_button = tk.Button(self.root, text="Fetch Models", command=self.fetch_models)
        self.model_button.pack()

        self.token_limit_label = tk.Label(self.root, text="Max Tokens (128000 by default):")
        self.token_limit_label.pack()

        self.token_limit_entry = tk.Entry(self.root)
        self.token_limit_entry.insert(0, "128000")
        self.token_limit_entry.pack()

        self.chat_log = tk.Text(self.root, state='disabled')
        self.chat_log.pack()

        self.message_entry = tk.Entry(self.root)
        self.message_entry.pack()

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack()

    def set_token(self):
        self.token = self.token_entry.get()
        openai.api_key = self.token
        messagebox.showinfo("Info", "Token set successfully!")
    
    def fetch_models(self):
        try:
            models = openai.Model.list()
            self.models = [model['id'] for model in models['data']]
            self.model_var.set(self.models[0])  # Set default model to the first one in the list
            self.update_model_dropdown()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch models: {str(e)}")
    
    def update_model_dropdown(self):
        menu = self.model_dropdown['menu']
        menu.delete(0, 'end')
        for model in self.models:
            menu.add_command(label=model, command=tk._setit(self.model_var, model))
    
    def send_message(self):
        if not self.token:
            messagebox.showerror("Error", "API Token is not set!")
            return

        user_message = self.message_entry.get()
        if not user_message:
            messagebox.showerror("Error", "Message cannot be empty!")
            return

        self.conversation.append({"role": "user", "content": user_message})
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model_var.get(),
                messages=self.conversation,
                max_tokens=int(self.token_limit_entry.get())
            )
            assistant_message = response['choices'][0]['message']['content']
            self.conversation.append({"role": "assistant", "content": assistant_message})
            self.update_chat_log(user_message, assistant_message)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {str(e)}")

    def update_chat_log(self, user_message, assistant_message):
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, f"You: {user_message}\n")
        self.chat_log.insert(tk.END, f"Assistant: {assistant_message}\n")
        self.chat_log.config(state='disabled')
        self.message_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = OpenAIApp(root)
    root.mainloop()
