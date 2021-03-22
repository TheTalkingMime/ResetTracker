import sys
import getopt

from saves import Saves
from options import Options
from sheet import get_client, create_sheet

if __name__ == '__main__':
	# options:
	# -h --help
	# -v --version
	#
	# -w --world folder_location
	# -s --sheet sheet_location
	# -c --credentials credential_file
	#
	# -o --options (option_file)
	#
	# -b --background
	# -p --prompt
	# -m --multiple
	# -n --no-save
	# -i --ingest
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hvw:s:c:obpmni", [
		                           "help", "version", "world=", "sheet=", "credentials=", "options", "background", "prompt", "multiple", "no-save", "ingest"])
	except getopt.GetoptError:
		print('error getting options')
		sys.exit(2)

	options = Options(opts)
	
	client = get_client(options.get_credentials())
	
	sheets = [create_sheet(sheet, client) for sheet in options.get_sheets()]

	def update_values(folder_id, world_id, values):
		for sheet in sheets:
			try:
				sheet.update_values(folder_id, world_id, values)
			except:
				pass

	worlds = [ Saves(world, update_values, options.get_injest()) for world in options.get_worlds() ]

	if options.get_prompt():
		import atexit
		for world in worlds:
			atexit.register(world.stop)
		for sheet in sheets:
			atexit.register(sheet.stop)
	else:
		user_input = None
		print("type q to exit:")
		while not user_input == "q":
			user_input = input("> ")
			print(user_input)
		for world in worlds:
			world.stop()
		for sheet in sheets:
			sheet.stop()
