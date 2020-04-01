from random import choice
# it does not true randomness, pseudo, based off of the Mersenne twister
# choice method uses random() to generate num between 0 and 1, multiply it
# by the number of items in the list we choose from and index into the list


class QuotePicker(object):
    
    def __init__(self, quotes_filename):
        """Initialize our QuotePicker class"""
        with open(quotes_filename) as quotes_file:
            self.quotes = quotes_file.readlines()

    def pick(self):
        """return a random quote."""
        return choice(self.quotes).strip()
