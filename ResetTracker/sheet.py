import gspread
from time import time_ns
import re

from tracking import Group

header_aliases = {
	"Session ID": "session id",
	"World ID": "world id",
	"ticks played": "igt",
	"sprint one cm": "distance sprinted",
	"drop gold ingot": "gold dropped",
	"pickup blaze rod": "rods collected",
	"pickup flint": "flint collected",
	"pickup ender pearl": "pearls collected",
	"pickup gold ingot": "gold collected",
	"pickup iron ingot": "iron collected",
	"killed blaze": "blaze killed",
	"killed iron golem": "iron golem killed",
	"mined iron ore": "iron ore mined",
	"mined magma block": "magma block mined",
	"mined gravel": "gravel mined",
	
	"Wood": "getting wood",
	"Iron Pickaxe": "iron pickaxe",
	"Nether": "we need to go deeper",
	"Bastions": "those where the days",
	"Fortress": "a terrible fortress",
	"Nether Exit": "got ender eyes",
	"Stronghold": "eye spy",
	"End": "the end?",
	"IGT": "igt",
	"Gold Dropped": "gold dropped",
	"Blaze Rods": "rods collected",
	"Blazes": "blaze killed",
	"Dmg Taken": "damage taken",
	"Sprint Dist": "distance sprinted",
	"Flint": "flint collected",
	"Gravel": "gravel mined",
	"Prismarine": "mined prismarine",
	"Furnace": "furnace placed",
	"Iron Mined": "iron ore mined",
	"Hay Mined": "mined hay block",
	"IGs Killed": "iron golem killed",
	"Magma Block": "magma block mined",
}

class Sheet:
	def __init__(self, data_saver=False):
		self.client = None
		self.worksheet = None
		self.session_id = time_ns() // 1_000_000
		self.world_id = None
		self.target_row = None

		self.data_saver = data_saver
		self.headers = None

	def load_credentials(self, file):
		try:
			self.client = gspread.service_account(filename=file)
			return True
		except:
			return False

	def set_sheet(self, sheet_link):
		try:
			# see if we have access to the listed sheet
			sheet = self.client.open_by_url(sheet_link)
		except:
			return False
		# get the worksheet
		self.worksheet = sheet.worksheet("Raw Data")

		# get the headers
		self.organize_headers()
		
		return True

	def get_target_row(self):
		if self.target_row == None:
			self.target_row = len(self.worksheet.get("A1:A"))
		return self.target_row

	def organize_headers(self):
		# get all of our headers that we want in line
		self.refresh_headers()
		current_headers = [ header if not header in header_aliases else header_aliases[header] for header in self.headers ]
		group_headers = [ item.name for group in Group.groups for item in group.get_items() ]

		# get a list of what the new headers are going to be
		all_headers = list(dict.fromkeys(current_headers + group_headers))

		# make sure we have space for all of the headers
		missing_col = len(all_headers) - self.worksheet.col_count
		self.worksheet.add_cols(missing_col)

		# get the current data from the spreadsheet
		current_data = self.worksheet.batch_get([ gspread.utils.rowcol_to_a1(3, i) + ":" + gspread.utils.rowcol_to_a1(3, i)[:-1] for i in range(1, len(all_headers) + 1)])
		def parse_value(value):
			if len(value) == 0:
				return []
			else:
				try:
					return [float(value[0])]
				except:
					return value

		current_data = [[ parse_value(row) for row in column ] + [[""]] * (len(current_data[0]) - len(column)) for column in current_data ]
		group_names = [ group.name for group in Group.groups ]

		# sort our headers into our groups
		groups = [[] for i in range(len(group_names))]
		no_group = []
		for index, header in enumerate(all_headers):
			if header in group_headers:
				groups[group_names.index(Group.find_host_group(header))].append((header, index))
			else:
				no_group.append((header, index))

		# orginize our groups to match the order items where defined in
		for index, group in enumerate(groups):
			def get_group_order(e):
				g = Group.groups[index]
				for i, item in enumerate(g.get_items()):
					if e[0] == item.name:
						return i
				return 0

			group = group.sort(key=get_group_order)

		# get our data for each column
		remapped_data = [item for group in groups for item in group] + no_group
		remapped_data = [[[header], ["-"]] + current_data[index] for header, index in remapped_data ]

		# remap all the data with our new headers
		self.worksheet.batch_update([ {
			"range": gspread.utils.rowcol_to_a1(1, index + 1) + ":" + gspread.utils.rowcol_to_a1(1, index + 1)[:-1],
			"values": column
		} for index, column in enumerate(remapped_data)], value_input_option="RAW")

	def refresh_headers(self):
		headers = self.worksheet.get("A1:" + gspread.utils.rowcol_to_a1(1, self.worksheet.col_count))
		try:
			self.headers = headers[0]
		except:
			self.headers = headers
		return self.headers

	def refresh_row(self, world_id):
		# if we are on data saver mode push the row and update row index before clearing it
		if self.data_saver:
			self.push_row()
			self.target_row += 1
		# if we arnt on data saver mode then just clear the row
		else:
			self.target_row = None
		self.row = [None] * len(self.headers)
		self.world_id = world_id
		self.set_row_value("session id", self.session_id)
		self.set_row_value("world id", self.world_id)

	def set_row_value(self, row_name, value):
		try:
			self.row[self.headers.index(row_name)] = value
		except:
			pass
	
	def push_row(self):
		target_row = self.get_target_row()
		range_start = gspread.utils.rowcol_to_a1(target_row, 1)
		range_end = gspread.utils.rowcol_to_a1(target_row, len(self.row) + 1)
		self.worksheet.update(range_start + ":" + range_end, [self.row])

	def update_values(self, world_id, values):
		if not world_id == self.world_id:
			self.refresh_headers()
			self.refresh_row(world_id)
			self.worksheet.append_row(self.row)

		for value in values:
			self.set_row_value(value.name, value.value)

		if not self.data_saver:
			self.push_row()
