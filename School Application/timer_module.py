import tkinter as tk
from tkinter import ttk, messagebox
import pygame
import os
from utils import ThemeManager, ModernWindow, ModernFrame, RoundedButton, ModernEntry

class TimerWindow(ModernWindow):
    def __init__(self, parent):
        super().__init__(parent, "Countdown Timer", "600x600")
        self.parent = parent  # Store reference to parent window
        
        # Initialize pygame for sound
        pygame.mixer.init()
        
        # Variables
        self.time_remaining = 0
        self.timer_running = False
        self.default_minutes = 5
        
        self.create_widgets()
    
    def create_widgets(self):
        # Time input frame
        input_frame = ModernFrame(self.content)
        input_frame.pack(pady=20)
        
        tk.Label(
            input_frame,
            text="Minutes:",
            font=("Helvetica", 12),
            bg=self.theme['bg_color'],
            fg=self.theme['text_color']
        ).pack(side=tk.LEFT, padx=5)
        
        self.minutes_var = tk.StringVar(value=str(self.default_minutes))
        self.minutes_entry = ModernEntry(
            input_frame,
            textvariable=self.minutes_var,
            width=8
        )
        self.minutes_entry.pack(side=tk.LEFT, padx=5)
        
        # Timer display
        display_frame = ModernFrame(self.content)
        display_frame.pack(pady=20)
        
        self.timer_label = tk.Label(
            display_frame,
            text="00:00",
            font=("Helvetica", 48, "bold"),
            bg=self.theme['bg_color'],
            fg=self.theme['text_color']
        )
        self.timer_label.pack(pady=20)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.content,
            style="Modern.Horizontal.TProgressbar",
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(pady=20)
        
        # Buttons frame
        button_frame = ModernFrame(self.content)
        button_frame.pack(pady=20)
        
        self.start_button = RoundedButton(
            button_frame,
            text="Start",
            command=self.start_timer,
            width=120,
            height=40
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        RoundedButton(
            button_frame,
            text="Reset",
            command=self.reset_timer,
            width=120,
            height=40
        ).pack(side=tk.LEFT, padx=5)
        
        RoundedButton(
            button_frame,
            text="Back",
            command=self.close_window,
            width=120,
            height=40
        ).pack(side=tk.LEFT, padx=5)
    
    def start_timer(self):
        if not self.timer_running:
            try:
                minutes = float(self.minutes_var.get())
                if minutes <= 0:
                    raise ValueError
                self.time_remaining = int(minutes * 60)
                self.total_time = self.time_remaining
                self.timer_running = True
                self.start_button.set_text("Pause")
                self.update_timer()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number of minutes")
        else:
            self.timer_running = False
            self.start_button.set_text("Resume")
    
    def update_timer(self):
        if self.timer_running and self.time_remaining > 0:
            minutes = self.time_remaining // 60
            seconds = self.time_remaining % 60
            self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            
            # Update progress bar
            progress = ((self.total_time - self.time_remaining) / self.total_time) * 100
            self.progress_bar['value'] = progress
            
            self.time_remaining -= 1
            self.after(1000, self.update_timer)
        elif self.timer_running:
            self.timer_running = False
            self.start_button.set_text("Start")
            self.timer_label.config(text="00:00")
            self.progress_bar['value'] = 100
            
            # Play end sound
            try:
                sound_file = os.path.join(os.path.dirname(__file__), 'timer_end.wav')
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
            except:
                messagebox.showwarning("Warning", "Could not play sound file")
    
    def reset_timer(self):
        self.timer_running = False
        self.start_button.set_text("Start")
        self.timer_label.config(text="00:00")
        self.progress_bar['value'] = 0
        self.minutes_var.set(str(self.default_minutes))
    
    def close_window(self):
        self.destroy()
        self.parent.lift()  # Bring main window to front
        self.parent.focus_force()  # Give focus to main window 