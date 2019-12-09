""" A script to test the classes defined in memory.py """
import memory

print("This Worked")

my_memory = memory.BactMem(1, "classify-on-update")
my_memory.update_memory("010")
my_memory.update_memory("0")
my_memory.update_memory("10")
my_memory.update_memory("1")

