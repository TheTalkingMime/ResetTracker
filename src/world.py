from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from time import time_ns
import os

from stats import Stats
from advancements import Advancements
from tracking import Parsed_Value

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
			self.callback([Parsed_Value(time_ns() // 1000000, "meta", "world loaded")])

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
	
	def injest_world(self, path):
		self.callback([
			Parsed_Value(os.path.getctime(os.path.join(path, "datapacks")), "meta", "world created"),
			Parsed_Value(os.path.getctime(os.path.join(path, "advancements")), "meta", "world loaded"),
			Parsed_Value(os.path.getmtime(os.path.join(path, "advancements")), "meta", "run ended"),
		])
		self.stats.injest(os.path.join(path, "stats"))
		self.advancements.injest(os.path.join(path, "advancements"))

	def stop(self):
		if not self.file_watchdog == None:
			self.file_watchdog.stop()
			self.file_watchdog.join()
		self.stats.stop()
		self.advancements.stop()

		self.loaded = False
		self.active = False
