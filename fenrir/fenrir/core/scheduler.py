
from apscheduler.schedulers.background import BackgroundScheduler

class Scheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def start(self):
        self.scheduler.start()
