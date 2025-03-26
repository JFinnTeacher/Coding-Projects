class Appearance:
    def __init__(self, config_handler):
        self.config_handler = config_handler
        self.settings = self.load_settings()

    def load_settings(self):
        return self.config_handler.load_config()

    def apply_settings(self):
        # Logic to apply the appearance settings to the UI
        pass

    def update_color_scheme(self, new_scheme):
        self.settings['color_scheme'] = new_scheme
        self.config_handler.save_config(self.settings)
        self.apply_settings()