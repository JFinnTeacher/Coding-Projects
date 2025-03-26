from ui.menu import Menu
from ui.appearance import Appearance
from ui.time_display import TimeDisplay
from utils.config_handler import ConfigHandler
import sys
import tkinter as tk

def main():
    # Load configuration settings
    config_handler = ConfigHandler('config.ini')
    appearance = Appearance(config_handler)
    appearance.apply_settings()

    # Initialize the main application window
    root = tk.Tk()
    root.title("Python Interface Menu")
    
    # Create and display the menu
    menu = Menu(root)
    menu.display()

    # Create and display the time display
    time_display = TimeDisplay(root)
    time_display.update_time()

    # Start the main event loop
    root.protocol("WM_DELETE_WINDOW", sys.exit)
    root.mainloop()

if __name__ == "__main__":
    main()