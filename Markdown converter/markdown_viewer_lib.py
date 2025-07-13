import customtkinter as ctk
import tkinter as tk
from tkinter import font as tkfont
import webbrowser
import tempfile
import os
import re

class MarkdownViewer(ctk.CTkFrame):
    """
    A customtkinter-based markdown viewer widget that renders markdown content
    using a simple HTML-based approach.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create a simple label for status
        self.status_label = ctk.CTkLabel(
            self,
            text="Rendering markdown...",
            font=("Arial", 12)
        )
        self.status_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
    def _get_theme_colors(self):
        """Get the current theme colors."""
        if ctk.get_appearance_mode() == "Dark":
            return {
                "bg": "#2b2b2b",
                "fg": "#ffffff",
                "link": "#4a9eff",
                "quote": "#a0a0a0",
                "code_bg": "#333333"
            }
        else:
            return {
                "bg": "#ffffff",
                "fg": "#000000",
                "link": "#0000ff",
                "quote": "#666666",
                "code_bg": "#f0f0f0"
            }
        
    def _convert_markdown_to_html(self, markdown_text):
        """Convert markdown to HTML using simple regex replacements."""
        # Headers
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', markdown_text, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        
        # Bold and Italic
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Code blocks
        html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
        
        # Links
        html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
        
        # Lists
        html = re.sub(r'^\s*[-*+]\s+(.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\g<0></ul>', html)
        
        # Blockquotes
        html = re.sub(r'^\s*>\s*(.*?)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
        
        # Tables
        def process_table(match):
            rows = match.group(1).strip().split('\n')
            if len(rows) < 2:
                return match.group(0)
            
            # Process header
            header_cells = [cell.strip() for cell in rows[0].strip('|').split('|')]
            header_html = '<tr>' + ''.join(f'<th>{cell}</th>' for cell in header_cells) + '</tr>'
            
            # Process separator
            separator = rows[1].strip('|').split('|')
            alignments = []
            for cell in separator:
                cell = cell.strip()
                if cell.startswith(':') and cell.endswith(':'):
                    alignments.append('center')
                elif cell.endswith(':'):
                    alignments.append('right')
                else:
                    alignments.append('left')
            
            # Process data rows
            data_rows = []
            for row in rows[2:]:
                cells = [cell.strip() for cell in row.strip('|').split('|')]
                if len(cells) == len(header_cells):
                    row_html = '<tr>'
                    for cell, align in zip(cells, alignments):
                        row_html += f'<td style="text-align: {align}">{cell}</td>'
                    row_html += '</tr>'
                    data_rows.append(row_html)
            
            return f'<table>{header_html}{"".join(data_rows)}</table>'
        
        html = re.sub(r'(\|[^\n]+\n\|[^\n]+\n(?:\|[^\n]+\n)+)', process_table, html)
        
        # Paragraphs
        html = re.sub(r'\n\n', r'</p><p>', html)
        html = f'<p>{html}</p>'
        
        return html
        
    def display_markdown(self, markdown_text):
        """
        Display markdown content with proper formatting.
        
        Args:
            markdown_text (str): The markdown content to display
        """
        # Get theme colors
        colors = self._get_theme_colors()
        
        # Convert markdown to HTML
        html_content = self._convert_markdown_to_html(markdown_text)
        
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
                    background-color: {colors['bg']};
                    color: {colors['fg']};
                }}
                pre {{
                    background-color: {colors['code_bg']};
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
                    border: 1px solid {colors['code_bg']};
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: {colors['code_bg']};
                    font-weight: bold;
                }}
                tr:nth-child(even) {{
                    background-color: {colors['code_bg']};
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
                a {{
                    color: {colors['link']};
                    text-decoration: underline;
                }}
                blockquote {{
                    border-left: 4px solid {colors['quote']};
                    margin: 0;
                    padding-left: 20px;
                    color: {colors['quote']};
                }}
                h1, h2, h3, h4, h5, h6 {{
                    margin-top: 24px;
                    margin-bottom: 16px;
                    font-weight: 600;
                    line-height: 1.25;
                }}
                h1 {{ font-size: 2em; }}
                h2 {{ font-size: 1.5em; }}
                h3 {{ font-size: 1.25em; }}
                ul, ol {{
                    padding-left: 2em;
                }}
                li {{
                    margin: 0.25em 0;
                }}
                hr {{
                    height: 0.25em;
                    padding: 0;
                    margin: 24px 0;
                    background-color: {colors['code_bg']};
                    border: 0;
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
        
    def clear(self):
        """Clear the current content."""
        self.status_label.configure(text="Ready to display markdown")
        
    def set_readonly(self, readonly=True):
        """Set the viewer to read-only mode."""
        pass  # No-op since we're using HTML rendering

class MarkdownPreviewWindow(ctk.CTkToplevel):
    """
    A window that displays markdown content using the MarkdownViewer widget.
    """
    def __init__(self, master, title="Markdown Preview", width=800, height=600):
        super().__init__(master)
        
        # Configure window
        self.title(title)
        self.geometry(f"{width}x{height}")
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create markdown viewer
        self.viewer = MarkdownViewer(self)
        self.viewer.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
    def display_markdown(self, markdown_text):
        """Display markdown content in the viewer."""
        self.viewer.display_markdown(markdown_text)
        self.deiconify()  # Show the window
        self.lift()  # Bring to front 