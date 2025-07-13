import tkinter as tk
from timer_module import TimerWindow
from name_picker_module import NamePickerWindow
from tournament_module import TournamentWindow
from utils import ThemeManager, ModernWindow, ModernFrame, RoundedButton

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.theme = ThemeManager.load_theme()
        
        # Configure window
        self.title("School Application")
        self.geometry("800x600")
        self.configure(bg=self.theme['bg_color'])
        
        # Create main container
        self.container = ModernFrame(self)
        self.container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Create header
        self.create_header()
        
        # Create content area
        self.content = ModernFrame(self.container)
        self.content.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Create main menu buttons
        self.create_menu_buttons()
    
    def create_header(self):
        header = ModernFrame(self.container)
        header.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            header,
            text="School Application",
            font=("Helvetica", 24, "bold"),
            bg=self.theme['bg_color'],
            fg=self.theme['accent_color']
        ).pack(pady=10)
    
    def create_menu_buttons(self):
        # Timer button
        RoundedButton(
            self.content,
            text="Countdown Timer",
            command=self.open_timer,
            width=200,
            height=40
        ).pack(pady=10)
        
        # Name picker button
        RoundedButton(
            self.content,
            text="Name Picker",
            command=self.open_name_picker,
            width=200,
            height=40
        ).pack(pady=10)
        
        # Tournament tracker button
        RoundedButton(
            self.content,
            text="Tournament Tracker",
            command=self.open_tournament,
            width=200,
            height=40
        ).pack(pady=10)
        
        # Exit button
        RoundedButton(
            self.content,
            text="Exit",
            command=self.quit,
            width=200,
            height=40
        ).pack(pady=10)
    
    def open_timer(self):
        TimerWindow(self)
    
    def open_name_picker(self):
        NamePickerWindow(self)
    
    def open_tournament(self):
        TournamentWindow(self)

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop() 