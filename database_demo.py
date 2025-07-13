import sqlite3
from sqlite3 import Error
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class DatabaseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Database Manager")
        self.root.geometry("800x600")
        
        # Database connection
        self.conn = None
        self.current_db = None
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Create main frames
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(fill=tk.X, pady=5)
        
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=5)
        
        # Database connection controls
        ttk.Button(self.top_frame, text="New Database", command=self.create_new_database).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.top_frame, text="Open Database", command=self.open_database).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.top_frame, text="Close Database", command=self.close_database).pack(side=tk.LEFT, padx=5)
        
        # Create buttons
        ttk.Button(button_frame, text="Create Table", command=self.create_table).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Insert Sample Data", command=self.insert_sample_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh Data", command=self.display_data).pack(side=tk.LEFT, padx=5)
        
        # Create user input frame
        input_frame = ttk.LabelFrame(self.root, text="Add New User")
        input_frame.pack(pady=10, padx=10, fill=tk.X)
        
        # Name input
        ttk.Label(input_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.name_var).grid(row=0, column=1, padx=5, pady=5)
        
        # Email input
        ttk.Label(input_frame, text="Email:").grid(row=0, column=2, padx=5, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.email_var).grid(row=0, column=3, padx=5, pady=5)
        
        # Add user button
        ttk.Button(input_frame, text="Add User", command=self.add_user).grid(row=0, column=4, padx=5, pady=5)
        
        # Create Treeview for data display
        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Email"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Email", text="Email")
        self.tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Not connected to database")
        status_label = ttk.Label(self.root, textvariable=self.status_var)
        status_label.pack(pady=5)

    def create_new_database(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if file_path:
            self.close_database()  # Close existing connection if any
            try:
                self.conn = sqlite3.connect(file_path)
                self.current_db = file_path
                self.status_var.set(f"Created and connected to new database: {file_path}")
                messagebox.showinfo("Success", "New database created successfully!")
            except Error as e:
                self.status_var.set(f"Error: {e}")
                messagebox.showerror("Error", f"Could not create database: {e}")

    def open_database(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if file_path:
            self.close_database()  # Close existing connection if any
            try:
                self.conn = sqlite3.connect(file_path)
                self.current_db = file_path
                self.status_var.set(f"Connected to database: {file_path}")
                messagebox.showinfo("Success", "Connected to database successfully!")
            except Error as e:
                self.status_var.set(f"Error: {e}")
                messagebox.showerror("Error", f"Could not open database: {e}")

    def close_database(self):
        if self.conn:
            try:
                self.conn.close()
                self.conn = None
                self.current_db = None
                self.status_var.set("Database connection closed")
                # Clear the treeview
                for item in self.tree.get_children():
                    self.tree.delete(item)
                messagebox.showinfo("Success", "Database connection closed successfully!")
            except Error as e:
                self.status_var.set(f"Error: {e}")
                messagebox.showerror("Error", f"Could not close database: {e}")

    def add_user(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
            
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        
        if not name or not email:
            messagebox.showerror("Error", "Please fill in both name and email!")
            return
            
        try:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
            self.conn.commit()
            self.status_var.set("New user added successfully")
            messagebox.showinfo("Success", "User added successfully!")
            
            # Clear the input fields
            self.name_var.set("")
            self.email_var.set("")
            
            # Refresh the display
            self.display_data()
        except Error as e:
            self.status_var.set(f"Error: {e}")
            messagebox.showerror("Error", f"Could not add user: {e}")

    def create_table(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
            
        try:
            cursor = self.conn.cursor()
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            );
            """
            cursor.execute(create_table_sql)
            self.status_var.set("Table created successfully")
            messagebox.showinfo("Success", "Table created successfully!")
        except Error as e:
            self.status_var.set(f"Error: {e}")
            messagebox.showerror("Error", f"Could not create table: {e}")

    def insert_sample_data(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
            
        try:
            cursor = self.conn.cursor()
            sample_users = [
                ('John Doe', 'john@example.com'),
                ('Jane Smith', 'jane@example.com'),
                ('Bob Wilson', 'bob@example.com')
            ]
            cursor.executemany('INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)', sample_users)
            self.conn.commit()
            self.status_var.set("Sample data inserted successfully")
            messagebox.showinfo("Success", "Sample data inserted successfully!")
            self.display_data()
        except Error as e:
            self.status_var.set(f"Error: {e}")
            messagebox.showerror("Error", f"Could not insert data: {e}")

    def display_data(self):
        if not self.conn:
            messagebox.showerror("Error", "Please connect to database first!")
            return
            
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            
            self.status_var.set(f"Displaying {len(rows)} records")
        except Error as e:
            self.status_var.set(f"Error: {e}")
            messagebox.showerror("Error", f"Could not fetch data: {e}")

def main():
    root = tk.Tk()
    app = DatabaseGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main() 