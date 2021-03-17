from datetime import datetime

class Parsed_Value:
	def __init__(self, value, group, name):
		self.value = value
		self.group = group
		self.name = name

class Group:
	groups = []

	@staticmethod
	def get_group(name):
		for group in Group.groups:
			if group.name == name:
				return group
		return Group(name)

	@staticmethod
	def find_host_group(name):
		for group in Group.groups:
			if not group.find_item(name) == None:
				return group.name

	def __init__(self, name, first_item=None):
		self.name = name
		
		if first_item == None:
			self.items = []
		else:
			self.items = [first_item]
		
		Group.groups.append(self)

	def add(self, item):
		self.items.append(item)

	def find_item(self, name):
		for item in self.items:
			if name == item.name:
				return item

	def get_items(self):
		return self.items
	
class Trackable:
	def __init__(self, group, name, handler=None, type=0):
		self.name = name
		self.group = group
		self.handler = handler
		self.type = type

		Group.get_group(group).add(self)

	def parse(self, value):
		if self.handler == None:
			return Parsed_Value(value, self.group, self.name)
		return Parsed_Value(self.handler(value), self.group, self.name)

class Stat(Trackable):
	stats = {}

	@staticmethod
	def parse_stats(stats):
		output = []
		for stat_type, tracked_stats in Stat.stats.items():
			for namespace_id, stat in tracked_stats.items():
				value = stats.get(stat_type, {}).get(namespace_id, None)
				if not value == None:
					output.append(stat.parse(value))
		return output

	@staticmethod
	def __create_stat(stat):
		try:
			type_group = Stat.stats[stat.stat_type]
		except:
			type_group = {}
			Stat.stats[stat.stat_type] = type_group

		# TODO: error checking for defining the same value twice
		type_group[stat.namespace_id] = stat

	def __init__(self, group, name, stat_type, namespace_id, handler=None):
		super().__init__(group, name, handler=handler, type=1)
		self.stat_type = stat_type
		self.namespace_id = namespace_id
		Stat.__create_stat(self)


class Advancement(Trackable):

	groups = ["advancement"]

	@staticmethod
	def parse_advancements(advancements):
		output = []
		for group in Advancement.groups:
			for a in Group.get_group(group).get_items():
				if not a.type == 2:
					continue
				advancement = advancements.get(a.advancement_id, None)
				if not advancement == None:
					output.append(a.parse(advancement))
		return output

	def __init__(self, name, advancement_id, track_type=0, track_target=None, group="advancement"):
		super().__init__(group, name, type=2)

		if not group in Advancement.groups:
			Advancement.groups.append(group)

		self.advancement_id = advancement_id

		self.track_type = track_type
		self.track_target = track_target

	def parse(self, advancement):
		criteria = advancement["criteria"]
		done = advancement["done"]
		# TODO: something with done
		# type 0 is get the min value
		if self.track_type == 0:
			return super().parse(int(min([datetime.strptime(criterion[0:19], "%Y-%m-%d %H:%M:%S").timestamp() for criterion in list(criteria.values())]) * 1000))
		# type 1 is get the max value
		elif self.track_type == 1:
			return super().parse(int(max([datetime.strptime(criterion[0:19], "%Y-%m-%d %H:%M:%S").timestamp() for criterion in list(criteria.values())]) * 1000))
		elif self.track_type == 2:
			return super().parse(min([(criterion, datetime.strptime(value[0:19], "%Y-%m-%d %H:%M:%S").timestamp()) for criterion, value in list(criteria.items())], key=lambda x: x[1])[0])
		elif self.track_type == 3:
			return super().parse(max([(criterion, datetime.strptime(value[0:19], "%Y-%m-%d %H:%M:%S").timestamp()) for criterion, value in list(criteria.items())], key=lambda x: x[1])[0])
		elif self.track_type == 4:
			if self.track_target == None:
				raise ValueError(
					"track_target in advancement trackable not defined for type 3 track_type")
			return super().parse(int(datetime.strptime(criteria[self.track_target][0:19], "%Y-%m-%d %H:%M:%S").timestamp() * 1000))

Trackable("meta", "session id")
Trackable("meta", "world id")
Trackable("meta", "world created")
Trackable("meta", "world loaded")
Trackable("meta", "run ended")
Trackable("meta", "checking ended")

Stat("meta", "igt", "minecraft:custom", "minecraft:play_one_minute", handler=lambda ticks: ticks)

Advancement("getting wood", "minecraft:recipes/misc/charcoal")
Advancement("iron pickaxe", "minecraft:story/iron_tools")
Advancement("we need to go deeper", "minecraft:story/enter_the_nether")
Advancement("those where the days", "minecraft:nether/find_bastion")
Advancement("a terrible fortress", "minecraft:nether/find_fortress")
Advancement("got ender eyes", "minecraft:recipes/decorations/ender_chest")
Advancement("eye spy", "minecraft:story/follow_ender_eye")
Advancement("the end?", "minecraft:story/enter_the_end")

Advancement("overworld biome", "minecraft:adventure/adventuring_time", track_type=2, group="biome")
Advancement("nether biome", "minecraft:nether/explore_nether", track_type=2, group="biome")

Stat("food", "damage taken", "minecraft:custom", "minecraft:damage_taken", handler=lambda damage: damage / 10)
Stat("food", "jump count", "minecraft:custom", "minecraft:jump")
Stat("food", "distance walked", "minecraft:custom", "minecraft:walk_one_cm", handler=lambda damage: damage / 100)
Stat("food", "distance sprinted", "minecraft:custom", "minecraft:sprint_one_cm", handler=lambda damage: damage / 100)

Stat("food types", "ate enchanted golden apple", "minecraft:item_used", "minecraft:enchanted_golden_apple")
Stat("food types", "ate golden carrot", "minecraft:item_used", "minecraft:golden_carrot")
Stat("food types", "ate golden apple", "minecraft:item_used", "minecraft:golden_apple")
Stat("food types", "ate suspicious stew", "minecraft:item_used", "minecraft:suspicious_stew")
Stat("food types", "ate cooked beef", "minecraft:item_used", "minecraft:cooked_beef")
Stat("food types", "ate cooked mutton", "minecraft:item_used", "minecraft:cooked_mutton")
Stat("food types", "ate cooked porkchop", "minecraft:item_used", "minecraft:cooked_porkchop")
Stat("food types", "ate cooked salmon", "minecraft:item_used", "minecraft:cooked_salmon")
Stat("food types", "ate baked potato", "minecraft:item_used", "minecraft:baked_potato")
Stat("food types", "ate cooked cod", "minecraft:item_used", "minecraft:cooked_cod")
Stat("food types", "ate cooked chicken", "minecraft:item_used", "minecraft:cooked_chicken")
Stat("food types", "ate cooked rabbit", "minecraft:item_used", "minecraft:cooked_rabbit")
Stat("food types", "ate bread", "minecraft:item_used", "minecraft:bread")
Stat("food types", "ate carrot", "minecraft:item_used", "minecraft:carrot")
Stat("food types", "ate mushroom stew", "minecraft:item_used", "minecraft:mushroom_stew")
Stat("food types", "ate potato", "minecraft:item_used", "minecraft:potato")
Stat("food types", "ate sweet berries", "minecraft:item_used", "minecraft:sweet_berries")
Stat("food types", "ate rotten flesh", "minecraft:item_used", "minecraft:rotten_flesh")

Stat("inventory", "crafting table opened", "minecraft:custom", "minecraft:interact_with_crafting_table")
Stat("inventory", "picked up crafting table", "minecraft:mined", "minecraft:crafting_table")

Stat("misc", "deaths", "minecraft:custom", "minecraft:deaths")

Stat("village", "trade attempts", "minecraft:custom", "minecraft:talked_to_villager")
Stat("village", "barrels placed", "minecraft:item_used", "minecraft:barrel")
Stat("village", "composter placed", "minecraft:item_used", "minecraft:composter")
Stat("village", "mined hay block", "minecraft:mined", "minecraft:hay_block")
Stat("village", "clay mined", "minecraft:mined", "minecraft:clay")
Stat("village", "emeralds bought", "minecraft:crafted", "minecraft:emerald")
Stat("village", "cyan bed mined", "minecraft:mined", "minecraft:cyan_bed")
Stat("village", "green bed mined", "minecraft:mined", "minecraft:green_bed")
Stat("village", "lime bed mined", "minecraft:mined", "minecraft:lime_bed")
Stat("village", "white bed mined", "minecraft:mined", "minecraft:white_bed")
Stat("village", "yellow bed mined", "minecraft:mined", "minecraft:yellow_bed")
Stat("village", "orange bed mined", "minecraft:mined", "minecraft:orange_bed")
Stat("village", "red bed mined", "minecraft:mined", "minecraft:red_bed")
Stat("village", "blue bed mined", "minecraft:mined", "minecraft:blue_bed")

Stat("structureless", "furnace opened", "minecraft:custom", "minecraft:interact_with_furnace")
Stat("structureless", "furnace crafted", "minecraft:crafted", "minecraft:furnace")
Stat("structureless", "iron ore mined", "minecraft:mined", "minecraft:iron_ore")
Stat("structureless", "coal ore mined", "minecraft:mined", "minecraft:coal_ore")

Stat("ocean", "magma block mined", "minecraft:mined", "minecraft:magma_block")
Stat("ocean", "craft acacia doors", "minecraft:crafted", "minecraft:acacia_door")
Stat("ocean", "craft birch doors", "minecraft:crafted", "minecraft:birch_door")
Stat("ocean", "craft dark_oak doors", "minecraft:crafted", "minecraft:dark_oak_door")
Stat("ocean", "craft jungle doors", "minecraft:crafted", "minecraft:jungle_door")
Stat("ocean", "craft oak doors", "minecraft:crafted", "minecraft:oak_door")
Stat("ocean", "craft spruce doors", "minecraft:crafted", "minecraft:spruce_door")

Stat("luck", "gravel mined", "minecraft:mined", "minecraft:gravel")
Stat("luck", "flint collected", "minecraft:picked_up", "minecraft:flint")
Stat("luck", "blaze killed", "minecraft:killed", "minecraft:blaze")
Stat("luck", "rods collected", "minecraft:picked_up", "minecraft:blaze")
Stat("luck", "iron golem killed", "minecraft:killed", "minecraft:iron_golem")
Stat("luck", "iron collected", "minecraft:picked_up", "minecraft:iron_ingot")
Stat("luck", "used eye", "minecraft:item_used", "minecraft:ender_eye")

Stat("wood", "oak log mined", "minecraft:mined", "minecraft:oak_log")
Stat("wood", "stripped oak log mined", "minecraft:mined", "minecraft:stripped_oak_log")
Stat("wood", "spruce log mined", "minecraft:mined", "minecraft:spruce_log")
Stat("wood", "stripped spruce log mined", "minecraft:mined", "minecraft:stripped_spruce_log")
Stat("wood", "birch log mined", "minecraft:mined", "minecraft:birch_log")
Stat("wood", "stripped birch log mined", "minecraft:mined", "minecraft:stripped_birch_log")
Stat("wood", "jungle log mined", "minecraft:mined", "minecraft:jungle_log")
Stat("wood", "stripped jungle log mined", "minecraft:mined", "minecraft:stripped_jungle_log")
Stat("wood", "acacia log mined", "minecraft:mined", "minecraft:acacia_log")
Stat("wood", "stripped acacia log mined", "minecraft:mined", "minecraft:stripped_acacia_log")
Stat("wood", "dark oak log mined", "minecraft:mined", "minecraft:dark_oak_log")
Stat("wood", "stripped dark oak log mined", "minecraft:mined", "minecraft:stripped_dark_oak_log")
Stat("wood", "crimson stem mined", "minecraft:mined", "minecraft:crimson_stem")
Stat("wood", "stripped crimson stem mined", "minecraft:mined", "minecraft:stripped_crimson_stem")
Stat("wood", "warped stem mined", "minecraft:mined", "minecraft:warped_stem")
Stat("wood", "stripped warped stem mined", "minecraft:mined", "minecraft:stripped_warped_stem")

Stat("piglins", "gold dropped", "minecraft:dropped", "minecraft:gold_ingot")
Stat("piglins", "gold collected", "minecraft:picked_up", "minecraft:gold_ingot")
Stat("piglins", "pearls collected", "minecraft:picked_up", "minecraft:ender_pearl")
Stat("piglins", "obsidian collected", "minecraft:picked_up", "minecraft:obsidian")
Stat("piglins", "fire res collected", "minecraft:picked_up", "minecraft:potion")
Stat("piglins", "fire res collected", "minecraft:picked_up", "minecraft:splash_potion")
Stat("piglins", "string collected", "minecraft:picked_up", "minecraft:string")

Stat("monument", "mined prismarine", "minecraft:mined", "minecraft:prismarine")
Stat("monument", "mined dark prismarine", "minecraft:mined", "minecraft:dark_prismarine")

Stat("classic", "nether gold mined", "minecraft:mined", "minecraft:nether_gold_ore")
Stat("classic", "gold nuggets picked up", "minecraft:picked_up", "minecraft:gold_nugget")
