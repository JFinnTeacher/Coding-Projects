import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
import pandas as pd
from pathlib import Path

class NameSelectorWindow:
    def __init__(self, parent, config):
        self.window = tk.Toplevel(parent)
        self.window.title("Name Selector")
        self.window.geometry("600x400")
        self.window.configure(bg=config["theme"]["background"])
        
        self.config = config
        self.names = []
        self.selected_names = set()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main Container
        main_frame = tk.Frame(self.window, bg=self.config["theme"]["background"])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left Frame - Name List
        left_frame = tk.LabelFrame(
            main_frame,
            text="Name List",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        )
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Name List
        self.name_listbox = tk.Listbox(
            left_frame,
            selectmode='extended',
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            selectbackground=self.config["theme"]["button_active_bg"],
            selectforeground=self.config["theme"]["button_active_fg"]
        )
        self.name_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Right Frame - Controls
        right_frame = tk.Frame(main_frame, bg=self.config["theme"]["background"])
        right_frame.pack(side='right', fill='y', padx=5)
        
        # Import Section
        import_frame = tk.LabelFrame(
            right_frame,
            text="Import Names",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        )
        import_frame.pack(fill='x', pady=5)
        
        tk.Button(
            import_frame,
            text="Import from CSV",
            command=self.import_csv,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(fill='x', padx=5, pady=5)
        
        tk.Button(
            import_frame,
            text="Add Manually",
            command=self.add_manual,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(fill='x', padx=5, pady=5)
        
        # Selection Section
        selection_frame = tk.LabelFrame(
            right_frame,
            text="Selection",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        )
        selection_frame.pack(fill='x', pady=5)
        
        tk.Button(
            selection_frame,
            text="Select Random Name",
            command=self.select_random,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(fill='x', padx=5, pady=5)
        
        tk.Button(
            selection_frame,
            text="Clear Selection",
            command=self.clear_selection,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(fill='x', padx=5, pady=5)
        
        # Group Section
        group_frame = tk.LabelFrame(
            right_frame,
            text="Group Assignment",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        )
        group_frame.pack(fill='x', pady=5)
        
        tk.Label(
            group_frame,
            text="Group Size:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(anchor='w', padx=5)
        
        self.group_size = tk.Entry(
            group_frame,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            insertbackground=self.config["theme"]["button_fg"]
        )
        self.group_size.insert(0, str(self.config["name_selector"]["default_group_size"]))
        self.group_size.pack(fill='x', padx=5, pady=5)
        
        tk.Button(
            group_frame,
            text="Create Groups",
            command=self.create_groups,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(fill='x', padx=5, pady=5)
        
        # Selected Names Display
        selected_frame = tk.LabelFrame(
            right_frame,
            text="Selected Names",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        )
        selected_frame.pack(fill='both', expand=True, pady=5)
        
        self.selected_display = tk.Text(
            selected_frame,
            height=5,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            insertbackground=self.config["theme"]["button_fg"]
        )
        self.selected_display.pack(fill='both', expand=True, padx=5, pady=5)
    
    def import_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                df = pd.read_csv(file_path)
                # Assuming first column contains names
                self.names = df.iloc[:, 0].tolist()
                self.update_name_list()
            except Exception as e:
                messagebox.showerror("Error", f"Error importing CSV: {str(e)}")
    
    def add_manual(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("Add Name")
        dialog.geometry("300x100")
        dialog.configure(bg=self.config["theme"]["background"])
        
        tk.Label(
            dialog,
            text="Enter name:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(pady=5)
        
        name_entry = tk.Entry(
            dialog,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            insertbackground=self.config["theme"]["button_fg"]
        )
        name_entry.pack(pady=5)
        
        def add():
            name = name_entry.get().strip()
            if name:
                self.names.append(name)
                self.update_name_list()
                dialog.destroy()
        
        tk.Button(
            dialog,
            text="Add",
            command=add,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(pady=5)
    
    def update_name_list(self):
        self.name_listbox.delete(0, tk.END)
        for name in self.names:
            if name not in self.selected_names:
                self.name_listbox.insert(tk.END, name)
    
    def select_random(self):
        if not self.names:
            messagebox.showwarning("Warning", "No names available")
            return
        
        available_names = [name for name in self.names if name not in self.selected_names]
        if not available_names:
            messagebox.showinfo("Info", "All names have been selected")
            return
        
        selected = random.choice(available_names)
        self.selected_names.add(selected)
        self.update_name_list()
        self.update_selected_display()
    
    def clear_selection(self):
        self.selected_names.clear()
        self.update_name_list()
        self.update_selected_display()
    
    def update_selected_display(self):
        self.selected_display.delete('1.0', tk.END)
        for name in sorted(self.selected_names):
            self.selected_display.insert(tk.END, f"{name}\n")
    
    def create_groups(self):
        try:
            group_size = int(self.group_size.get())
            if group_size < self.config["name_selector"]["min_group_size"]:
                raise ValueError(f"Group size must be at least {self.config['name_selector']['min_group_size']}")
            if group_size > self.config["name_selector"]["max_group_size"]:
                raise ValueError(f"Group size must be at most {self.config['name_selector']['max_group_size']}")
            
            available_names = [name for name in self.names if name not in self.selected_names]
            if not available_names:
                messagebox.showwarning("Warning", "No names available for grouping")
                return
            
            random.shuffle(available_names)
            groups = []
            for i in range(0, len(available_names), group_size):
                groups.append(available_names[i:i + group_size])
            
            # Display groups
            dialog = tk.Toplevel(self.window)
            dialog.title("Groups")
            dialog.geometry("400x300")
            dialog.configure(bg=self.config["theme"]["background"])
            
            text_widget = tk.Text(
                dialog,
                bg=self.config["theme"]["button_bg"],
                fg=self.config["theme"]["button_fg"],
                insertbackground=self.config["theme"]["button_fg"]
            )
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            
            for i, group in enumerate(groups, 1):
                text_widget.insert(tk.END, f"Group {i}:\n")
                for name in group:
                    text_widget.insert(tk.END, f"  {name}\n")
                text_widget.insert(tk.END, "\n")
            
            text_widget.config(state='disabled')
            
        except ValueError as e:
            messagebox.showerror("Error", str(e)) 