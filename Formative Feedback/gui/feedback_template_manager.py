import tkinter as tk
from tkinter import ttk
import json
import os

class FeedbackTemplateManager(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Feedback Template Manager")
        self.geometry("500x350")
        self.resizable(False, False)
        self.setup_ui()
        self.load_templates()

    def setup_ui(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.template_listbox = tk.Listbox(main_frame, width=25)
        self.template_listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.template_listbox.bind('<<ListboxSelect>>', self.display_template)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.details_text = tk.Text(right_frame, height=15, width=40, state=tk.DISABLED)
        self.details_text.pack(fill=tk.BOTH, expand=True)

        close_btn = ttk.Button(self, text="Close", command=self.destroy)
        close_btn.pack(side=tk.BOTTOM, pady=10)

    def load_templates(self):
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'feedback_templates.json')
        self.data_path = data_path
        try:
            with open(data_path, 'r') as f:
                self.templates = json.load(f)
        except Exception:
            self.templates = []
        self.template_listbox.delete(0, tk.END)
        for idx, template in enumerate(self.templates):
            name = template.get('name', f'Template {idx+1}')
            self.template_listbox.insert(tk.END, name)

    def display_template(self, event=None):
        selection = self.template_listbox.curselection()
        if not selection:
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete('1.0', tk.END)
            self.details_text.config(state=tk.DISABLED)
            return
        idx = selection[0]
        template = self.templates[idx]
        details = json.dumps(template, indent=2)
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete('1.0', tk.END)
        self.details_text.insert(tk.END, details)
        self.details_text.config(state=tk.DISABLED) 