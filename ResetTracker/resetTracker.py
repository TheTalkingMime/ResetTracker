import sys
import getopt
import pathlib
import json
import time

from saves import valid_minecraft_folder, Saves
from sheet import Sheet

help_str = "\
Help:\n\n\
-h --help\tprint out this menu\n\
-w --worlds\tset the directory for your .minecraft/saves folder\n\
-c --credentials\tset the file that your credentials are located in\n\
-s --sheet\tset the url for your spreadsheet\n\
-o --options\tset the file that options are going to be save in\n\
-n --no-save\tflag to not save settings in options\n\
"


# option file manager
class Options:
	def __init__(self, file, no_save):
		self.file = file
		self.no_save = no_save
		try:
			with self.file.open("r") as f:
				self.values = json.load(f)
		except:
			self.values = {}

	def has(self, opt):
		return opt in self.values and not self.get(opt) == None

	def get(self, opt):
		return self.values.get(opt) if not self.values.get(opt) == "" else None

	def set(self, opt, value):
		self.values[opt] = value
		if not self.no_save:
			with self.file.open("w") as f:
				f.write(json.dumps(self.values))
		return value


if __name__ == '__main__':
	# options:
	# -h --help
	# -w --worlds
	# -c --credentials
	# -s --sheet
	# -o --options
	# -n --no-save
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hbw:c:s:o:n", [
		                           "help", "background", "worlds=", "credentials=", "sheet=", "options:", "no-save"])
	except getopt.GetoptError:
		sys.exit(2)
		print('error getting options')

	local_path = pathlib.Path(__file__).parent.parent

	options_file = None
	world_folder = None
	credentials_file = None
	sheet_link = None
	no_save = False
	background = False

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print(help_str)
			sys.exit(0)
		if opt in ("-b", "--background"):
			background = True
		if opt in ("-o", "--options"):
			options_file = pathlib.Path(arg)
		if opt in ("-w", "--worlds"):
			world_folder = pathlib.Path(arg)
		if opt in ("-c", "--credentials"):
			credentials_file = pathlib.Path(arg)
		if opt in ("-s", "--sheet"):
			sheet_link = arg
		if opt in ("-n", "--no-save"):
			no_save = True

	# get out options file
	if options_file == None:
		options_file = local_path.joinpath("defualt_options.json").absolute()
	else:
		if not options_file.exists():
			print("specified options folder does not exists!")
			sys.exit(2)

	options = Options(options_file, no_save)

	# if we dont have a world folder set see if we can load it from the options file, if that doesnt work then try the default, if that doenst work ask the user
	if world_folder == None:
		# see if we have a saved world_folder
		if options.has("world_folder"):
			world_folder = pathlib.Path(options.get("world_folder"))
		# try the default .minecraft locaton
		else:
			# get the default .minecraft folder for all othe the different operating systems
			if sys.platform.startswith("win32"):
				world_folder = pathlib.Path.home().joinpath("Appdata/.minecraft")
			elif sys.platform.startswith("linux"):
				world_folder = pathlib.Path.home().joinpath(".minecraft")
			elif sys.platform.startswith("darwin"):
				world_folder = pathlib.Path.home().joinpath(
					"Library/Application Support/minecraft")

		# ask the user for the file path as a last restort
		while world_folder == None or not world_folder.exists() or not valid_minecraft_folder(world_folder):
			if(background):
				print("no saves folder specified for background process")
				sys.exit(2)
			world_folder = pathlib.Path(
				input("saves folder not found please input saves folder location:\n> "))
			world_folder = world_folder.expanduser()
		# save the path in the options file
		options.set("world_folder", world_folder.absolute().as_posix())
	else:
		if not world_folder.exists() or valid_minecraft_folder(world_folder):
			print("specified saves folder does not exist!")
			sys.exit(2)

	sheet = Sheet()

	if credentials_file == None or not credentials_file.exists() or not sheet.load_credentials(credentials_file):
		# see if we have a saved credentials file
		if options.has("credentials_file"):
			credentials_file = pathlib.Path(options.get("credentials_file"))

		# wait for the file to show up or ask the user for the path
		while credentials_file == None or not credentials_file.exists() or not sheet.load_credentials(credentials_file):
			if(background):
				path = local_path.joinpath("credentials.json")
				print("credentials file not found. Trying again in 5 seconds")
				time.sleep(5)
			else:
				path = input("Credentials not found. please move credentials to exactly \"" + local_path.joinpath("credentials.json")
			             .absolute().as_posix() + "\" and press enter, or type in the path that the credentials file is located at.\n> ")
			if path == "":
				path = local_path.joinpath("credentials.json").absolute()
			credentials_file = pathlib.Path(path)
			credentials_file = credentials_file.expanduser()

		# save the credentials_file location
		options.set("credentials_file", credentials_file.absolute().as_posix())
	else:
		if not credentials_file.exists() and not sheet.load_credentials(credentials_file):
			print("specified credentials file does not exist!")
			sys.exit(2)

	with credentials_file.open("r") as f:
		client_email = json.load(f)["client_email"]

	if sheet_link == None:
		# see if we have a saved sheet
		if options.has("sheet"):
			sheet_link = options.get("sheet")
		# ask the user for the sheet as a last restort
		while sheet_link == None or not sheet.set_sheet(sheet_link):
			if(background):
				print("no sheet specified for background process")
				sys.exit(2)
			sheet_link = options.set("sheet", input(
				"what is the sheet that will be used for the calcualtions:\t(Make sure your sheet is shared with \"" + client_email + "\")\n> "))
	else:
		if not sheet.set_sheet(sheet_link):
			print("no access to target spreadsheet!")
			sys.exit(2)

	saves = Saves(world_folder, sheet.update_values)

	if background:
		import atexit
		atexit.register(saves.stop)
	else:
		user_input = None
		print("type q to exit:")
		while not user_input == "q":
			user_input = input("> ")
			print(user_input)
		saves.stop()
