from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import json

from tracking import Advancement

class Advancements(FileSystemEventHandler):
	def __init__(self, callback):
		self.callback = callback

		self.file_watchdog = None

	def on_modified(self, event):
		if event.is_directory:
			return
		with open(event.src_path) as f:
			advancements = Advancement.parse_advancements(json.load(f))
		self.callback(advancements)

	def set_path(self, path):
		self.file_watchdog = Observer()
		self.file_watchdog.schedule(self, path, recursive=False)
		self.file_watchdog.start()

	def stop(self):
		if not self.file_watchdog == None:
			self.file_watchdog.stop()
			self.file_watchdog.join()
