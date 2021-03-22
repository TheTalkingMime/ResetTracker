import sys
import pathlib
import json
import time

from sheet import is_google_sheet, get_credentials

help_str = "\
Help:\n\n\
-h --help\tprint out this menu\n\
-v --version\tget the build version\n\
-w --worlds\tset the directory for your .minecraft/saves folder\n\
-c --credentials\tset the file that your credentials are located in\n\
-s --sheet\tset the url for your spreadsheet\n\
-o --options\tset the file that options are going to be save in\n\
-n --no-save\tflag to not save settings in options\n\
"

local_path = pathlib.Path(__file__).parent.parent

def prompt_user(prompt, result_filter, pre_processes, exit_condition, multiple):
	accumulator = []
	while True:
		last = input("> ")
		if exit_condition(last):
			return accumulator
		last = pre_processes(last)
		if result_filter(last):
			accumulator.append(last)
			if not multiple:
				return accumulator
		else:
			print("invalid input")

class Options:
	def __init__(self, opts):
		# saved values
		self.filename = None
		self.worlds = []
		self.sheets = []
		self.credentials = None
		self.options = {}

		# options that modify how the code is going to run
		self.no_save = False
		self.injest = False

		# option that modifies how defaul values are handeled
		self.prompt = None
		multiple = False

		# load in command line args
		for opt, arg in opts:
			if opt in ("-h", "--help"):
				print(help_str)
				sys.exit(0)
			elif opt in ("-v", "--version"):
				print("0.1.0")
				sys.exit(0)
			elif opt in ("-w", "--world"):
				self.add_world_folder(arg)
			elif opt in ("-c", "--credentials"):
				self.set_credentials(arg)
			elif opt in ("-s", "--sheet"):
				self.add_sheet(arg)
			elif opt in ("-o", "--options"):
				self.filename = arg
			elif opt in ("-b", "--background"):
				if self.prompt == True:
					print("Error: can not specify both background and prompt options")
					sys.exit(2)
				self.prompt = False
			elif opt in ("-p", "--prompt"):
				if self.prompt == False:
					print("Error: can not specify both background and prompt options")
					sys.exit(2)
				self.prompt = True
			elif opt in ("-m", "--multiple"):
				multiple = True
			elif opt in ("-n", "--no-save"):
				self.no_save = True
			elif opt in ("-i", "--ingest"):
				self.injest = True

		# get where the options file should be located at
		# if we have no file name then its just the default file path
		if self.filename == None:
			self.filename = local_path.joinpath("default_options.json").absolute()
		# convert the file name to a file object
		elif not self.filename == "":
			self.filename = pathlib.Path(self.filename)

		# read the options file if we can
		try:
			with self.filename.open("r") as f:
				file_json = json.load(f)
		except:
			file_json = {}

		# merge the options file data with the command line data
		for key, value in file_json.items():
			if key == "worlds":
				for world in value:
					self.add_world_folder(world)
			elif key == "sheets":
				for sheet in value:
					self.add_sheet(sheet)
			elif key == "credentials":
				self.set_credentials(value)

		# if we dont have a worlds folder then try and get the default one
		if len(self.worlds) == 0 and not self.prompt:
			if sys.platform.startswith("win32"):
				default_world_folder = pathlib.Path.home().joinpath("Appdata/.minecraft/saves")
			elif sys.platform.startswith("linux"):
				default_world_folder = pathlib.Path.home().joinpath(".minecraft/saves")
			elif sys.platform.startswith("darwin"):
				default_world_folder = pathlib.Path.home().joinpath(
					"Library/Application Support/minecraft/saves")

			if default_world_folder.exists():
				self.add_world_folder(default_world_folder)

		# if we still havent found a worlds folder or we are prompting for them ask the user where the worlds folders are
		if (self.prompt == None and len(self.worlds) == 0) or self.prompt:
			worlds = self.prompt_user("Please enter each of the save folders you would like to read from. (press enter when you are done)",
			                           lambda file: file.exists(), lambda file: pathlib.Path(file).expanduser(), lambda arg: arg == "", multiple)
			for world in worlds:
				self.add_world_folder(world)

		if len(self.worlds) == 0:
			print("WARNING: no valid world folders specified")

		if (self.prompt == None and len(self.sheets) == 0) or self.prompt:
			sheets = self.prompt_user("Please enter the url or file path to the spreadsheets you would like to write to. (press enter when you are done)",
			                           lambda uri: is_google_sheet(uri) or pathlib.Path(uri).exists(), lambda arg: arg, lambda arg: arg == "", multiple)
			for sheet in sheets:
				self.add_sheet(sheet)

		if len(self.sheets) == 0:
			print("WARNING: no valid sheets specified")

		if any(is_google_sheet(sheet) for sheet in self.sheets):
			if self.credentials == None or self.prompt:
				self.set_credentials(get_credentials(self.sheets, not self.prompt == False))
			if self.credentials == None:
				print("ERROR: no valid credentials specified")

		self.save()

	def add_world_folder(self, filename):
		file = pathlib.Path(filename)
		if not file.exists():
			return
		if file.parts[-1] == "saves":
			self.worlds.append(filename)
		else:
			self.worlds.append(file.joinpath("saves/").absolute().as_posix())

	def add_sheet(self, sheet):
		file = pathlib.Path(sheet)
		if not file.exists() and not is_google_sheet(sheet):
			return
		self.sheets.append(sheet)

	def set_credentials(self, credential):
		if not self.credentials == None:
			print("WARNING: two sheets credential provided")
		self.credentials = credential

	def get_worlds(self):
		return self.worlds

	def get_sheets(self):
		return self.sheets

	def get_credentials(self):
		return self.credentials

	def get_injest(self):
		return self.injest

	def get_prompt(self):
		return self.prompt

	def save(self):
		if self.no_save or self.filename == "":
			return
		obj = {
			"worlds": self.worlds,
			"sheets": self.sheets,
			"credentials": self.credentials
		}
		with self.filename.open("w") as f:
			json.dump(obj, f)
