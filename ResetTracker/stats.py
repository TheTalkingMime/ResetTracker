from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json

from tracking import Stat

class Stats(FileSystemEventHandler):
	def __init__(self, callback):
		self.callback = callback

		self.file_watchdog = None

	# read the file when it changes
	def on_modified(self, event):
		if event.is_directory:
			return
		try:
			with open(event.src_path) as f:
				# map though all of the stats that we are tracking and at them to an output array
				json_data = json.load(f)
		except:
			print("error test stats")
			return
		# send the output back up to be prossesed
		stats = Stat.parse_stats(json_data["stats"])
		self.callback(stats)
		
	def set_path(self, path):
		self.file_watchdog = Observer()
		self.file_watchdog.schedule(self, path, recursive=False)
		self.file_watchdog.start()

	def stop(self):
		if not self.file_watchdog == None:
			self.file_watchdog.stop()
			self.file_watchdog.join()
