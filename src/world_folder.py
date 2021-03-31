import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from time import time_ns
from os import scandir

from world import World
from repeated_timer import RepeatedTimer
from window import get_window_name
from tracking import Parsed_Value

class World_Folder(FileSystemEventHandler):
	folder_id = -1
	@staticmethod
	def get_folder_id():
		World_Folder.folder_id += 1
		return World_Folder.folder_id

	def __init__(self, path, callback, injest):
		# normalize the file path
		print("world folder added: " + path)
		self.path = path

		self.folder_id = World_Folder.get_folder_id()

		# callback for all of the values
		self.callback = callback

		# this is our world file instance
		self.world = World(self.update_values)

		if injest:
			self.world_id = 0
			self.active_run = True
			self.loading_world = True
			for world in scandir(self.path):
				self.world.injest_world(world)
				self.world_id += 1
		else:
			# id for the active world
			self.world_id = -1
			self.last_world_path = ""

			# start watchdog for new minecraft worlds
			self.saves_watchdog = Observer()
			self.saves_watchdog.schedule(self, self.path, recursive=False)
			self.saves_watchdog.start()

			# listener for window title change
			self.window_title = None
			self.window_listener = RepeatedTimer(0.1, self.window_title_listener)

			# valuse for game state
			self.active_run = False
			self.loading_world = False
			self.active_window = False
			self.checking = False

	# function that gets run on a new world files being made
	def on_created(self, event):
		if not event.is_directory:
			return
		if self.last_world_path == event.src_path or sys.platform.startswith("win32"):
			try:
				self.world.set_world(event.src_path)
				self.world_id += 1
				self.loading_world = True
				self.update_values([Parsed_Value(time_ns() // 1000000, "meta", "world created")])
			except:
				pass
		else:
			self.last_world_path = event.src_path

	# function that gets run every second to get the active window title
	def window_title_listener(self):
		title = get_window_name()
		# make sure that the window that we are looking at is minecraft
		if not title.startswith("Minecraft* "):
			return
		# we only care about when the title changes
		if not title == self.window_title:
			self.window_title = title
			# call the title change listener
			self.on_title_change(self.window_title)

	# function that gets an when the title changes
	def on_title_change(self, title):
		# see if we are in single player and if thats a new thing
		if title.endswith("Singleplayer") and not self.active_window:
			self.set_active_window(True)
		# if we arnt in single player and thats a new thing we are in lan or the home menu
		elif not title.endswith("Singleplayer") and self.active_window:
			self.set_active_window(False)

		if title.endswith("Multiplayer (LAN)") and not self.checking:
			self.set_checking(True)
		elif not title.endswith("Multiplayer (LAN)") and self.checking:
			self.set_checking(False)

	# function for manageing the active window state along with world loading
	def set_active_window(self, active):
		self.active_window = active
		# if we are loading a world and the window is active then we arnt loading the world anymore
		if self.loading_world and self.active_window:
			self.loading_world = False
			self.set_active_run(True)
		# if we arnt loading a world and the window is not active then we are no longer in single player
		elif not self.loading_world and not self.active_window:
			self.update_values([Parsed_Value(time_ns() // 1000000, "meta", "run ended")])
			self.set_active_run(False)

	def set_checking(self, checking):
		if self.checking and not checking:
			self.update_values([Parsed_Value(time_ns() // 1000000, "meta", "checking ended")], force=True)
		self.checking = checking

	# function for setting if our run is active and stopping the watchdogs if it isnt
	def set_active_run(self, active):
		self.active_run = active
		# close the world listeners if the run is no longer active
		if not self.active_run:
			self.world.stop()

	# callback for our world to pass values back up to us
	def update_values(self, values, force=False):
		if not self.loading_world and not self.active_run and not force:
			return
		self.callback(self.folder_id, self.world_id, values)

	def stop(self):
		print("closing")
		self.window_listener.stop()
		self.saves_watchdog.stop()
		self.saves_watchdog.join()
		self.world.stop()
