from nbt import nbt
import os

path = """D:/Users/Andrew D/AppData/Roaming/.minecraft/saves/New World (14)/level.dat"""
print(
    os.chdir(
        """D:\\Users\\Andrew D\\AppData\\Roaming\\.minecraft\\saves\\New World (14)\\level.dat"""
    )
)
nbtfile = nbt.NBTFile(path, "rb")
print(nbtfile["Data"]["WorldGenSettings"]["seed"])