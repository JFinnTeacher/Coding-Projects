import tkinter as tk
from tkinter import ttk
import json
import os
from pathlib import Path

from sections.config_window import ConfigWindow
from sections.timer import TimerWindow
from sections.name_selector import NameSelectorWindow
from sections.tournament import TournamentWindow

class TeacherAssistant:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Teacher Assistant")
        self.root.geometry("800x600")
        
        # Load configuration
        self.config = self.load_config()
        
        # Apply theme
        self.apply_theme()
        
        # Create main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Create title
        title_label = ttk.Label(
            self.main_frame,
            text="Teacher Assistant",
            font=('Helvetica', 24, 'bold')
        )
        title_label.pack(pady=(0, 40))
        
        # Create menu buttons
        self.create_menu_buttons()
        
        # Create close button
        close_button = tk.Button(
            self.main_frame,
            text="Close Application",
            command=self.root.quit,
            bg=self.config["theme"]["close_button_bg"],
            fg=self.config["theme"]["close_button_fg"],
            activebackground=self.config["theme"]["close_button_active_bg"],
            activeforeground=self.config["theme"]["close_button_fg"],
            font=('Helvetica', 10, 'bold'),
            relief='raised',
            padx=10,
            pady=5
        )
        close_button.pack(pady=20, fill='x')
        
    def load_config(self):
        config_path = Path("config/settings.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {
            "theme": {
                "background": "#000000",
                "foreground": "#FFFFFF",
                "accent": "#0000FF",
                "button_bg": "#1a1a1a",
                "button_fg": "#FFFFFF",
                "button_active_bg": "#0000FF",
                "button_active_fg": "#FFFFFF",
                "close_button_bg": "#8B0000",
                "close_button_fg": "#FFFFFF",
                "close_button_active_bg": "#FF0000"
            },
            "timer": {
                "default_time": 300,
                "sound_file": "sounds/timer_end.wav"
            },
            "name_selector": {
                "default_group_size": 4,
                "min_group_size": 2,
                "max_group_size": 8
            },
            "tournament": {
                "default_teams": 8,
                "min_teams": 2,
                "max_teams": 32
            }
        }
    
    def apply_theme(self):
        style = ttk.Style()
        
        # Configure main frame
        style.configure(
            "TFrame",
            background=self.config["theme"]["background"]
        )
        
        # Configure labels
        style.configure(
            "TLabel",
            background=self.config["theme"]["background"],
            foreground=self.config["theme"]["foreground"]
        )
        
        # Configure notebook (tabs)
        style.configure(
            "TNotebook",
            background=self.config["theme"]["background"],
            foreground=self.config["theme"]["foreground"]
        )
        
        style.configure(
            "TNotebook.Tab",
            background=self.config["theme"]["button_bg"],
            foreground=self.config["theme"]["button_fg"],
            padding=5
        )
        
        style.map("TNotebook.Tab",
            background=[('selected', self.config["theme"]["button_active_bg"])],
            foreground=[('selected', self.config["theme"]["button_active_fg"])]
        )
        
        # Configure entry fields
        style.configure(
            "TEntry",
            fieldbackground=self.config["theme"]["button_bg"],
            foreground=self.config["theme"]["button_fg"]
        )
        
        # Configure label frames
        style.configure(
            "TLabelframe",
            background=self.config["theme"]["background"],
            foreground=self.config["theme"]["foreground"]
        )
        
        style.configure(
            "TLabelframe.Label",
            background=self.config["theme"]["background"],
            foreground=self.config["theme"]["foreground"]
        )
        
        # Configure root window
        self.root.configure(bg=self.config["theme"]["background"])
        
        # Apply theme to all existing widgets
        self.apply_theme_to_widgets(self.root)
    
    def apply_theme_to_widgets(self, widget):
        """Recursively apply theme to all widgets"""
        try:
            if isinstance(widget, tk.Button):
                widget.configure(
                    bg=self.config["theme"]["button_bg"],
                    fg=self.config["theme"]["button_fg"],
                    activebackground=self.config["theme"]["button_active_bg"],
                    activeforeground=self.config["theme"]["button_active_fg"],
                    font=('Helvetica', 10),
                    relief='raised',
                    padx=10,
                    pady=5
                )
            elif isinstance(widget, ttk.Label):
                widget.configure(style="TLabel")
            elif isinstance(widget, ttk.Entry):
                widget.configure(style="TEntry")
            elif isinstance(widget, ttk.Frame):
                widget.configure(style="TFrame")
            elif isinstance(widget, ttk.LabelFrame):
                widget.configure(style="TLabelframe")
            elif isinstance(widget, ttk.Notebook):
                widget.configure(style="TNotebook")
        except:
            pass
            
        # Apply to all children
        for child in widget.winfo_children():
            self.apply_theme_to_widgets(child)
    
    def create_menu_buttons(self):
        buttons = [
            ("Configuration", self.open_config),
            ("Countdown Timer", self.open_timer),
            ("Name Selector", self.open_name_selector),
            ("Tournament Tracker", self.open_tournament)
        ]
        
        for text, command in buttons:
            btn = tk.Button(
                self.main_frame,
                text=text,
                command=command,
                bg=self.config["theme"]["button_bg"],
                fg=self.config["theme"]["button_fg"],
                activebackground=self.config["theme"]["button_active_bg"],
                activeforeground=self.config["theme"]["button_active_fg"],
                font=('Helvetica', 10),
                relief='raised',
                padx=10,
                pady=5
            )
            btn.pack(pady=5, fill='x')
    
    def open_config(self):
        ConfigWindow(self.root, self.config, self.update_config)
    
    def open_timer(self):
        TimerWindow(self.root, self.config)
    
    def open_name_selector(self):
        NameSelectorWindow(self.root, self.config)
    
    def open_tournament(self):
        TournamentWindow(self.root, self.config)
    
    def update_config(self, new_config):
        self.config = new_config
        self.apply_theme()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TeacherAssistant()
    app.run() 