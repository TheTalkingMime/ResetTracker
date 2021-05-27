from watchdog.events import FileSystemEventHandler
from Stats import Stats
from Achievements import Achievements
from watchdog.observers import Observer
import time


class Buffer(FileSystemEventHandler):
    a_observer = None
    s_observer = None
    stats = None
    achievements = None
    path = None

    def __init__(self):

        self.achievements = Achievements()
        self.stats = Stats(self.achievements)

    def on_created(self, event):
        self.path = event.src_path
        if not event.is_directory:
            return

        if event.src_path[-5:] == "stats":
            self.s_observer = Observer()
            self.s_observer.schedule(self.stats, event.src_path, recursive=False)
            self.s_observer.start()

        if event.src_path[-12:] == "advancements":
            self.a_observer = Observer()
            self.a_observer.schedule(
                self.achievements,
                event.src_path,
                recursive=False,
            )
            self.a_observer.start()

    def stop(self):
        if self.s_observer != None:
            self.s_observer.stop()
        if self.a_observer != None:
            self.a_observer.stop()

    def getRun(self):
        if self.stats.getRun()[0] == None:
            return None
        if self.achievements != None and self.stats != None:
            return self.achievements.getRun() + self.stats.getRun()
