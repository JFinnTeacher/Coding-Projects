import tkinter as tk
from tkinter import ttk
import os

class ThemeManager:
    """Manages application-wide theming"""
    
    @staticmethod
    def load_theme():
        return {
            'bg_color': '#1a1a1a',
            'accent_color': '#0066cc',
            'text_color': '#ffffff',
            'hover_color': '#0052a3',
            'input_bg': '#2a2a2a',
            'shadow_color': '#2a2a2a'
        }

class ModernFrame(tk.Frame):
    """A frame with modern styling and optional shadow effect"""
    
    def __init__(self, parent, **kwargs):
        theme = ThemeManager.load_theme()
        bg_color = kwargs.pop('bg', theme['bg_color'])
        super().__init__(parent, bg=bg_color, **kwargs)
        
        # Add subtle shadow effect
        self.shadow = tk.Frame(self, bg=theme['shadow_color'], height=1)
        self.shadow.place(relx=0, rely=1, relwidth=1)

class RoundedButton(tk.Canvas):
    """A button with rounded corners"""
    
    def __init__(self, parent, text, command=None, width=200, height=40, corner_radius=10, **kwargs):
        theme = ThemeManager.load_theme()
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent['bg'],
            highlightthickness=0,
            **kwargs
        )
        self.command = command
        
        # Create rounded rectangle
        self.rect = self.create_rounded_rect(
            0, 0, width, height,
            corner_radius,
            fill=theme['accent_color']
        )
        
        # Create text
        self.text_id = self.create_text(
            width/2,
            height/2,
            text=text,
            fill=theme['text_color'],
            font=('Helvetica', 12, 'bold')
        )
        
        # Bind events
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        self.bind('<ButtonRelease-1>', self.on_release)
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, event):
        theme = ThemeManager.load_theme()
        self.itemconfig(self.rect, fill=theme['hover_color'])
    
    def on_leave(self, event):
        theme = ThemeManager.load_theme()
        self.itemconfig(self.rect, fill=theme['accent_color'])
    
    def on_click(self, event):
        theme = ThemeManager.load_theme()
        self.itemconfig(self.rect, fill=theme['hover_color'])
    
    def on_release(self, event):
        theme = ThemeManager.load_theme()
        self.itemconfig(self.rect, fill=theme['accent_color'])
        if self.command:
            self.command()
    
    def set_text(self, text):
        self.itemconfig(self.text_id, text=text)

class ModernEntry(tk.Frame):
    """A modern styled entry widget"""
    
    def __init__(self, parent, **kwargs):
        theme = ThemeManager.load_theme()
        super().__init__(parent, bg=theme['bg_color'])
        
        self.entry = tk.Entry(
            self,
            font=('Helvetica', 12),
            bg=theme['input_bg'],
            fg=theme['text_color'],
            insertbackground=theme['text_color'],
            relief='flat',
            **kwargs
        )
        self.entry.pack(padx=2, pady=2)
    
    def get(self):
        return self.entry.get()
    
    def delete(self, first, last):
        self.entry.delete(first, last)

class ModernListbox(tk.Frame):
    """A modern-styled listbox with scrollbar"""
    
    def __init__(self, parent, **kwargs):
        theme = ThemeManager.load_theme()
        super().__init__(parent, bg=theme['bg_color'])
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(
            self,
            bg=theme['input_bg'],
            highlightthickness=0
        )
        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview
        )
        
        # Create frame for content
        self.frame = tk.Frame(
            self.canvas,
            bg=theme['input_bg']
        )
        
        # Configure canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas_frame = self.canvas.create_window(
            (0, 0),
            window=self.frame,
            anchor='nw'
        )
        
        # Pack widgets
        self.scrollbar.pack(side=tk.RIGHT, fill='y')
        self.canvas.pack(side=tk.LEFT, fill='both', expand=True)
        
        # Configure canvas scrolling
        self.frame.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
    
    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(
            self.canvas_frame,
            width=event.width
        )

class ModernWindow(tk.Toplevel):
    """Base class for modern-styled windows"""
    
    def __init__(self, parent, title, geometry):
        super().__init__(parent)
        
        self.theme = ThemeManager.load_theme()
        
        # Configure window
        self.title(title)
        self.geometry(geometry)
        self.configure(bg=self.theme['bg_color'])
        
        # Create main content frame
        self.content = ModernFrame(self)
        self.content.pack(expand=True, fill='both', padx=20, pady=20)

    def toggle_theme(self):
        self.theme = ThemeManager.load_theme()
        
        # Update window background
        self.configure(bg=self.theme['bg_color'])
        
        # Update all child widgets
        self._update_widget_colors(self)
    
    def _update_widget_colors(self, widget):
        if isinstance(widget, (tk.Label, ModernFrame)):
            widget.configure(bg=self.theme['bg_color'])
            if isinstance(widget, tk.Label):
                widget.configure(fg=self.theme['text_color'])
        
        if isinstance(widget, ModernEntry):
            widget.configure(bg=self.theme['input_bg'])
            widget.configure(fg=self.theme['text_color'])
        
        if isinstance(widget, RoundedButton):
            widget.update_colors(
                bg_color=self.theme['accent_color'],
                fg_color=self.theme['text_color'],
                hover_color=self.theme['hover_color']
            )
        
        # Recursively update all child widgets
        for child in widget.winfo_children():
            self._update_widget_colors(child)

    def create_header(self, title):
        header = ModernFrame(self.container, bg=self.theme['bg_color'])
        header.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            header,
            text=title,
            font=("Helvetica", 24, "bold"),
            bg=self.theme['bg_color'],
            fg=self.theme['accent_color']
        ).pack(pady=10) 