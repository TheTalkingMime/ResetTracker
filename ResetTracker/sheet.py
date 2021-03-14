import gspread
from time import time_ns
import re

trackables = {
	"misc": [
		"Session ID",
		"World ID",
		"world created",
		"world loaded",
		"run ended",
		"checking ended",
	],
	"stats": {
		"minecraft:custom": {
			"minecraft:play_one_minute": "ticks played",
			"minecraft:damage_taken": "damage taken",
			"minecraft:jump": "jump count",
			"minecraft:walk_one_cm": "walk one cm",
			"minecraft:sprint_one_cm": "sprint one cm",
			"minecraft:swim_one_cm": "swim one cm",
			"minecraft:boat_one_cm": "boat one cm",
			"minecraft:interact_with_crafting_table": "interact with crafting table",
			"minecraft:interact_with_furnace": "interact with furnace",
			"minecraft:deaths": "deaths",
			"minecraft:talked_to_villager": "trade attempts"
		},
		"minecraft:crafted": {
			"minecraft:wooden_axe": "craft wooden axe",
			"minecraft:iron_pick": "craft iron pick",
			"minecraft:furnace": "craft furnace",
			"minecraft:iron_ingot": "craft iron ingot",
		},
		"minecraft:dropped": {
			"minecraft:gold_ingot": "drop gold ingot"
		},
		"minecraft:picked_up": {
			"minecraft:blaze_rod": "pickup blaze rod",
			"minecraft:flint": "pickup flint",
			"minecraft:ender_pearl": "pickup ender pearl",
			"minecraft:gold_ingot": "pickup gold ingot",
			"minecraft:iron_ingot": "pickup iron ingot",
			"minecraft:oak_log": "pickup log",
			"minecraft:stripped_oak_log": "pickup log",
			"minecraft:spruce_log": "pickup log",
			"minecraft:stripped_spruce_log": "pickup log",
			"minecraft:birch_log": "pickup log",
			"minecraft:stripped_birch_log": "pickup log",
			"minecraft:jungle_log": "pickup log",
			"minecraft:stripped_jungle_log": "pickup log",
			"minecraft:acacia_log": "pickup log",
			"minecraft:stripped_acacia_log": "pickup log",
			"minecraft:dark_oak_log": "pickup log",
			"minecraft:stripped_dark_oak_log": "pickup log",
			"minecraft:crimson_stem": "pickup log",
			"minecraft:stripped_crimson_stem": "pickup log",
			"minecraft:warped_stem": "pickup log",
			"minecraft:stripped_warped_stem": "pickup log",
		},
		"minecraft:killed": {
			"minecraft:blaze": "killed blaze",
			"minecraft:iron_golem": "killed iron golem",
		},
		"minecraft:mined": {
			"minecraft:prismarine": "mined prismarine",
			"minecraft:iron_ore": "mined iron ore",
			"minecraft:hay_block": "mined hay block",
			"minecraft:magma_block": "mined magma block",
			"minecraft:gravel": "mined gravel",
			"minecraft:crafting_table": "mined crafting table",
		},
		"minecraft:item_used": {
			"minecraft:ender_eye": "eyes used",
			"minecraft:barrel": "barrels placed",
			"minecraft:composter": "composter placed",
		},
	},
	"advancements": {
		"minecraft:recipes/misc/charcoal": "getting wood",
		"minecraft:story/iron_tools": "iron pickaxe",
		"minecraft:story/enter_the_nether": "we need to go deeper",
		"minecraft:nether/find_bastion": "those where the days",
		"minecraft:nether/find_fortress": "a terrible fortress",
		"minecraft:recipes/decorations/ender_chest": "got ender eyes",
		"minecraft:story/follow_ender_eye": "eye spy",
		"minecraft:story/enter_the_end": "the end?",
		"minecraft:end/kill_dragon": "free the end",
	}
}

columns = list(set(trackables["misc"] + list(trackables["advancements"].values()) + [name for stat_type in trackables["stats"].values() for name in stat_type.values()]))

class Sheet:
	def __init__(self, data_saver=False):
		self.client = None
		self.worksheet = None
		self.session_id = time_ns() // 1_000_000
		self.active_world = None
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
		self.refresh_headers()

		return True

	def get_target_row(self):
		if self.target_row == None:
			self.target_row = len(self.worksheet.get("A1:A"))
		return self.target_row

	def refresh_headers(self):
		headers = self.worksheet.get("A1:" + gspread.utils.rowcol_to_a1(1, self.worksheet.col_count))

		if len(headers) == 0:
			# if we have not headers set then default to tracking everything
			self.headers = columns
			self.worksheet.add_cols(len(columns) - self.worksheet.col_count)

			# update the header with our values
			range_start = gspread.utils.rowcol_to_a1(1, 1)
			range_end = gspread.utils.rowcol_to_a1(1, len(columns) + 1)
			self.worksheet.update(range_start + ":" + range_end, [columns])
		else:
			self.headers = headers[0]

	def update_headers(self, blacklist=[]):
		refresh_headers()
		new_headers = [key for key in columns if key not in blacklist and key not in self.headers]
		self.headers += new_headers
		
		# update the header with our values
		range_start = gspread.utils.rowcol_to_a1(1, 1)
		range_end = gspread.utils.rowcol_to_a1(1, len(columns) + 1)
		self.worksheet.update(range_start + ":" + range_end, [columns])

	def refresh_row(self, world_id):
		# if we are on data saver mode push the row and update row index before clearing it
		if self.data_saver:
			self.push_row()
			self.target_row += 1
		# if we arnt on data saver mode then just clear the row
		else:
			self.target_row = None
		self.row = [None] * len(columns)
		self.row[0] = self.session_id
		self.row[1] = world_id
		self.active_world = world_id
	
	def push_row(self):
		target_row = self.get_target_row()
		range_start = gspread.utils.rowcol_to_a1(target_row, 1)
		range_end = gspread.utils.rowcol_to_a1(target_row, len(self.row) + 1)
		self.worksheet.update(range_start + ":" + range_end, [self.row])

	def update_values(self, world_id, values):
		if not world_id == self.active_world:
			self.refresh_row(world_id)
			self.worksheet.append_row(self.row)
		
		for name, value in values.items():
			try:
				self.row[self.headers.index(name)] = value
			except:
				pass

		if not self.data_saver:
			self.push_row()
