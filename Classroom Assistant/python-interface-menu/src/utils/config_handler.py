class ConfigHandler:
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.settings = {}

    def load_settings(self):
        """Load settings from the config.ini file."""
        try:
            with open(self.config_file, 'r') as file:
                for line in file:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        self.settings[key.strip()] = value.strip()
        except FileNotFoundError:
            print(f"Config file {self.config_file} not found. Using default settings.")

    def save_settings(self):
        """Save settings to the config.ini file."""
        with open(self.config_file, 'w') as file:
            for key, value in self.settings.items():
                file.write(f"{key}={value}\n")

    def get_setting(self, key, default=None):
        """Get a setting value by key."""
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        """Set a setting value by key."""
        self.settings[key] = value