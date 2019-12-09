import network_listener
import memory
import threading
import time
import sys
import logging
import csv

t = threading.Thread(target=network_listener.listen_on_network)
t.start()
with open("../data/network_output.csv", "w") as out:
    with open("../data/live_decisions.txt", "w") as dec_file:
        out_csv = csv.writer(out)
        count = 0
        while count < 50:
            packet = network_listener.thread_queue.get()
            dec_file.write(str(count) + ' ' + str(count) + ' ' + packet[0] + '\n')
            out_csv.writerow(packet[0])#packet[1:])
            count += 1
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
my_mem = memory.BactMem(44, 1, 1)
while True:
    packet = network_listener.thread_queue.get()
    packet_string = ",".join(packet)
    while len(packet_string) < 44:
        packet_string += "0"
    result = my_mem.update_memory(packet[0])#"," + ','.join(packet))
    print(result)
time.sleep(1)
