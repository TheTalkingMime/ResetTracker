from watchdog.events import FileSystemEventHandler
import json


class Stats(FileSystemEventHandler):
    checks = [
        ("minecraft:custom", "minecraft:play_one_minute"),
        ("minecraft:dropped", "minecraft:gold_ingot"),
        ("minecraft:picked_up", "minecraft:blaze_rod"),
        ("minecraft:killed", "minecraft:blaze"),
        ("minecraft:custom", "minecraft:damage_taken"),
        ("minecraft:custom", "minecraft:sprint_one_cm"),
        ("minecraft:custom", "minecraft:boat_one_cm"),
        ("minecraft:picked_up", "minecraft:flint"),
        ("minecraft:mined", "minecraft:gravel"),
        ("minecraft:mined", "minecraft:prismarine"),
        ("minecraft:crafted", "minecraft:furnace"),  # for identifying structureless
        ("minecraft:crafted", "minecraft:iron_ingot"),  # for identifying structureless
        ("minecraft:mined", "minecraft:iron_ore"),  # for identifying structureless
        ("minecraft:mined", "minecraft:hay_block"),  # for identifying village
        ("minecraft:killed", "minecraft:iron_golem"),  # for identifying village
        ("minecraft:mined", "minecraft:magma_block"),  # for identifying shipwreck
        ("minecraft:crafted", "minecraft:wooden_axe"),  # for identifying shipwreck
        ("minecraft:custom", "minecraft:swim_one_cm"),
        ("minecraft:custom", "minecraft:deaths"),
        ("minecraft:custom", "minecraft:time_since_death"),
        ("minecraft:custom", "minecraft:traded_with_villager"),
        ("minecraft:killed", "minecraft:enderman"),
        ("minecraft:crafted", "minecraft:shield"),
        ("minecraft:crafted", "minecraft:bucket"),
        ("minecraft:picked_up", "minecraft:ender_eye"),
    ]
    this_run = None

    def __init__(self, advancements):
        self.this_run = [None] * (len(self.checks))
        self.advancements = advancements
        self.pauses = 0
        try:
            settings_file = open("settings.json")
            settings = json.load(settings_file)
            settings_file.close()
            self.threshold = settings["threshold"]
            # print("Set threshold to", self.threshold)
        except Exception as e:
            print(e)
            print(
                "Could not find settings.json, make sure you have the file in the same directory as the exe, and named exactly 'settings.json'"
            )
            wait = input("")

    def on_modified(self, event):
        try:
            stats_file = open(event.src_path)
            stats = json.load(stats_file)
            stats_file.close()
        except Exception as e:
            print("Failed to open stats file")
            return
        stats = stats["stats"]
        self.this_run[0] = stats[self.checks[0][0]][self.checks[0][1]]
        if self.this_run[0] <= self.threshold:
            return  # Prevents stats being read early from multi instances
        for idx in range(1, len(self.checks)):
            if (
                self.checks[idx][0] in stats
                and self.checks[idx][1] in stats[self.checks[idx][0]]
            ):
                self.this_run[idx] = str(
                    stats[self.checks[idx][0]][self.checks[idx][1]]
                )
        if self.this_run[0] != None and self.advancements.path != None:
            self.advancements.checkAdvancements(int(self.this_run[0]))

    def getIgt(self):
        if self.this_run[0] != None:
            return int(self.this_run[0])
        return None

    def getRun(self):
        return self.this_run