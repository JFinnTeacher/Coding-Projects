import tkinter as tk
from tkinter import ttk, messagebox
import time
import winsound
import threading
from ..common_styles import apply_module_style
from config.settings import COLORS, WINDOW, GRID, MODULES, SOUNDS

class TimerWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title(MODULES['timer']['title'])
        
        # Apply common styles
        apply_module_style(self.window, 'timer')
        
        # Timer variables
        self.remaining_time = 0
        self.timer_running = False
        self.timer_thread = None
        
        # Configure window grid
        self.window.columnconfigure(0, weight=1)
        
        # Create main frame
        main_frame = ttk.Frame(
            self.window,
            padding=WINDOW['module']['padding'],
            style='Main.TFrame'
        )
        main_frame.grid(sticky="nsew", **GRID['padding'])
        
        # Time input frame
        input_frame = ttk.LabelFrame(main_frame, text="Set Timer", padding="10")
        input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Time inputs
        self.minutes_var = tk.StringVar(value="0")
        self.seconds_var = tk.StringVar(value="0")
        
        minutes_frame = ttk.Frame(input_frame, style='Main.TFrame')
        minutes_frame.grid(row=0, column=0, padx=5)
        
        ttk.Label(minutes_frame, text="Minutes:", style='Regular.TLabel').grid(row=0, column=0)
        ttk.Entry(minutes_frame, textvariable=self.minutes_var, width=5, style='TEntry').grid(row=1, column=0)
        
        seconds_frame = ttk.Frame(input_frame, style='Main.TFrame')
        seconds_frame.grid(row=0, column=1, padx=5)
        
        ttk.Label(seconds_frame, text="Seconds:", style='Regular.TLabel').grid(row=0, column=0)
        ttk.Entry(seconds_frame, textvariable=self.seconds_var, width=5, style='TEntry').grid(row=1, column=0)
        
        # Timer display
        self.time_display = ttk.Label(main_frame, text="00:00", style='Large.TLabel')
        self.time_display.grid(row=1, column=0, pady=20)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame, style='Main.TFrame')
        button_frame.grid(row=2, column=0, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_timer)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_timer, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=5)
        
        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_timer)
        self.reset_button.grid(row=0, column=2, padx=5)
        
    def update_display(self):
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.time_display.config(text=f"{minutes:02d}:{seconds:02d}")
        
    def start_timer(self):
        try:
            minutes = int(self.minutes_var.get())
            seconds = int(self.seconds_var.get())
            
            if minutes < 0 or seconds < 0 or seconds >= 60:
                raise ValueError
                
            self.remaining_time = minutes * 60 + seconds
            if self.remaining_time == 0:
                raise ValueError
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid time values")
            return
            
        self.timer_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        def timer_thread():
            while self.timer_running and self.remaining_time > 0:
                self.remaining_time -= 1
                self.window.after(0, self.update_display)
                time.sleep(1)
                
            if self.timer_running:  # Timer completed naturally
                self.timer_running = False
                self.window.after(0, self.timer_completed)
                
        self.timer_thread = threading.Thread(target=timer_thread)
        self.timer_thread.daemon = True
        self.timer_thread.start()
        
    def stop_timer(self):
        self.timer_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
    def reset_timer(self):
        self.timer_running = False
        self.remaining_time = 0
        self.minutes_var.set("0")
        self.seconds_var.set("0")
        self.update_display()
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
    def timer_completed(self):
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        messagebox.showinfo("Timer", "Time's up!")
        winsound.Beep(
            SOUNDS['timer_complete']['frequency'],
            SOUNDS['timer_complete']['duration']
        )

def open_window(parent):
    TimerWindow(parent) 