import tkinter as tk
from tkinter import ttk, messagebox
from gui.category_manager import CategoryManager
from gui.feedback_template_manager import FeedbackTemplateManager

class MainWindow:
    def __init__(self, master):
        self.master = master
        self.setup_ui()

    def setup_ui(self):
        # Student Info Frame
        student_frame = ttk.LabelFrame(self.master, text="Student Information")
        student_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(student_frame, text="Name:").grid(row=0, column=0, sticky="w")
        self.name_entry = ttk.Entry(student_frame)
        self.name_entry.grid(row=0, column=1, sticky="ew")

        ttk.Label(student_frame, text="Gender:").grid(row=1, column=0, sticky="w")
        self.gender_var = tk.StringVar()
        gender_combo = ttk.Combobox(student_frame, textvariable=self.gender_var, values=["Male", "Female", "Other"])
        gender_combo.grid(row=1, column=1, sticky="ew")
        gender_combo.current(0)

        # Grades Frame (placeholder)
        grades_frame = ttk.LabelFrame(self.master, text="Assessment Grades")
        grades_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        # TODO: Dynamically generate grade fields based on categories

        # Generate Feedback Button
        generate_btn = ttk.Button(self.master, text="Generate Feedback", command=self.generate_feedback)
        generate_btn.grid(row=2, column=0, pady=10)

        # Feedback Output
        self.feedback_text = tk.Text(self.master, height=8, width=60)
        self.feedback_text.grid(row=3, column=0, padx=10, pady=10)

        # Menu for editing templates and categories
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Feedback Templates", command=self.open_feedback_editor)
        edit_menu.add_command(label="Categories/Scales", command=self.open_category_manager)

    def generate_feedback(self):
        # Placeholder for feedback generation logic
        self.feedback_text.delete("1.0", tk.END)
        self.feedback_text.insert(tk.END, "[Generated feedback will appear here]")

    def open_feedback_editor(self):
        FeedbackTemplateManager(self.master)

    def open_category_manager(self):
        CategoryManager(self.master) 