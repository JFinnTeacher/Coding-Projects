import tkinter as tk
from tkinter import ttk, messagebox
import random
from ..common_styles import apply_module_style
from config.settings import COLORS, WINDOW, GRID, MODULES

class RandomStudentWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title(MODULES['random_student']['title'])
        
        # Apply common styles
        apply_module_style(self.window, 'random_student')
        
        # Student list
        self.students = []
        
        # Configure window grid
        self.window.columnconfigure(0, weight=1)
        
        # Create main frame
        main_frame = ttk.Frame(
            self.window,
            padding=WINDOW['module']['padding'],
            style='Main.TFrame'
        )
        main_frame.grid(sticky="nsew", **GRID['padding'])
        
        # Create student entry section
        entry_frame = ttk.LabelFrame(main_frame, text="Add Student", padding="10")
        entry_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        self.student_entry = ttk.Entry(entry_frame, style='TEntry')
        self.student_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        add_button = ttk.Button(entry_frame, text="Add Student", command=self.add_student)
        add_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Student listbox frame
        list_frame = ttk.LabelFrame(main_frame, text="Student List", padding="10")
        list_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)
        
        # Configure listbox colors
        self.student_listbox = tk.Listbox(
            list_frame,
            height=10,
            bg=COLORS['button'],
            fg=COLORS['text'],
            selectbackground=COLORS['highlight'],
            selectforeground='white'
        )
        self.student_listbox.grid(row=0, column=0, columnspan=2, pady=10, sticky="nsew")
        
        # Remove student button
        remove_button = ttk.Button(list_frame, text="Remove Selected", command=self.remove_student)
        remove_button.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Random selection button
        select_button = ttk.Button(main_frame, text="Select Random Student", command=self.select_random)
        select_button.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Selected student label
        self.result_label = ttk.Label(main_frame, text="", style='Title.TLabel')
        self.result_label.grid(row=3, column=0, columnspan=2, pady=10)
        
    def add_student(self):
        student = self.student_entry.get().strip()
        if student:
            self.students.append(student)
            self.student_listbox.insert(tk.END, student)
            self.student_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Please enter a student name")
            
    def remove_student(self):
        selection = self.student_listbox.curselection()
        if selection:
            index = selection[0]
            self.student_listbox.delete(index)
            self.students.pop(index)
        else:
            messagebox.showwarning("Warning", "Please select a student to remove")
            
    def select_random(self):
        if self.students:
            selected = random.choice(self.students)
            self.result_label.config(text=f"Selected: {selected}")
        else:
            messagebox.showwarning("Warning", "No students in the list")

def open_window(parent):
    RandomStudentWindow(parent) 