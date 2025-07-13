import tkinter as tk
from tkinter import messagebox
import random
import pandas as pd
import os
from utils import ThemeManager, ModernWindow, ModernFrame, RoundedButton, ModernEntry

class NamePickerWindow(ModernWindow):
    def __init__(self, parent):
        super().__init__(parent, "Name Picker", "600x600")
        self.parent = parent  # Store reference to parent window
        self.names = []
        self.create_widgets()
    
    def create_widgets(self):
        # Input frame
        input_frame = ModernFrame(self.content)
        input_frame.pack(pady=20)
        
        tk.Label(
            input_frame,
            text="Enter Name:",
            font=("Helvetica", 12),
            bg=self.theme['bg_color'],
            fg=self.theme['text_color']
        ).pack(side=tk.LEFT, padx=5)
        
        self.name_entry = ModernEntry(input_frame)
        self.name_entry.pack(side=tk.LEFT, padx=5)
        
        RoundedButton(
            input_frame,
            text="Add Name",
            command=self.add_name,
            width=100,
            height=30
        ).pack(side=tk.LEFT, padx=5)
        
        # Names list frame
        list_frame = ModernFrame(self.content)
        list_frame.pack(pady=20, fill='both', expand=True)
        
        tk.Label(
            list_frame,
            text="Names List",
            font=("Helvetica", 14, "bold"),
            bg=self.theme['bg_color'],
            fg=self.theme['text_color']
        ).pack(pady=(0, 10))
        
        # Create listbox with scrollbar
        listbox_frame = ModernFrame(list_frame)
        listbox_frame.pack(fill='both', expand=True)
        
        self.names_listbox = tk.Listbox(
            listbox_frame,
            font=("Helvetica", 12),
            bg=self.theme['input_bg'],
            fg=self.theme['text_color'],
            selectmode=tk.SINGLE,
            relief='flat',
            highlightthickness=0
        )
        self.names_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        # Connect scrollbar to listbox
        self.names_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.names_listbox.yview)
        
        # Result label
        self.result_label = tk.Label(
            self.content,
            text="",
            font=("Helvetica", 16, "bold"),
            bg=self.theme['bg_color'],
            fg=self.theme['accent_color']
        )
        self.result_label.pack(pady=20)
        
        # CSV buttons frame
        csv_frame = ModernFrame(self.content)
        csv_frame.pack(pady=(0, 10))
        
        RoundedButton(
            csv_frame,
            text="Generate Template",
            command=self.generate_template,
            width=150,  # Increased width
            height=30
        ).pack(side=tk.LEFT, padx=5)
        
        RoundedButton(
            csv_frame,
            text="Import CSV",
            command=self.import_csv,
            width=120,
            height=30
        ).pack(side=tk.LEFT, padx=5)
        
        # Main buttons frame
        button_frame = ModernFrame(self.content)
        button_frame.pack(pady=10)
        
        RoundedButton(
            button_frame,
            text="Pick Random",
            command=self.pick_random,
            width=120,
            height=40
        ).pack(side=tk.LEFT, padx=5)
        
        RoundedButton(
            button_frame,
            text="Clear All",
            command=self.clear_names,
            width=120,
            height=40
        ).pack(side=tk.LEFT, padx=5)
        
        RoundedButton(
            button_frame,
            text="Back",
            command=self.close_window,  # Changed to use new close method
            width=120,
            height=40
        ).pack(side=tk.LEFT, padx=5)
    
    def close_window(self):
        self.destroy()
        self.parent.lift()  # Bring main window to front
        self.parent.focus_force()  # Give focus to main window
    
    def add_name(self):
        name = self.name_entry.get().strip()
        if name:
            if name not in self.names:
                self.names.append(name)
                self.names_listbox.insert(tk.END, name)
                self.name_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Warning", "Name already exists")
        else:
            messagebox.showwarning("Warning", "Please enter a name")
    
    def pick_random(self):
        if self.names:
            chosen_name = random.choice(self.names)
            self.result_label.config(text=f"Selected: {chosen_name}")
        else:
            messagebox.showwarning("Warning", "No names to pick from")
    
    def clear_names(self):
        self.names = []
        self.names_listbox.delete(0, tk.END)
        self.result_label.config(text="")
    
    def generate_template(self):
        try:
            csv_file = os.path.join(os.path.dirname(__file__), 'names.csv')
            # Create a template with example names
            example_names = ['Student 1', 'Student 2', 'Student 3']
            df = pd.DataFrame({'Name': example_names})
            df.to_csv(csv_file, index=False)
            messagebox.showinfo("Success", f"Template created at: {csv_file}\nEdit the file and use Import CSV to load your names.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create template: {str(e)}")
    
    def import_csv(self):
        try:
            csv_file = os.path.join(os.path.dirname(__file__), 'names.csv')
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)
                if 'Name' in df.columns:
                    new_names = df['Name'].tolist()
                    self.names.extend(new_names)
                    for name in new_names:
                        self.names_listbox.insert(tk.END, name)
                    messagebox.showinfo("Success", f"Imported {len(new_names)} names")
                else:
                    messagebox.showerror("Error", "CSV file must have a 'Name' column")
            else:
                messagebox.showerror("Error", "names.csv not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV: {str(e)}") 