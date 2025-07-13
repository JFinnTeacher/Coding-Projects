# MarkItDown GUI Converter

A modern GUI application for converting various file formats to Markdown using Microsoft's MarkItDown library.

## Features

- Modern, user-friendly interface
- Support for multiple file formats:
  - PDF
  - Word Documents (.docx)
  - PowerPoint Presentations (.pptx)
  - Excel Spreadsheets (.xlsx)
  - Text Files (.txt)
  - HTML Files (.html)
- Progress tracking
- Error handling
- Dark/Light mode support

## Installation

1. Make sure you have Python 3.10 or higher installed
2. Clone this repository or download the source files
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:

```bash
python markitdown_gui.py
```

2. Use the interface to:
   - Select an input file using the "Browse" button
   - Choose an output directory using the "Browse" button
   - Click "Convert to Markdown" to start the conversion
   - Wait for the conversion to complete
   - The converted markdown file will be saved in your chosen output directory

## Requirements

- Python 3.10+
- markitdown[all]
- customtkinter
- pillow

## License

This project is licensed under the MIT License - see the LICENSE file for details. 