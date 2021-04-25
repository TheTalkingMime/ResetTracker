import datetime
import json
import time
from datetime import datetime
import time

from watchdog.events import FileSystemEventHandler


class Achievements(FileSystemEventHandler):
    checks = [
        ("minecraft:recipes/misc/charcoal", "has_log"),
        ("minecraft:story/iron_tools", "iron_pickaxe"),
        ("minecraft:story/enter_the_nether", "entered_nether"),
        ("minecraft:nether/find_bastion", "bastion"),
        ("minecraft:nether/find_fortress", "fortress"),
        ("minecraft:recipes/decorations/ender_chest", "has_ender_eye"),
        ("minecraft:story/follow_ender_eye", "in_stronghold"),
        ("minecraft:story/enter_the_end", "entered_end"),
    ]

    def __init__(self):
        self.startTime = None
        self.this_run = [None] * (len(self.checks) + 1)
        self.endTime = datetime.now()
        self.path = None

    def on_modified(self, event):
        self.path = event.src_path

    def checkAdvancements(self, igt):
        self.endTime = datetime.now()

        if self.startTime == None:
            self.startTime = datetime.now()

        try:
            achievements_file = open(self.path)
            achievements = json.load(achievements_file)
            achievements_file.close()
        except:
            print("Could not open achievements at, ", self.path)
            print("Will try again at next auto save/pause")
            time.sleep(0.1)
            self.checkAdvancements(igt)
            return

        if (
            "minecraft:adventure/adventuring_time" in achievements
            and "criteria" in achievements["minecraft:adventure/adventuring_time"]
        ):
            temp = min(
                achievements["minecraft:adventure/adventuring_time"][
                    "criteria"
                ].values()
            )
            temp = temp[0:19]
            self.startTime = datetime.strptime(temp, "%Y-%m-%d %H:%M:%S")

        if self.endTime < self.startTime:
            print("endTime was before startTime, setting endTime equal to start...")
            self.endTime = self.startTime

        self.this_run[0] = "0:" + str(
            time.strftime(
                "%M:%S",
                time.gmtime((self.endTime - self.startTime).total_seconds()),
            )
        )

        if igt != None:
            igt = igt / 20
            offset = (self.endTime - self.startTime).total_seconds() - (igt)
            for idx in range(len(self.checks)):
                if (
                    self.checks[idx][0] in achievements
                    and achievements[self.checks[idx][0]]["done"]
                    and self.this_run[idx + 1] == None
                ):
                    time_str = (
                        self.checks[idx][1],
                        achievements[self.checks[idx][0]]["criteria"][
                            self.checks[idx][1]
                        ],
                    )
                    time_str = time_str[1]
                    time_str = time_str[0:19]
                    time_timefmt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    seconds = (time_timefmt - self.startTime).total_seconds() - offset
                    if seconds < 0:
                        seconds = (time_timefmt - self.startTime).total_seconds()
                        print(
                            "IGT Offset was too high (likely couldn't load stats file) would've caused underflow, recovering using RTA"
                        )
                    self.this_run[idx + 1] = "0:" + str(
                        time.strftime("%M:%S", time.gmtime(seconds))
                    )

    def getRun(self):
        if self.this_run[0] == None:
            self.this_run[0] = "0:00:00"
        return self.this_run
