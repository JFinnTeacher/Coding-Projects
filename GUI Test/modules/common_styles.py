from tkinter import ttk
from config.settings import COLORS, FONTS, BUTTONS, WINDOW

def configure_styles():
    style = ttk.Style()
    
    # Configure frame styles
    style.configure('Main.TFrame',
                   background=COLORS['secondary'])
    
    style.configure('Secondary.TFrame',
                   background=COLORS['primary'])
    
    # Configure label styles
    style.configure('Title.TLabel',
                   background=COLORS['secondary'],
                   foreground=COLORS['text'],
                   font=FONTS['title'])
    
    style.configure('Regular.TLabel',
                   background=COLORS['secondary'],
                   foreground=COLORS['text'],
                   font=FONTS['text'])
    
    style.configure('Large.TLabel',
                   background=COLORS['secondary'],
                   foreground=COLORS['text'],
                   font=FONTS['large'])
    
    style.configure('Clock.TLabel',
                   background=COLORS['secondary'],
                   foreground=COLORS['text'],
                   font=FONTS['clock'])
    
    # Configure button styles
    style.configure('TButton',
                   padding=BUTTONS['padding'],
                   width=BUTTONS['width'],
                   font=FONTS['button'],
                   background=COLORS['button'])
    
    style.map('TButton',
              background=[('active', COLORS['button_hover'])])
    
    # Configure entry styles
    style.configure('TEntry',
                   fieldbackground=COLORS['button'],
                   foreground=COLORS['text'])
    
    # Configure labelframe styles
    style.configure('TLabelframe',
                   background=COLORS['secondary'])
    
    style.configure('TLabelframe.Label',
                   background=COLORS['secondary'],
                   foreground=COLORS['text'])

def apply_module_style(window, module_name=None):
    """Apply common style to a module window"""
    window.configure(bg=COLORS['primary'])
    if module_name and module_name in WINDOW['module']:
        window.geometry(f"{WINDOW['module'][module_name]['width']}x{WINDOW['module'][module_name]['height']}")
    else:
        window.geometry(f"{WINDOW['module']['default_width']}x{WINDOW['module']['default_height']}")
    configure_styles()
 