import tkinter as tk
from tkinter import ttk
import base64

def encode_text():
    input_text = input_entry.get("1.0", tk.END).strip()
    encoded_bytes = base64.b64encode(input_text.encode('utf-8'))
    encoded_text = encoded_bytes.decode('utf-8')
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, encoded_text)

def decode_text():
    input_text = input_entry.get("1.0", tk.END).strip()
    try:
        decoded_bytes = base64.b64decode(input_text)
        decoded_text = decoded_bytes.decode('utf-8')
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, decoded_text)
    except Exception as e:
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, "Error decoding: " + str(e))

def encode_twice():
    input_text = input_entry.get("1.0", tk.END).strip()
    # First encoding
    encoded_bytes = base64.b64encode(input_text.encode('utf-8'))
    encoded_text = encoded_bytes.decode('utf-8')
    # Second encoding
    encoded_bytes_twice = base64.b64encode(encoded_text.encode('utf-8'))
    encoded_text_twice = encoded_bytes_twice.decode('utf-8')
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, encoded_text_twice)

def decode_twice():
    input_text = input_entry.get("1.0", tk.END).strip()
    try:
        # First decoding
        decoded_bytes = base64.b64decode(input_text)
        decoded_text = decoded_bytes.decode('utf-8')
        # Second decoding
        decoded_bytes_twice = base64.b64decode(decoded_text)
        decoded_text_twice = decoded_bytes_twice.decode('utf-8')
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, decoded_text_twice)
    except Exception as e:
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, "Error decoding: " + str(e))

def copy_to_clipboard():
    decoded_text = output_text.get("1.0", tk.END).strip()
    root.clipboard_clear()  # Clear the clipboard
    root.clipboard_append(decoded_text)  # Append the decoded text to the clipboard

def exit_app():
    root.quit()  # Close the application

# Create the main window
root = tk.Tk()
root.title("Base64 Encoder/Decoder")
root.geometry("600x400")  # Set a fixed size for the window

# Create input text area
input_label = ttk.Label(root, text="Input Text:")
input_label.pack(pady=5)
input_entry = tk.Text(root, height=10, width=50)
input_entry.pack(pady=5)

# Create buttons for encoding and decoding
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

encode_button = ttk.Button(button_frame, text="Encode", command=encode_text)
encode_button.grid(row=0, column=0, padx=5)

encode_twice_button = ttk.Button(button_frame, text="Encode Twice", command=encode_twice)
encode_twice_button.grid(row=0, column=1, padx=5)

decode_button = ttk.Button(button_frame, text="Decode", command=decode_text)
decode_button.grid(row=0, column=2, padx=5)

decode_twice_button = ttk.Button(button_frame, text="Decode Twice", command=decode_twice)
decode_twice_button.grid(row=0, column=3, padx=5)

copy_button = ttk.Button(button_frame, text="Copy", command=copy_to_clipboard)
copy_button.grid(row=0, column=4, padx=5)

exit_button = ttk.Button(button_frame, text="Exit", command=exit_app)
exit_button.grid(row=0, column=5, padx=5)

# Create output text area
output_label = ttk.Label(root, text="Output Text:")
output_label.pack(pady=5)
output_text = tk.Text(root, height=10, width=50)
output_text.pack(pady=5)

# Start the GUI event loop
root.mainloop()
