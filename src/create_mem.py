""" A program to take a file with input and 'classify' it for the
bacterial memory. It just uses the fact that the data's basically marked."""
import memory

curr_index = 0
try:
    with open('../data/memory_string.txt', 'r') as mem_file:
        with open('../data/decisions.txt', 'w') as dec_file:
            for line in mem_file:
                line = line.strip("\n")
                for i in range(len(line)):
                    dec_file.write(str(curr_index) + ' ' + str(curr_index) + ' ' + line[i] + '\n')
                    curr_index += 1
                
except IOError:
    print("Couldn't open the file.")
