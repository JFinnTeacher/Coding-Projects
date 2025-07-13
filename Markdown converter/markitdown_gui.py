import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from markitdown import MarkItDown
import os
from PIL import Image
import threading
from markdown_viewer_lib import MarkdownPreviewWindow
import shutil

class MarkItDownGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("MarkItDown Converter")
        self.geometry("800x600")  # Reduced window size
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  # Reduced padding
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)  # Changed to 4 to accommodate options frame

        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="MarkItDown File Converter",
            font=ctk.CTkFont(size=20, weight="bold")  # Reduced font size
        )
        self.title_label.grid(row=0, column=0, padx=10, pady=(10, 5))  # Reduced padding

        # File selection frame
        self.file_frame = ctk.CTkFrame(self.main_frame)
        self.file_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")  # Reduced padding
        self.file_frame.grid_columnconfigure(1, weight=1)

        self.file_label = ctk.CTkLabel(self.file_frame, text="Select File:")
        self.file_label.grid(row=0, column=0, padx=5, pady=5)  # Reduced padding

        self.file_path = ctk.CTkEntry(self.file_frame, placeholder_text="No file selected")
        self.file_path.grid(row=0, column=1, padx=5, pady=5, sticky="ew")  # Reduced padding

        self.browse_button = ctk.CTkButton(
            self.file_frame, 
            text="Browse",
            command=self.browse_file,
            width=80  # Fixed width for button
        )
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)  # Reduced padding

        # Output directory frame
        self.output_frame = ctk.CTkFrame(self.main_frame)
        self.output_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")  # Reduced padding
        self.output_frame.grid_columnconfigure(1, weight=1)

        self.output_label = ctk.CTkLabel(self.output_frame, text="Output Directory:")
        self.output_label.grid(row=0, column=0, padx=5, pady=5)  # Reduced padding

        self.output_path = ctk.CTkEntry(self.output_frame, placeholder_text="No directory selected")
        self.output_path.grid(row=0, column=1, padx=5, pady=5, sticky="ew")  # Reduced padding

        self.output_button = ctk.CTkButton(
            self.output_frame, 
            text="Browse",
            command=self.browse_output,
            width=80  # Fixed width for button
        )
        self.output_button.grid(row=0, column=2, padx=5, pady=5)  # Reduced padding

        # Options frame
        self.options_frame = ctk.CTkFrame(self.main_frame)
        self.options_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")  # Reduced padding
        self.options_frame.grid_columnconfigure(0, weight=1)
        self.options_frame.grid_columnconfigure(1, weight=1)

        # Left column options
        self.preserve_layout_var = tk.BooleanVar(value=True)
        self.preserve_layout_check = ctk.CTkCheckBox(
            self.options_frame,
            text="Preserve Layout",
            variable=self.preserve_layout_var,
            command=self.update_options
        )
        self.preserve_layout_check.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.enable_plugins_var = tk.BooleanVar(value=False)
        self.enable_plugins_check = ctk.CTkCheckBox(
            self.options_frame,
            text="Enable Plugins",
            variable=self.enable_plugins_var,
            command=self.update_options
        )
        self.enable_plugins_check.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        # Right column options
        self.image_handling_label = ctk.CTkLabel(self.options_frame, text="Image Handling:")
        self.image_handling_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.image_handling_var = tk.StringVar(value="extract")
        self.image_handling_menu = ctk.CTkOptionMenu(
            self.options_frame,
            values=["extract", "embed", "skip"],
            variable=self.image_handling_var,
            command=self.update_options
        )
        self.image_handling_menu.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.image_format_label = ctk.CTkLabel(self.options_frame, text="Image Format:")
        self.image_format_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.image_format_var = tk.StringVar(value="png")
        self.image_format_menu = ctk.CTkOptionMenu(
            self.options_frame,
            values=["png", "jpg", "webp"],
            variable=self.image_format_var,
            command=self.update_options
        )
        self.image_format_menu.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        # Button frame for Convert and Open Markdown
        self.action_frame = ctk.CTkFrame(self.main_frame)
        self.action_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")  # Reduced padding
        self.action_frame.grid_columnconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure(1, weight=1)

        # Convert button
        self.convert_button = ctk.CTkButton(
            self.action_frame,
            text="Convert to Markdown",
            command=self.start_conversion,
            font=ctk.CTkFont(size=14, weight="bold")  # Reduced font size
        )
        self.convert_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Open Markdown button
        self.open_md_button = ctk.CTkButton(
            self.action_frame,
            text="Open Markdown File",
            command=self.open_markdown_file,
            font=ctk.CTkFont(size=14, weight="bold"),  # Reduced font size
            fg_color="#2E7D32",  # Green color
            hover_color="#1B5E20"
        )
        self.open_md_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")  # Reduced padding

        # Progress frame
        self.progress_frame = ctk.CTkFrame(self.main_frame)
        self.progress_frame.grid(row=5, column=0, padx=10, pady=5, sticky="ew")  # Reduced padding
        self.progress_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.grid(row=0, column=0, padx=5, pady=5, sticky="ew")  # Reduced padding
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            self.progress_frame,
            text="Ready to convert",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=1, column=0, padx=5, pady=(0, 5))  # Reduced padding

        # Status window (multi-line, read-only)
        self.status_window = ctk.CTkTextbox(self.main_frame, height=100, state="disabled")  # Reduced height
        self.status_window.grid(row=6, column=0, padx=10, pady=(5, 0), sticky="nsew")  # Reduced padding
        self.main_frame.grid_rowconfigure(6, weight=1)

        # Button frame for Preview and Exit
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.grid(row=7, column=0, padx=10, pady=(5, 10), sticky="ew")  # Reduced padding
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        # Preview button
        self.preview_button = ctk.CTkButton(
            self.button_frame,
            text="Preview Markdown",
            command=self.preview_markdown,
            fg_color="green",
            hover_color="#006400"
        )
        self.preview_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")  # Reduced padding

        # Exit button
        self.exit_button = ctk.CTkButton(
            self.button_frame,
            text="Exit",
            command=self.on_exit,
            fg_color="red",
            hover_color="#b22222"
        )
        self.exit_button.grid(row=0, column=1, padx=5, pady=5, sticky="e")  # Reduced padding

        # Create preview window (initially hidden)
        self.preview_window = None

        # Initialize MarkItDown with default options
        self.update_options()

    def update_options(self, *args):
        """Update the MarkItDown converter with current options."""
        self.converter = MarkItDown(
            enable_plugins=self.enable_plugins_var.get(),
            preserve_layout=self.preserve_layout_var.get(),
            image_handling=self.image_handling_var.get(),
            image_format=self.image_format_var.get()
        )

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("All Supported Files", "*.pdf;*.docx;*.pptx;*.xlsx;*.txt;*.html"),
                ("PDF Files", "*.pdf"),
                ("Word Documents", "*.docx"),
                ("PowerPoint Presentations", "*.pptx"),
                ("Excel Spreadsheets", "*.xlsx"),
                ("Text Files", "*.txt"),
                ("HTML Files", "*.html"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.file_path.delete(0, tk.END)
            self.file_path.insert(0, file_path)

    def browse_output(self):
        output_dir = filedialog.askdirectory()
        if output_dir:
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, output_dir)

    def start_conversion(self):
        input_file = self.file_path.get()
        output_dir = self.output_path.get()

        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Error", "Please select a valid input file")
            self.log_status("Error: Please select a valid input file.")
            return

        if not output_dir or not os.path.exists(output_dir):
            messagebox.showerror("Error", "Please select a valid output directory")
            self.log_status("Error: Please select a valid output directory.")
            return

        # Disable convert button during conversion
        self.convert_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Converting...")
        self.log_status(f"Starting conversion: {input_file} -> {output_dir}")

        # Start conversion in a separate thread
        thread = threading.Thread(target=self.convert_file, args=(input_file, output_dir))
        thread.start()

    def convert_file(self, input_file, output_dir):
        try:
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(output_dir, f"{base_name}.md")
            images_dir = os.path.join(output_dir, f"{base_name}_images")
            
            # Create images directory if needed
            if self.image_handling_var.get() == "extract":
                os.makedirs(images_dir, exist_ok=True)
            
            self.after(0, self.log_status, f"Converting {input_file} to {output_file}...")
            
            # Update converter options before conversion
            self.update_options()
            
            # Convert the file
            result = self.converter.convert(input_file)
            
            # Handle images if needed
            if self.image_handling_var.get() == "extract" and hasattr(result, 'images'):
                self.after(0, self.log_status, "Extracting images...")
                for i, img in enumerate(result.images):
                    img_path = os.path.join(images_dir, f"image_{i+1}.{self.image_format_var.get()}")
                    img.save(img_path)
                    # Update image references in markdown
                    result.text_content = result.text_content.replace(
                        f"![image_{i+1}]",
                        f"![image_{i+1}]({os.path.relpath(img_path, output_dir).replace(os.sep, '/')})"
                    )
            
            # Save markdown file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.text_content)
            
            self.after(0, self.log_status, f"Conversion successful! Saved to: {output_file}")
            self.after(0, self.conversion_complete, True, output_file)
            
        except Exception as e:
            self.after(0, self.log_status, f"Conversion failed: {e}")
            self.after(0, self.conversion_complete, False, str(e))

    def conversion_complete(self, success, message):
        self.progress_bar.set(1)
        if success:
            self.status_label.configure(text=f"Conversion complete! Saved to: {message}")
            self.log_status(f"Conversion complete! Saved to: {message}")
            messagebox.showinfo("Success", f"File converted successfully!\nSaved to: {message}")
        else:
            self.status_label.configure(text=f"Conversion failed: {message}")
            self.log_status(f"Conversion failed: {message}")
            messagebox.showerror("Error", f"Conversion failed: {message}")
        self.convert_button.configure(state="normal")

    def log_status(self, message):
        self.status_window.configure(state="normal")
        self.status_window.insert(tk.END, message + "\n")
        self.status_window.see(tk.END)
        self.status_window.configure(state="disabled")

    def preview_markdown(self):
        output_dir = self.output_path.get()
        if not output_dir or not os.path.exists(output_dir):
            messagebox.showerror("Error", "Please select a valid output directory")
            self.log_status("Error: Please select a valid output directory.")
            return

        input_file = self.file_path.get()
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Error", "Please select a valid input file")
            self.log_status("Error: Please select a valid input file.")
            return

        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(output_dir, f"{base_name}.md")

        if not os.path.exists(output_file):
            messagebox.showerror("Error", "Output file not found. Please convert the file first.")
            self.log_status("Error: Output file not found. Please convert the file first.")
            return

        try:
            # Read the markdown file
            with open(output_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            # Create preview window if it doesn't exist
            if self.preview_window is None:
                self.preview_window = MarkdownPreviewWindow(
                    self,
                    title=f"Preview: {os.path.basename(output_file)}"
                )

            # Display markdown content
            self.preview_window.display_markdown(markdown_content)
            self.log_status(f"Previewing: {os.path.basename(output_file)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview markdown: {str(e)}")
            self.log_status(f"Failed to preview markdown: {str(e)}")

    def open_markdown_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Markdown Files", "*.md"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            try:
                # Read the markdown file
                with open(file_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()

                # Create preview window if it doesn't exist
                if self.preview_window is None:
                    self.preview_window = MarkdownPreviewWindow(
                        self,
                        title=f"Preview: {os.path.basename(file_path)}"
                    )

                # Display markdown content
                self.preview_window.display_markdown(markdown_content)
                self.log_status(f"Opened markdown file: {file_path}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to open markdown file: {str(e)}")
                self.log_status(f"Failed to open markdown file: {str(e)}")

    def on_exit(self):
        self.destroy()

if __name__ == "__main__":
    # Set appearance mode and default color theme
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

    app = MarkItDownGUI()
    app.mainloop() 