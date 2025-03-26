class TimeDisplay:
    def __init__(self, label):
        self.label = label

    def update_time(self):
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.label.config(text=current_time)

    def start_time_update(self, interval=1000):
        self.update_time()
        self.label.after(interval, self.start_time_update, interval)