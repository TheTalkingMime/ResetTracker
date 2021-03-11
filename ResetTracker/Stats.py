from watchdog.events import FileSystemEventHandler
import time
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
    ]
    this_run = None

    def __init__(self):
        self.this_run = [None] * (len(self.checks) + 1)

    def on_modified(self, event):
        stats = open(event.src_path)
        stats = json.load(stats)
        stats = stats["stats"]
        for idx in range(len(self.checks)):
            try:
                self.this_run[idx] = str(
                    stats[self.checks[idx][0]][self.checks[idx][1]]
                )
            except Exception as e:
                continue

    def getIgt(self):
        if self.this_run[0] != None:
            return int(self.this_run[0])
        return 0

    def getRun(self):
        return self.this_run