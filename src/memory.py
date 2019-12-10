""" A module to implement the Bacterial Memory model for a primitive machine learning algorithm. """
import logging
import sys
#import random

#Comment out this line to turn off logging
#logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class BactMem():
    """ The Bacterial Memory Model implementation """
    memory_file_name = '../data/network_output.csv'#memory_string.txt'
    decision_file_name = '../data/live_decisions.txt'


    def __init__(self, mem_entry_len, update_mode, decision_mode):
        self.memory = "" #the memory string
        self.decisions = {} # decision memory
        self.mem_entry_len = mem_entry_len
        self.update_mode = update_mode
        self.decision_mode = decision_mode
        # load memory from file
        try:
            with open(BactMem.memory_file_name, 'r') as mf:
                for line in mf:
                    self.memory += line.strip('\n')
        except IOError:
            logging.error("The memory file does not exist.")
        # load decisions from file
        try:
            with open(BactMem.decision_file_name, 'r') as df:
                for line in df:
                    vals = line.split()
                    if len(vals) == 3:
                        print(line + self.memory[int(vals[0])])
                        decision = Decision(int(vals[0]), int(vals[1]), int(vals[2]))
                        self.add_decision(decision)
        except IOError:
            logging.error("The decision file does not exist.")


    def add_decision(self, decision):
        """ A method to add a Decision object to the object's decision dictionary. """
        if not decision.end_position in self.decisions:
            self.decisions[decision.end_position] = decision
        else:
            logging.info("Attempting to add duplicate decision")


    def update_memory(self, new_memory):
        """ Updates the internal memory representation with the newly produced data.
                new_memory: a string containing the memory. The format is determined
                (and enforced) by the client """
        self.memory += new_memory
        decision = -1
        if self.update_mode == "classify-on-update":
            decision = self.make_decision(self.memory)
            self.add_decision(decision)
        return decision


    def find_substr(self, search_string, offset):
        """ Find the last (rightmost) occurrence of the given string in self.memory. """
        offset *= self.mem_entry_len
        return self.memory.rfind(
            search_string[offset:], 0, len(search_string) - self.mem_entry_len)


    def find_memory(self, search_string):
        """ Finds the largest suffix of search_string that occurred previously in the memory.
        It will return the last occurrence. """
        logging.info("find_memory: Finding substring of %s \nin memory", search_string)
        logging.info("find_memory: last index is %s", search_string[-1])
        offset = 1
        index = self.find_substr(search_string, offset)
        while index == -1 and offset < len(search_string) - 1:
            #logging.info(search_string[offset:] + " does not occur")
            offset += 1
            index = self.find_substr(search_string, offset)
            if self.decisions.get(index + len(search_string[offset:])-1) is None:
                index = -1
        return index, offset


    def make_decision(self, curr_memory):
        """ A system to decide whether the current memory-state is 'bad'.
        Finds the most recent relevant memory and investigates the decision made
        at that time. If no memory was made, it makes a random choice and enters
        that as the decision. """
        recent_memory, offset = self.find_memory(curr_memory)
        prev_decision = self.decisions.get(recent_memory + len(curr_memory[offset:]) - self.mem_entry_len)
        logging.debug("make_decision: matched string %s", curr_memory[recent_memory:])
        if recent_memory == -1 or prev_decision is None:
            decision_value = 0 #decision_value = random.randint(0,1) if self.decision_mode == 0 else int(input())
            decision = Decision(len(self.memory) - 1, len(self.memory), decision_value)
            logging.info(
                "make_decision: New Decision is " + str(decision.decision)
                + " at " + str(decision.substr_len) + " characters long")
        else:
            decision = Decision(
                len(self.memory) - 1, prev_decision.substr_len, prev_decision.decision)
            logging.info(
                "make_decision: Matched Decision at " + str(prev_decision.end_position)
                + " is " + str(decision.decision)
                + " at " + str(decision.substr_len) + " characters long")
        return decision


class Decision():
    """ A class to provide an organization for the decisions as a data structure. """

    def __init__(self, index, length, decision):
        self._end_position = index
        self._substr_len = length
        self._decision = decision # this is an integer


    @property
    def end_position(self):
        """ Get the end position in memory where this decision occurred. """
        return self._end_position


    @property
    def substr_len(self):
        """ Get the length of the substring associated with this decision. """
        return self._substr_len


    @property
    def decision(self):
        """ Get the decision for this memory. """
        return self._decision


    def update(self, updated_decision):
        """ Updates the decision to the provided integer value. """
        self._decision = updated_decision
