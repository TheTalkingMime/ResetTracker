import sys
import pathlib
import json
from time import sleep
from pathlib import Path

from sheet import Sheet
from world_folder import World_Folder

# help_str = "\
# Help:
# -h --help\tprint out this menu
# -v --version\tget the build version
# -w --worlds\tset the directory for your .minecraft/saves folder
# -c --credentials\tset the file that your credentials are located in
# -s --sheet\tset the url for your spreadsheet
# -o --options\tset the file that options are going to be save in
# -n --no-save\tflag to not save settings in options
# "

help_str = "\
Help:\n\n\
-h --help\tprint out this menu\n\
-v --version\tget the build version\n\
\
-w --world folder_location\tset the directory for your .minecraft/saves folder\n\
-s --sheet sheet_location\tset the url for your spreadsheet\n\
-c --credentials credential_file\tset the file that your credentials are located in\n\
\
-o --options (option_file)\tset the file that options are going to be save in. Not specifying a file will result in no file being made\n\
\
-b --background\trun without prompting for user input\n\
-p --prompt\tforce prompts on all locations\n\
-m --multiple\tmake prompts take multiple values\n\
-n --no-save\tdont save new values to options file\n\
-i --ingest\tflag to set mode to world injest\n\
"

version_str = "1.0.1"

local_path = pathlib.Path.cwd()

class Options:

	def __init__(self, opts):
		# the file that this data is saved/loaded from
		self.options_file = None

		# do we want to save the options
		self.no_save = False

		# worlds folders we are loading saves from
		self.worlds = []
		# spreadsheets we are saving to
		self.sheets = []

		# do we want to injest all of the world files
		self.injest = False
		
		# credentials to access google sheet
		self.credentials = None

		# do we want to prompt the user for things
		self.prompt = None
		self.multiple = None

		# load in command line args
		for opt, arg in opts:
			if opt in ("-h", "--help"):
				print(help_str)
				sys.exit(0)
			elif opt in ("-v", "--version"):
				print(version_str)
				sys.exit(0)
			elif opt in ("-w", "--world"):
				self.add_world(arg)
			elif opt in ("-c", "--credentials"):
				self.set_credentials(arg)
			elif opt in ("-s", "--sheet"):
				self.add_sheet(arg)
			elif opt in ("-o", "--options"):
				self.options_file = arg
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
				self.multiple = True
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
		
		# try and read in the options file
		try:
			with self.filename.open("r") as f:
				file_json = json.load(f)
		except:
			file_json = {}
		
		# merge the options file data with the command line data
		for key, value in file_json.items():
			if key == "worlds":
				for world in value:
					self.add_world(world)
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
		
		# TODO: ask for world folder
		

		# warn the user if they dont have any worlds
		if len(self.worlds) == 0:
			print("WARNING: no valid world folders specified")

		# TODO: ask for spreadsheets

		# warn the user if they dont have any sheets
		if len(self.sheets) == 0:
			print("WARNING: no valid sheets specified")

		# TODO: if we have any google sheets check credentials things

		self.save()

	def prompt(self, query):
		# TODO: something along the lines of prompt_user
		if self.prompt == False:
			return []
		

	def add_world(self, world):
		# TODO: 
		pass

	def get_worlds(self):
		# TODO: 
		return self.worlds

	def add_sheet(self, world):
		# TODO: 
		pass

	def get_sheets(self):
		# TODO: 
		return self.sheets

	def set_credentials(self, credentials, force=False):
		# TODO: 
		pass

	def get_credentials(self):
		return self.credentials

	def get_injest(self):
		return self.injest


# def prompt_user(prompt, result_filter, pre_processes, exit_condition, multiple):
# 	accumulator = []
# 	print(prompt)
# 	while True:
# 		last = input("> ")
# 		if exit_condition(last):
# 			return accumulator
# 		last = pre_processes(last)
# 		if result_filter(last):
# 			accumulator.append(last)
# 			if not multiple:
# 				return accumulator
# 		else:
# 			print("invalid input")

# def get_client(sheets, prompt):
# 	default_location = local_path.joinpath("credentials.json").absolute()
# 	print("Credentials not found. please move credentials to exactly \"" + default_location.as_posix() +
# 	      "\" and press enter, or type in the path that the credentials file is located at.")
# 	while True:
# 		if prompt:
# 			file = input("> ")
# 			if file == "":
# 				path = default_location
# 		else:
# 			path = default_location
# 			sleep(5)
		
# 		file = Path(file)
# 		file = file.expanduser()

# 		if not file.exists():
# 			continue

# 		client = Sheet.get_credentials(file.as_posix())

# 		if client == False:
# 			print("could not load credentials from that file. Please try it again")
# 			continue
# 		if not all(Sheet.sheet_access(sheet, client) for sheet in sheets):
# 			with file.open("r") as f:
# 				client_email = json.load(f)["client_email"]
# 				print("target credentials couldnt access all target sheets. Please make sure all sheets are shared with " + client_email)
# 			continue

# 		return client

# class Options:
# 	def __init__(self, opts):
# 		# saved values
# 		self.filename = None
# 		self.worlds = []
# 		self.sheets = []
# 		self.client = None
# 		self.options = {}

# 		# options that modify how the code is going to run
# 		self.no_save = False
# 		self.injest = False

# 		# option that modifies how defaul values are handeled
# 		self.prompt = None
# 		multiple = False

# 		# load in command line args
# 		for opt, arg in opts:
# 			if opt in ("-h", "--help"):
# 				print(help_str)
# 				sys.exit(0)
# 			elif opt in ("-v", "--version"):
# 				print(version_str)
# 				sys.exit(0)
# 			elif opt in ("-w", "--world"):
# 				self.add_world_folder(arg)
# 			elif opt in ("-c", "--credentials"):
# 				self.set_client(arg)
# 			elif opt in ("-s", "--sheet"):
# 				self.add_sheet(arg)
# 			elif opt in ("-o", "--options"):
# 				self.filename = arg
# 			elif opt in ("-b", "--background"):
# 				if self.prompt == True:
# 					print("Error: can not specify both background and prompt options")
# 					sys.exit(2)
# 				self.prompt = False
# 			elif opt in ("-p", "--prompt"):
# 				if self.prompt == False:
# 					print("Error: can not specify both background and prompt options")
# 					sys.exit(2)
# 				self.prompt = True
# 			elif opt in ("-m", "--multiple"):
# 				multiple = True
# 			elif opt in ("-n", "--no-save"):
# 				self.no_save = True
# 			elif opt in ("-i", "--ingest"):
# 				self.injest = True

# 		# get where the options file should be located at
# 		# if we have no file name then its just the default file path
# 		if self.filename == None:
# 			self.filename = local_path.joinpath("default_options.json").absolute()
# 		# convert the file name to a file object
# 		elif not self.filename == "":
# 			self.filename = pathlib.Path(self.filename)

# 		# read the options file if we can
# 		try:
# 			with self.filename.open("r") as f:
# 				file_json = json.load(f)
# 		except:
# 			file_json = {}

# 		# merge the options file data with the command line data
# 		for key, value in file_json.items():
# 			if key == "worlds":
# 				for world in value:
# 					self.add_world_folder(world)
# 			elif key == "sheets":
# 				for sheet in value:
# 					self.add_sheet(sheet)
# 			elif key == "credentials":
# 				self.set_client(value)

# 		# if we dont have a worlds folder then try and get the default one
# 		if len(self.worlds) == 0 and not self.prompt:
# 			if sys.platform.startswith("win32"):
# 				default_world_folder = pathlib.Path.home().joinpath("Appdata/.minecraft/saves")
# 			elif sys.platform.startswith("linux"):
# 				default_world_folder = pathlib.Path.home().joinpath(".minecraft/saves")
# 			elif sys.platform.startswith("darwin"):
# 				default_world_folder = pathlib.Path.home().joinpath(
# 					"Library/Application Support/minecraft/saves")

# 			if default_world_folder.exists():
# 				self.add_world_folder(default_world_folder)

# 		# if we still havent found a worlds folder or we are prompting for them ask the user where the worlds folders are
# 		if (self.prompt == None and len(self.worlds) == 0) or self.prompt:
# 			worlds = prompt_user("Please enter each of the save folders you would like to read from." + " (press enter when you are done)" if multiple else "",
#                             World_Folder.valid_folder, lambda file: pathlib.Path(file).expanduser(), lambda arg: arg == "", multiple)
# 			for world in worlds:
# 				self.add_world_folder(world)

# 		if len(self.worlds) == 0:
# 			print("WARNING: no valid world folders specified")

# 		if (self.prompt == None and len(self.sheets) == 0) or self.prompt:
# 			sheets = prompt_user("Please enter the url or file path to the spreadsheet you would like to write to." + " (press enter when you are done)" if multiple else "",
#                             lambda uri: Sheet.valid_sheet(uri), lambda arg: arg, lambda arg: arg == "", multiple)
# 			for sheet in sheets:
# 				self.add_sheet(sheet)

# 		if len(self.sheets) == 0:
# 			print("WARNING: no valid sheets specified")

# 		google_sheets = [sheet for sheet in self.sheets if Sheet.is_google_sheet(sheet)]
# 		if not len(google_sheets) == 0:
# 			if self.client == None or self.prompt:
# 				self.set_client(get_client(google_sheets, not self.prompt == False))
# 			if self.client == None:
# 				print("ERROR: no valid credentials specified")
# 				sys.exit(2)
		
# 		if self.client == None:
# 			default_location = local_path.joinpath("credentials.json").absolute()
# 			while self.client == None:
# 				if self.prompt:
# 					file = input("> ")
# 				else:
# 					sleep(1)

# 				if file == "":
# 					pass

# 		self.save()

# 	def add_world_folder(self, filename):
# 		file = pathlib.Path(filename)
# 		if not file.exists():
# 			return
# 		if file.parts[-1] == "saves":
# 			self.worlds.append(filename)
# 		else:
# 			self.worlds.append(file.joinpath("saves/").absolute().as_posix())

# 	def add_sheet(self, sheet):
# 		if not Sheet.is_google_sheet(sheet) and not pathlib.Path(sheet).exists():
# 			return
# 		self.sheets.append(sheet)

# 	def set_client(self, credential):
# 		if not self.client == None:
# 			print("WARNING: two sheet credential provided defaulting to second one")
# 		self.client = credential

# 	def check_credentials(self):
# 		google_sheets = [
# 				sheet for sheet in self.sheets if Sheet.is_google_sheet(sheet)]
# 		if not len(google_sheets) == 0:
# 			if self.client == None or self.prompt:
# 				pass
# 		pass

# 	def get_worlds(self):
# 		return self.worlds

# 	def get_sheets(self):
# 		return self.sheets

# 	def get_client(self):
# 		return self.client

# 	def get_injest(self):
# 		return self.injest

# 	def get_prompt(self):
# 		return self.prompt

# 	def save(self):
# 		if self.no_save or self.filename == "":
# 			return
# 		obj = {
# 			"worlds": self.worlds,
# 			"sheets": self.sheets,
# 			"credentials": self.client
# 		}
# 		with self.filename.open("w") as f:
# 			json.dump(obj, f)
