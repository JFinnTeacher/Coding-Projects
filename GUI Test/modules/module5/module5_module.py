import tkinter as tk
from tkinter import ttk
from ..common_styles import apply_module_style
from config.settings import WINDOW, GRID, MODULES

class Module5Window:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title(MODULES['module5']['title'])
        
        # Apply common styles
        apply_module_style(self.window, 'module5')
        
        # Create main frame
        main_frame = ttk.Frame(
            self.window,
            padding=WINDOW['module']['padding'],
            style='Main.TFrame'
        )
        main_frame.grid(sticky="nsew", **GRID['padding'])
        
        # Add placeholder content
        ttk.Label(main_frame, text="Module 5 Content", style='Title.TLabel').grid(pady=20)
        ttk.Label(main_frame, text="This is a placeholder for Module 5", style='Regular.TLabel').grid(pady=10)

def open_window(parent):
    Module5Window(parent) 