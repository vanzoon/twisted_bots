import os
from sys import path


path.insert(0, '/home/vanzoon/Projects/PycharmProjects/net_bot')


from twisted.trial import unittest
# trial is unit testing system, an extension of python unittest module

from talkback.quote_picker import QuotePicker


class TestQuotePicker(unittest.TestCase):
    QUOTE1 = (
        "A fool without fear is sometimes wiser than an angel with fear. "
        "~ Nancy Astor"
    )
    QUOTE2 = (
        "You don't manage people, you manage things. You lead people. "
        "~ Grace Hopper"
    )

    def test_pick(self):
        picker = QuotePicker(
                os.path.join(path[0], "tests/test_quotes.txt")
        )
        # we have to check the pick function returned quote.
        quote = picker.pick()
        self.assertIn(quote, (self.QUOTE1, self.QUOTE2),
                      f"Got unexpected quote: {quote}")
