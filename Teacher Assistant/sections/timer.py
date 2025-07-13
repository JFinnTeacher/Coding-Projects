import tkinter as tk
from tkinter import ttk
import time
from pathlib import Path
import os

try:
    from playsound import playsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False

class TimerWindow:
    def __init__(self, parent, config):
        self.window = tk.Toplevel(parent)
        self.window.title("Countdown Timer")
        self.window.geometry("400x300")
        self.window.configure(bg=config["theme"]["background"])
        
        self.config = config
        self.time_left = self.config["timer"]["default_time"]
        self.running = False
        self.paused = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.window, bg=self.config["theme"]["background"])
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Time Display
        self.time_display = tk.Label(
            main_frame,
            text=self.format_time(self.time_left),
            font=('Helvetica', 48, 'bold'),
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        )
        self.time_display.pack(pady=20)
        
        # Control Frame
        control_frame = tk.Frame(main_frame, bg=self.config["theme"]["background"])
        control_frame.pack(pady=20)
        
        # Time Input Frame
        input_frame = tk.Frame(main_frame, bg=self.config["theme"]["background"])
        input_frame.pack(pady=10)
        
        tk.Label(
            input_frame,
            text="Minutes:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left', padx=5)
        
        self.minutes = tk.Entry(
            input_frame,
            width=5,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            insertbackground=self.config["theme"]["button_fg"]
        )
        self.minutes.pack(side='left', padx=5)
        
        tk.Label(
            input_frame,
            text="Seconds:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left', padx=5)
        
        self.seconds = tk.Entry(
            input_frame,
            width=5,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            insertbackground=self.config["theme"]["button_fg"]
        )
        self.seconds.pack(side='left', padx=5)
        
        # Set Time Button
        tk.Button(
            input_frame,
            text="Set Time",
            command=self.set_time,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
        
        # Control Buttons
        self.start_button = tk.Button(
            control_frame,
            text="Start",
            command=self.start_timer,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        )
        self.start_button.pack(side='left', padx=5)
        
        self.pause_button = tk.Button(
            control_frame,
            text="Pause",
            command=self.pause_timer,
            state='disabled',
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        )
        self.pause_button.pack(side='left', padx=5)
        
        self.reset_button = tk.Button(
            control_frame,
            text="Reset",
            command=self.reset_timer,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        )
        self.reset_button.pack(side='left', padx=5)
        
        # Sound Status Label
        if not SOUND_AVAILABLE:
            tk.Label(
                main_frame,
                text="Sound playback not available",
                bg=self.config["theme"]["background"],
                fg="#FF0000"  # Red color for warning
            ).pack(pady=5)
        
    def format_time(self, seconds):
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:02d}:{remaining_seconds:02d}"
    
    def set_time(self):
        try:
            mins = int(self.minutes.get() or 0)
            secs = int(self.seconds.get() or 0)
            self.time_left = mins * 60 + secs
            self.time_display.config(text=self.format_time(self.time_left))
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter valid numbers")
    
    def start_timer(self):
        if not self.running:
            self.running = True
            self.paused = False
            self.start_button.config(state='disabled')
            self.pause_button.config(state='normal')
            self.update_timer()
    
    def pause_timer(self):
        if self.running:
            self.paused = not self.paused
            self.pause_button.config(text="Resume" if self.paused else "Pause")
    
    def reset_timer(self):
        self.running = False
        self.paused = False
        self.time_left = self.config["timer"]["default_time"]
        self.time_display.config(text=self.format_time(self.time_left))
        self.start_button.config(state='normal')
        self.pause_button.config(state='disabled')
        self.pause_button.config(text="Pause")
    
    def update_timer(self):
        if self.running and not self.paused:
            if self.time_left > 0:
                self.time_left -= 1
                self.time_display.config(text=self.format_time(self.time_left))
                self.window.after(1000, self.update_timer)
            else:
                self.timer_complete()
    
    def timer_complete(self):
        self.running = False
        self.start_button.config(state='normal')
        self.pause_button.config(state='disabled')
        self.pause_button.config(text="Pause")
        
        # Play sound if available
        if SOUND_AVAILABLE:
            sound_file = Path(self.config["timer"]["sound_file"])
            if sound_file.exists():
                try:
                    playsound(str(sound_file))
                except Exception as e:
                    print(f"Error playing sound: {e}")
        
        tk.messagebox.showinfo("Timer Complete", "Time's up!") 