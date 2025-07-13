import tkinter as tk
from tkinter import ttk
import sys
import os
from datetime import datetime

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from config.settings import (
    WINDOW, COLORS, FONTS, TIME_FORMATS,
    BUTTONS, GRID, MODULES
)

class ClassroomAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW['main']['title'])
        
        # Set window size and position it in center
        window_width = WINDOW['main']['width']
        window_height = WINDOW['main']['height']
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Configure root grid and background
        self.root.configure(bg=COLORS['primary'])
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        
        # Create main frame
        main_frame = ttk.Frame(
            root,
            padding=WINDOW['main']['padding'],
            style='Main.TFrame'
        )
        main_frame.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="nsew",
            **GRID['padding']
        )
        
        # Title Label
        title_label = ttk.Label(
            main_frame, 
            text=WINDOW['main']['title'],
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Clock Frame
        clock_frame = ttk.Frame(main_frame, style='Main.TFrame')
        clock_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Digital Clock
        self.time_label = ttk.Label(
            clock_frame,
            style='Clock.TLabel'
        )
        self.time_label.grid(row=0, column=0, pady=5)
        
        self.date_label = ttk.Label(
            clock_frame,
            font=FONTS['date'],
            style='Regular.TLabel'
        )
        self.date_label.grid(row=1, column=0)
        
        # Start clock update
        self.update_clock()
        
        # Create and position buttons
        self.create_button(main_frame, "Random Student", self.open_random_student, 2, 0)
        self.create_button(main_frame, "Tournament Generator", self.open_tournament_generator, 3, 0)
        self.create_button(main_frame, "Timer", self.open_timer, 4, 0)
        self.create_button(main_frame, "Module 4", self.open_module4, 2, 1)
        self.create_button(main_frame, "Module 5", self.open_module5, 3, 1)
        self.create_button(main_frame, "Module 6", self.open_module6, 4, 1)
        
        # Exit button
        exit_button = ttk.Button(
            main_frame,
            text="Exit",
            command=self.root.quit,
            style='Exit.TButton'
        )
        exit_button.grid(row=5, column=0, columnspan=2, pady=20, sticky="ew")
        
        # Configure styles
        self.configure_styles()
        
    def update_clock(self):
        current_time = datetime.now()
        time_string = current_time.strftime(TIME_FORMATS['clock'])
        date_string = current_time.strftime(TIME_FORMATS['date'])
        
        self.time_label.config(text=time_string)
        self.date_label.config(text=date_string)
        self.root.after(1000, self.update_clock)
        
    def configure_styles(self):
        style = ttk.Style()
        
        # Configure frame style
        style.configure('Main.TFrame', background=COLORS['secondary'])
        
        # Configure label style
        style.configure('Title.TLabel',
                       background=COLORS['secondary'],
                       foreground=COLORS['text'])
        
        # Configure regular button style
        style.configure('TButton',
                       padding=BUTTONS['padding'],
                       width=BUTTONS['width'],
                       font=FONTS['button'],
                       background=COLORS['button'])
        
        style.map('TButton',
                  background=[('active', COLORS['button_hover'])])
        
        # Configure exit button style
        style.configure('Exit.TButton',
                       padding=BUTTONS['padding'],
                       width=BUTTONS['width'],
                       background=COLORS['exit_bg'],
                       font=FONTS['button'])
        
        style.map('Exit.TButton',
                  background=[('active', COLORS['exit_hover'])])
        
    def create_button(self, parent, text, command, row, column):
        button = ttk.Button(parent, text=text, command=command)
        button.grid(
            row=row,
            column=column,
            **BUTTONS['spacing']
        )
        
    def open_random_student(self):
        from modules.random_student import random_student_module
        random_student_module.open_window(self.root)
        
    def open_tournament_generator(self):
        from modules.tournament_generator import tournament_generator_module
        tournament_generator_module.open_window(self.root)
        
    def open_timer(self):
        from modules.timer import timer_module
        timer_module.open_window(self.root)
        
    def open_module4(self):
        from modules.module4 import module4_module
        module4_module.open_window(self.root)
        
    def open_module5(self):
        from modules.module5 import module5_module
        module5_module.open_window(self.root)
        
    def open_module6(self):
        from modules.module6 import module6_module
        module6_module.open_window(self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClassroomAssistant(root)
    root.mainloop()
