from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from time import time_ns

from stats import Stats
from advancements import Advancements


class World(FileSystemEventHandler):
	def __init__(self, callback):
		self.callback = callback

		self.active = False

		self.file_watchdog = None
		self.loaded = False

		self.stats = Stats(callback)
		self.advancements = Advancements(callback)

	def on_created(self, event):
		if not event.is_directory:
			return

		if not self.loaded and event.src_path[-5:] == "stats" or event.src_path[-5:] == "advancements":
			self.loaded = True
			self.callback({
				"world loaded": time_ns() // 1000000
			})

		if event.src_path[-5:] == "stats":
			self.stats.set_path(event.src_path)

		if event.src_path[-12:] == "advancements":
			self.advancements.set_path(event.src_path)

	def set_world(self, path):
		if self.active:
			self.stop()
		self.file_watchdog = Observer()
		self.file_watchdog.schedule(self, path, recursive=False)
		self.file_watchdog.start()
		self.active = True

	def stop(self):
		if not self.file_watchdog == None:
			self.file_watchdog.stop()
			self.file_watchdog.join()
		self.stats.stop()
		self.advancements.stop()

		self.loaded = False
		self.active = False
