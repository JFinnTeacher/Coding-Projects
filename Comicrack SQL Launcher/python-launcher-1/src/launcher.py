class Launcher:
    def __init__(self):
        self.scripts = {}

    def add_script(self, name, script):
        self.scripts[name] = script

    def run(self, name):
        if name in self.scripts:
            exec(self.scripts[name])
        else:
            raise ValueError(f"Script '{name}' not found.")