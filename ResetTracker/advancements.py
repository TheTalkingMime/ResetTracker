from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import json

from sheet import trackables

checks = trackables["advancements"]


class Advancements(FileSystemEventHandler):
	def __init__(self, callback):
		self.callback = callback

		self.file_watchdog = None

	def on_modified(self, event):
		if event.is_directory:
			return
		output = {}
		with open(event.src_path) as f:
			advancements = json.load(f)
			for advancement_id, name in checks.items():
				advancement = advancements.get(advancement_id, None)
				if advancement == None or not advancement["done"]:
					continue
				output[name] = int(datetime.strptime(next(iter(advancement["criteria"].values()))[
				                   0:19], "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
		self.callback(output)

	def set_path(self, path):
		self.file_watchdog = Observer()
		self.file_watchdog.schedule(self, path, recursive=False)
		self.file_watchdog.start()

	def stop(self):
		if not self.file_watchdog == None:
			self.file_watchdog.stop()
			self.file_watchdog.join()
