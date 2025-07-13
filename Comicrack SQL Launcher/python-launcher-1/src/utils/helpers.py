def load_script(script_path):
    """Load a script from the given path."""
    with open(script_path, 'r') as file:
        return file.read()

def log(message):
    """Log a message to the console."""
    print(f"[LOG] {message}")