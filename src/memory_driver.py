import memory

my_memory = memory.BactMem(1, "classify-on-update", 0)

try:
    with open('../data/testing_data.txt', 'r') as f:
        for line in f:
            clean_line = line.strip('\n')
            for i in range(0, len(clean_line)):
                result = my_memory.update_memory(clean_line[i])
                if str(result.decision) == clean_line[i]:
                    print("!!!!!!!!!!!!!!!!!!!!!!Good bot!!!!!!!!!!!!!!!!!!! " + str(result.decision))
                else:
                    print("Bad bot? " + str(result.decision))
except IOError:
    print("Couldn't open the file")

