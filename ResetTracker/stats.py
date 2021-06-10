from watchdog.events import FileSystemEventHandler
import time
import json
from datetime import datetime


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
    ]
    this_run = None

    def __init__(self, advancements):
        self.this_run = [None] * (len(self.checks) + 1)
        self.advancements = advancements

    def on_modified(self, event):
        print("stats updated")
        try:
            stats_file = open(event.src_path)
            stats = json.load(stats_file)
            stats_file.close()
        except Exception as e:
            print("Failed to open stats file")
            return
        stats = stats["stats"]
        self.this_run[0] = stats[self.checks[0][0]][self.checks[0][1]]
        for idx in range(len(self.checks)):
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