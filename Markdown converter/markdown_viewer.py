import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import markdown
import webbrowser
import os
import tempfile

class MarkdownViewer(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Markdown Viewer")
        self.geometry("1000x800")
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Markdown Viewer",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # File selection frame
        self.file_frame = ctk.CTkFrame(self.main_frame)
        self.file_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.file_frame.grid_columnconfigure(1, weight=1)

        self.file_label = ctk.CTkLabel(self.file_frame, text="Select Markdown File:")
        self.file_label.grid(row=0, column=0, padx=10, pady=10)

        self.file_path = ctk.CTkEntry(self.file_frame, placeholder_text="No file selected")
        self.file_path.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.browse_button = ctk.CTkButton(
            self.file_frame, 
            text="Browse",
            command=self.browse_file
        )
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        # Preview button
        self.preview_button = ctk.CTkButton(
            self.file_frame,
            text="Preview",
            command=self.preview_markdown,
            fg_color="green",
            hover_color="#006400"
        )
        self.preview_button.grid(row=0, column=3, padx=10, pady=10)

        # Status label
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Ready to preview markdown files",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=2, column=0, padx=20, pady=(0, 10))

        # Exit button
        self.exit_button = ctk.CTkButton(
            self.main_frame,
            text="Exit",
            command=self.on_exit,
            fg_color="red",
            hover_color="#b22222"
        )
        self.exit_button.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="e")

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Markdown Files", "*.md"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.file_path.delete(0, tk.END)
            self.file_path.insert(0, file_path)

    def preview_markdown(self):
        file_path = self.file_path.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid markdown file")
            return

        try:
            # Read the markdown file
            with open(file_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            # Convert markdown to HTML
            html_content = markdown.markdown(
                markdown_content,
                extensions=['tables', 'fenced_code', 'codehilite']
            )

            # Create a complete HTML document with CSS styling
            html_doc = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    pre {{
                        background-color: #f8f8f8;
                        padding: 10px;
                        border-radius: 5px;
                        overflow-x: auto;
                    }}
                    code {{
                        font-family: 'Courier New', Courier, monospace;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 20px 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f2f2f2;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """

            # Create a temporary HTML file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as f:
                f.write(html_doc)
                temp_path = f.name

            # Open the HTML file in the default browser
            webbrowser.open('file://' + temp_path)
            self.status_label.configure(text=f"Previewing: {os.path.basename(file_path)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview markdown: {str(e)}")
            self.status_label.configure(text=f"Error: {str(e)}")

    def on_exit(self):
        self.destroy()

if __name__ == "__main__":
    # Set appearance mode and default color theme
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

    app = MarkdownViewer()
    app.mainloop() 