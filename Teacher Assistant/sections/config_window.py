import tkinter as tk
from tkinter import ttk, colorchooser
import json
from pathlib import Path

class ConfigWindow:
    def __init__(self, parent, config, on_save):
        self.window = tk.Toplevel(parent)
        self.window.title("Configuration")
        self.window.geometry("800x700")
        self.window.resizable(True, True)
        
        # Store configuration and callback
        self.config = config
        self.on_save = on_save
        self.unsaved_changes = False
        
        # Create main container with padding
        self.main_container = tk.Frame(self.window, bg=self.config["theme"]["background"])
        self.main_container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Create tab buttons frame
        self.tab_buttons = tk.Frame(self.main_container, bg=self.config["theme"]["background"])
        self.tab_buttons.pack(fill='x', padx=5, pady=5)
        
        # Create content frame
        self.content_frame = tk.Frame(self.main_container, bg=self.config["theme"]["background"])
        self.content_frame.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Create tabs
        self.tabs = {
            "Theme": tk.Frame(self.content_frame, bg=self.config["theme"]["background"]),
            "Timer": tk.Frame(self.content_frame, bg=self.config["theme"]["background"]),
            "Name Selector": tk.Frame(self.content_frame, bg=self.config["theme"]["background"]),
            "Tournament": tk.Frame(self.content_frame, bg=self.config["theme"]["background"])
        }
        
        # Create tab buttons
        self.current_tab = None
        self.tab_buttons_dict = {}
        for i, (name, frame) in enumerate(self.tabs.items()):
            btn = tk.Button(
                self.tab_buttons,
                text=name,
                command=lambda f=frame, n=name: self.show_tab(f, n),
                bg=self.config["theme"]["button_bg"],
                fg=self.config["theme"]["button_fg"],
                activebackground=self.config["theme"]["button_active_bg"],
                activeforeground=self.config["theme"]["button_active_fg"],
                font=('Helvetica', 10),
                relief='raised',
                padx=15,
                pady=5
            )
            btn.pack(side='left', padx=2)
            self.tab_buttons_dict[name] = btn
        
        # Show first tab by default
        self.show_tab(self.tabs["Theme"], "Theme")
        
        # Create content for each tab
        self.create_theme_tab()
        self.create_timer_tab()
        self.create_name_selector_tab()
        self.create_tournament_tab()
        
        # Create button frame at the bottom
        self.create_button_frame()
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def show_tab(self, tab_frame, tab_name):
        # Hide current tab
        if self.current_tab:
            self.current_tab.pack_forget()
            self.tab_buttons_dict[self.current_tab_name].configure(
                bg=self.config["theme"]["button_bg"],
                fg=self.config["theme"]["button_fg"]
            )
        
        # Show selected tab
        tab_frame.pack(expand=True, fill='both')
        self.current_tab = tab_frame
        self.current_tab_name = tab_name
        
        # Update button appearance
        self.tab_buttons_dict[tab_name].configure(
            bg=self.config["theme"]["button_active_bg"],
            fg=self.config["theme"]["button_active_fg"]
        )
    
    def create_theme_tab(self):
        # Create preview frame
        preview_frame = tk.LabelFrame(
            self.tabs["Theme"],
            text="Preview",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        )
        preview_frame.pack(fill='x', padx=10, pady=10)
        
        # Add preview elements
        preview_label = tk.Label(
            preview_frame,
            text="Sample Text",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        )
        preview_label.pack(pady=10)
        
        preview_button = tk.Button(
            preview_frame,
            text="Sample Button",
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        )
        preview_button.pack(pady=5)
        
        # Color selection buttons
        colors_frame = tk.Frame(self.tabs["Theme"], bg=self.config["theme"]["background"])
        colors_frame.pack(fill='x', padx=10, pady=10)
        
        # Background color
        bg_frame = tk.Frame(colors_frame, bg=self.config["theme"]["background"])
        bg_frame.pack(fill='x', pady=5)
        tk.Label(
            bg_frame,
            text="Background Color:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left')
        tk.Button(
            bg_frame,
            text="Select",
            command=lambda: self.select_color("background"),
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right')
        
        # Text color
        fg_frame = tk.Frame(colors_frame, bg=self.config["theme"]["background"])
        fg_frame.pack(fill='x', pady=5)
        tk.Label(
            fg_frame,
            text="Text Color:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left')
        tk.Button(
            fg_frame,
            text="Select",
            command=lambda: self.select_color("foreground"),
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right')
        
        # Accent color
        accent_frame = tk.Frame(colors_frame, bg=self.config["theme"]["background"])
        accent_frame.pack(fill='x', pady=5)
        tk.Label(
            accent_frame,
            text="Accent Color:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left')
        tk.Button(
            accent_frame,
            text="Select",
            command=lambda: self.select_color("accent"),
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right')
        
        # Button background color
        button_bg_frame = tk.Frame(colors_frame, bg=self.config["theme"]["background"])
        button_bg_frame.pack(fill='x', pady=5)
        tk.Label(
            button_bg_frame,
            text="Button Background:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left')
        tk.Button(
            button_bg_frame,
            text="Select",
            command=lambda: self.select_color("button_bg"),
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right')
        
        # Button text color
        button_fg_frame = tk.Frame(colors_frame, bg=self.config["theme"]["background"])
        button_fg_frame.pack(fill='x', pady=5)
        tk.Label(
            button_fg_frame,
            text="Button Text Color:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left')
        tk.Button(
            button_fg_frame,
            text="Select",
            command=lambda: self.select_color("button_fg"),
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right')
        
        # Button active background color
        button_active_bg_frame = tk.Frame(colors_frame, bg=self.config["theme"]["background"])
        button_active_bg_frame.pack(fill='x', pady=5)
        tk.Label(
            button_active_bg_frame,
            text="Button Active Background:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left')
        tk.Button(
            button_active_bg_frame,
            text="Select",
            command=lambda: self.select_color("button_active_bg"),
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right')
        
        # Button active text color
        button_active_fg_frame = tk.Frame(colors_frame, bg=self.config["theme"]["background"])
        button_active_fg_frame.pack(fill='x', pady=5)
        tk.Label(
            button_active_fg_frame,
            text="Button Active Text Color:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left')
        tk.Button(
            button_active_fg_frame,
            text="Select",
            command=lambda: self.select_color("button_active_fg"),
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right')
        
        # Close button colors
        close_button_frame = tk.LabelFrame(
            self.tabs["Theme"],
            text="Close Button Colors",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        )
        close_button_frame.pack(fill='x', padx=10, pady=10)
        
        # Close button background color
        close_bg_frame = tk.Frame(close_button_frame, bg=self.config["theme"]["background"])
        close_bg_frame.pack(fill='x', pady=5)
        tk.Label(
            close_bg_frame,
            text="Close Button Background:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left')
        tk.Button(
            close_bg_frame,
            text="Select",
            command=lambda: self.select_color("close_button_bg"),
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right')
        
        # Close button text color
        close_fg_frame = tk.Frame(close_button_frame, bg=self.config["theme"]["background"])
        close_fg_frame.pack(fill='x', pady=5)
        tk.Label(
            close_fg_frame,
            text="Close Button Text Color:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left')
        tk.Button(
            close_fg_frame,
            text="Select",
            command=lambda: self.select_color("close_button_fg"),
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right')
        
        # Close button active background color
        close_active_bg_frame = tk.Frame(close_button_frame, bg=self.config["theme"]["background"])
        close_active_bg_frame.pack(fill='x', pady=5)
        tk.Label(
            close_active_bg_frame,
            text="Close Button Active Background:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left')
        tk.Button(
            close_active_bg_frame,
            text="Select",
            command=lambda: self.select_color("close_button_active_bg"),
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right')
    
    def create_timer_tab(self):
        # Default time setting
        time_frame = tk.LabelFrame(
            self.tabs["Timer"],
            text="Timer Settings",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        )
        time_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            time_frame,
            text="Default Time (seconds):",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(pady=5)
        
        self.default_time = tk.Entry(
            time_frame,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            insertbackground=self.config["theme"]["button_fg"]
        )
        self.default_time.insert(0, str(self.config["timer"]["default_time"]))
        self.default_time.pack(pady=5)
    
    def create_name_selector_tab(self):
        # Group size settings
        group_frame = tk.LabelFrame(
            self.tabs["Name Selector"],
            text="Group Size Settings",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        )
        group_frame.pack(fill='x', padx=10, pady=10)
        
        # Default group size
        default_frame = tk.Frame(group_frame, bg=self.config["theme"]["background"])
        default_frame.pack(fill='x', pady=5)
        tk.Label(
            default_frame,
            text="Default Group Size:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left')
        self.default_group_size = tk.Entry(
            default_frame,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            insertbackground=self.config["theme"]["button_fg"]
        )
        self.default_group_size.insert(0, str(self.config["name_selector"]["default_group_size"]))
        self.default_group_size.pack(side='right')
        
        # Min group size
        min_frame = tk.Frame(group_frame, bg=self.config["theme"]["background"])
        min_frame.pack(fill='x', pady=5)
        tk.Label(
            min_frame,
            text="Minimum Group Size:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left')
        self.min_group_size = tk.Entry(
            min_frame,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            insertbackground=self.config["theme"]["button_fg"]
        )
        self.min_group_size.insert(0, str(self.config["name_selector"]["min_group_size"]))
        self.min_group_size.pack(side='right')
        
        # Max group size
        max_frame = tk.Frame(group_frame, bg=self.config["theme"]["background"])
        max_frame.pack(fill='x', pady=5)
        tk.Label(
            max_frame,
            text="Maximum Group Size:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left')
        self.max_group_size = tk.Entry(
            max_frame,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            insertbackground=self.config["theme"]["button_fg"]
        )
        self.max_group_size.insert(0, str(self.config["name_selector"]["max_group_size"]))
        self.max_group_size.pack(side='right')
    
    def create_tournament_tab(self):
        # Tournament settings
        tournament_frame = tk.LabelFrame(
            self.tabs["Tournament"],
            text="Tournament Settings",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        )
        tournament_frame.pack(fill='x', padx=10, pady=10)
        
        # Default teams
        teams_frame = tk.Frame(tournament_frame, bg=self.config["theme"]["background"])
        teams_frame.pack(fill='x', pady=5)
        tk.Label(
            teams_frame,
            text="Default Number of Teams:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left')
        self.default_teams = tk.Entry(
            teams_frame,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            insertbackground=self.config["theme"]["button_fg"]
        )
        self.default_teams.insert(0, str(self.config["tournament"]["default_teams"]))
        self.default_teams.pack(side='right')
        
        # Min teams
        min_frame = tk.Frame(tournament_frame, bg=self.config["theme"]["background"])
        min_frame.pack(fill='x', pady=5)
        tk.Label(
            min_frame,
            text="Minimum Number of Teams:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left')
        self.min_teams = tk.Entry(
            min_frame,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            insertbackground=self.config["theme"]["button_fg"]
        )
        self.min_teams.insert(0, str(self.config["tournament"]["min_teams"]))
        self.min_teams.pack(side='right')
        
        # Max teams
        max_frame = tk.Frame(tournament_frame, bg=self.config["theme"]["background"])
        max_frame.pack(fill='x', pady=5)
        tk.Label(
            max_frame,
            text="Maximum Number of Teams:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left')
        self.max_teams = tk.Entry(
            max_frame,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            insertbackground=self.config["theme"]["button_fg"]
        )
        self.max_teams.insert(0, str(self.config["tournament"]["max_teams"]))
        self.max_teams.pack(side='right')
    
    def create_button_frame(self):
        # Create container for buttons
        button_container = tk.Frame(self.window, bg=self.config["theme"]["background"])
        button_container.pack(side='bottom', fill='x', padx=20, pady=10)
        
        # Create buttons
        apply_button = tk.Button(
            button_container,
            text="Apply",
            command=self.apply_changes,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5,
            width=10
        )
        apply_button.pack(side='left', padx=5)
        
        save_button = tk.Button(
            button_container,
            text="Save",
            command=self.save_config,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5,
            width=10
        )
        save_button.pack(side='left', padx=5)
        
        close_button = tk.Button(
            button_container,
            text="Close",
            command=self.window.destroy,
            bg=self.config["theme"]["close_button_bg"],
            fg=self.config["theme"]["close_button_fg"],
            activebackground=self.config["theme"]["close_button_active_bg"],
            activeforeground=self.config["theme"]["close_button_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5,
            width=10
        )
        close_button.pack(side='left', padx=5)
    
    def select_color(self, color_key):
        color = colorchooser.askcolor(
            title=f"Select {color_key.replace('_', ' ').title()}",
            color=self.config["theme"][color_key]
        )[1]
        if color:
            self.config["theme"][color_key] = color
            self.unsaved_changes = True
            self.apply_preview_theme()
    
    def apply_preview_theme(self):
        # Update preview elements
        for widget in self.tabs["Theme"].winfo_children():
            if isinstance(widget, tk.LabelFrame):
                widget.configure(
                    bg=self.config["theme"]["background"],
                    fg=self.config["theme"]["foreground"]
                )
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(
                            bg=self.config["theme"]["background"],
                            fg=self.config["theme"]["foreground"]
                        )
                    elif isinstance(child, tk.Button):
                        child.configure(
                            bg=self.config["theme"]["button_bg"],
                            fg=self.config["theme"]["button_fg"],
                            activebackground=self.config["theme"]["button_active_bg"],
                            activeforeground=self.config["theme"]["button_active_fg"]
                        )
        
        # Update tab buttons
        for btn in self.tab_buttons_dict.values():
            if btn["text"] == self.current_tab_name:
                btn.configure(
                    bg=self.config["theme"]["button_active_bg"],
                    fg=self.config["theme"]["button_active_fg"]
                )
            else:
                btn.configure(
                    bg=self.config["theme"]["button_bg"],
                    fg=self.config["theme"]["button_fg"],
                    activebackground=self.config["theme"]["button_active_bg"],
                    activeforeground=self.config["theme"]["button_active_fg"]
                )
    
    def apply_changes(self):
        try:
            # Update timer settings
            self.config["timer"]["default_time"] = int(self.default_time.get())
            
            # Update name selector settings
            self.config["name_selector"]["default_group_size"] = int(self.default_group_size.get())
            self.config["name_selector"]["min_group_size"] = int(self.min_group_size.get())
            self.config["name_selector"]["max_group_size"] = int(self.max_group_size.get())
            
            # Update tournament settings
            self.config["tournament"]["default_teams"] = int(self.default_teams.get())
            self.config["tournament"]["min_teams"] = int(self.min_teams.get())
            self.config["tournament"]["max_teams"] = int(self.max_teams.get())
            
            # Apply changes to main window
            self.on_save(self.config)
            
        except ValueError:
            tk.messagebox.showerror(
                "Error",
                "Please enter valid numbers for all settings."
            )
    
    def save_config(self):
        try:
            # Validate and update settings
            self.apply_changes()
            
            # Save to file
            config_path = Path("config/settings.json")
            config_path.parent.mkdir(exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            self.unsaved_changes = False
            tk.messagebox.showinfo("Success", "Configuration saved successfully!")
            
        except ValueError:
            tk.messagebox.showerror(
                "Error",
                "Please enter valid numbers for all settings."
            )
    
    def on_closing(self):
        if self.unsaved_changes:
            if tk.messagebox.askyesno(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?"
            ):
                self.save_config()
        self.window.destroy() 