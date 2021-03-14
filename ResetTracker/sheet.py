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
			"minecraft:sprint_one_cm": "sprint one cm",
			"minecraft:boat_one_cm": "boat one cm",
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
			"minecraft.ender_pearl": "pickup ender pearl",
			"minecraft.gold_ingot": "pickup gold ingot",
			"minecraft.iron_ingot": "pickup iron ingot",
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
			"minecraft:gravel": "mined gravel"
		},
		"minecraft:item_used": {
			"minecraft:minecraft:ender_eye": "eyes used",
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

columns = trackables["misc"] + list(trackables["advancements"].values()) + [
    name for stat_type in trackables["stats"].values() for name in stat_type.values()]


class Sheet:
	def __init__(self, data_saver=False):
		self.client = None
		self.worksheet = None
		self.session_id = time_ns() // 1_000_000
		self.active_world = None
		self.target_row = None

		self.data_saver = data_saver

	def refresh_row(self, world_id):
		self.row = [None] * len(columns)
		self.row[0] = self.session_id
		self.row[1] = world_id
		self.active_world = world_id

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


		self.worksheet.add_cols(len(columns) - self.worksheet.col_count)

		# update the header with our values
		range_start = gspread.utils.rowcol_to_a1(1, 1)
		range_end = gspread.utils.rowcol_to_a1(1, len(columns) + 1)
		self.worksheet.update(range_start + ":" + range_end, [columns])
		return True

	def get_target_row(self):
		if self.target_row == None:
			self.target_row = len(self.worksheet.get("A1:A"))
		return self.target_row
	
	def push_row(self):
		target_row = self.get_target_row()
		range_start = gspread.utils.rowcol_to_a1(target_row, 1)
		range_end = gspread.utils.rowcol_to_a1(target_row, len(self.row) + 1)
		self.worksheet.update(range_start + ":" + range_end, [self.row])

	def update_values(self, world_id, values):
		if not world_id == self.active_world:
			if self.data_saver:
				self.push_row()
				self.target_row += 1
			else:
				self.target_row = None
			self.refresh_row(world_id)
			self.worksheet.append_row(self.row)
		for name, value in values.items():
			self.row[columns.index(name)] = value
		
		if not self.data_saver:
			self.push_row()
