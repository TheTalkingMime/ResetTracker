from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json

from sheet import trackables

checks = trackables["stats"]


class Stats(FileSystemEventHandler):
	def __init__(self, callback):
		self.callback = callback

		self.file_watchdog = None

	# read the file when it changes
	def on_modified(self, event):
		if event.is_directory:
			return
		output = {}
		with open(event.src_path) as f:
			# map though all of the stats that we are tracking and at them to an output array
			stats = json.load(f)["stats"]
			for stat_type, values in checks.items():
				for namespace_id, name in values.items():
					value = stats.get(stat_type, {}).get(namespace_id, None)
					if not value == None:
						output[name] = value
		# send the output back up to be prossesed
		self.callback(output)

	def set_path(self, path):
		self.file_watchdog = Observer()
		self.file_watchdog.schedule(self, path, recursive=False)
		self.file_watchdog.start()

	def stop(self):
		if not self.file_watchdog == None:
			self.file_watchdog.stop()
			self.file_watchdog.join()
