import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class CategoryManager(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Category/Scale Manager")
        self.geometry("500x400")
        self.resizable(False, False)
        self.setup_ui()
        self.load_scales()

    def setup_ui(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.scale_listbox = tk.Listbox(left_frame, width=18)
        self.scale_listbox.pack(fill=tk.Y)
        self.scale_listbox.bind('<<ListboxSelect>>', self.display_scale)

        ttk.Button(left_frame, text="New Scale", command=self.create_new_scale).pack(pady=5)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(right_frame, columns=("max_mark", "descriptor"), show="headings", selectmode="browse", height=10)
        self.tree.heading("max_mark", text="Max Mark")
        self.tree.heading("descriptor", text="Grade Descriptor")
        self.tree.column("max_mark", width=100)
        self.tree.column("descriptor", width=180)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<Double-1>', self.on_treeview_double_click)

        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Add", command=self.add_row).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_row).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Save", command=self.save_scale).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT, padx=2)

    def load_scales(self):
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'scales.json')
        self.data_path = data_path
        with open(data_path, 'r') as f:
            self.scales = json.load(f)
        self.scale_names = list(self.scales.keys())
        self.scale_listbox.delete(0, tk.END)
        for name in self.scale_names:
            self.scale_listbox.insert(tk.END, name.replace('_', ' ').title())
        if self.scale_names:
            self.scale_listbox.selection_set(0)
            self.display_scale()

    def display_scale(self, event=None):
        selection = self.scale_listbox.curselection()
        if not selection:
            self.tree.delete(*self.tree.get_children())
            return
        idx = selection[0]
        self.current_scale_key = self.scale_names[idx]
        scale = self.scales[self.current_scale_key]
        self.tree.delete(*self.tree.get_children())
        for item in scale:
            # Support both old and new formats for backward compatibility
            max_mark = item.get('max_mark')
            if max_mark is None and 'range' in item:
                # Try to extract max from range string
                import re
                match = re.findall(r'(\d+)', item['range'])
                if match:
                    max_mark = int(match[-1])
            descriptor = item.get('descriptor', '')
            self.tree.insert('', tk.END, values=(max_mark if max_mark is not None else '', descriptor))

    def on_treeview_double_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        row_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not row_id or not col:
            return
        col_idx = int(col.replace('#', '')) - 1
        x, y, width, height = self.tree.bbox(row_id, col)
        value = self.tree.set(row_id, col)
        entry = ttk.Entry(self.tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()
        def save_edit(event=None):
            new_value = entry.get().strip()
            if col_idx == 0 and not new_value.isdigit():
                entry.configure(foreground='red')
                return
            values = list(self.tree.item(row_id, 'values'))
            values[col_idx] = new_value
            self.tree.item(row_id, values=values)
            entry.destroy()
        entry.bind('<Return>', save_edit)
        entry.bind('<FocusOut>', save_edit)

    def add_row(self):
        self.tree.insert('', tk.END, values=("", ""))

    def delete_row(self):
        selected = self.tree.selection()
        if not selected:
            return
        self.tree.delete(selected[0])

    def save_scale(self):
        # Save the current treeview to the scales dict and write to file
        items = []
        for row in self.tree.get_children():
            max_mark, desc = self.tree.item(row, 'values')
            if not str(max_mark).isdigit() or not desc:
                messagebox.showerror("Invalid Data", "All rows must have a valid integer Max Mark and a non-empty Grade Descriptor.")
                return
            items.append({'max_mark': int(max_mark), 'descriptor': desc})
        self.scales[self.current_scale_key] = items
        with open(self.data_path, 'w') as f:
            json.dump(self.scales, f, indent=2)
        messagebox.showinfo("Saved", "Scale saved successfully.")

    def create_new_scale(self):
        def on_ok():
            name = entry.get().strip().lower().replace(' ', '_')
            if not name:
                messagebox.showerror("Invalid Name", "Scale name cannot be empty.")
                return
            if name in self.scales:
                messagebox.showerror("Duplicate Name", "A scale with this name already exists.")
                return
            self.scales[name] = []
            self.scale_names.append(name)
            self.scale_listbox.insert(tk.END, name.replace('_', ' ').title())
            self.scale_listbox.selection_clear(0, tk.END)
            self.scale_listbox.selection_set(tk.END)
            self.display_scale()
            dialog.destroy()
        dialog = tk.Toplevel(self)
        dialog.title("New Scale")
        dialog.geometry("250x100")
        ttk.Label(dialog, text="Enter new scale name:").pack(pady=5)
        entry = ttk.Entry(dialog)
        entry.pack(pady=5)
        ttk.Button(dialog, text="OK", command=on_ok).pack(pady=5)
        entry.focus()
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog) 