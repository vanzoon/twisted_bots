from sys import path


path.insert(0, '/home/vanzoon/Projects/PycharmProjects/net_bot')


from twisted.test import proto_helpers
from twisted.trial import unittest

from talkback.bot import TalkBackBotFactory

# unit tests need to be independent of each other!

QUOTE = "Nobody minds having what is too good for them. ~ Jane Austen"


class FakePicker(object):
    """Always return the same quote."""
    def __init__(self, quote):
        self._quote = quote

    def pick(self):
        return self._quote


class TestTalkBackBot(unittest.SynchronousTestCase):
    # SynchronousTestCase extends TestCase by adding some helpers (logging,
    # warning integration, monkey-patching and others)
    _channel = "#testchannel"
    _username = "#testuser"
    _us = "tbb"

    def setUp(self):
        # gets called to prepare our tests
        factory = TalkBackBotFactory(
            self._channel,
            self._us,
            "Jane Doe",
            FakePicker(QUOTE),
            ['twss'],  # trigger
        )
        # working with fake network connection, face IRC server
        self.bot = factory.buildProtocol(('127.0.0.1', 0))  # localhost, port 0
        self.fake_transport = proto_helpers.StringTransport()
        self.bot.makeConnection(self.fake_transport)
        self.bot.signedOn()
        self.bot.joined(self._channel)
        self.fake_transport.clear()

    def test_privmsgNoTrigger(self):
        """Should not send a quote if message does not match trigger"""
        # when we run our test suite, it will pick up on all functions
        # that begin with test_
        self.bot.privmsg(self._username, self._channel, "hi")  # does not match
        self.assertEqual(
            b'',
            self.fake_transport.value()
        )

    def test_privmsgWithTrigger(self):
        """Should send a quote if message matches trigger"""
        #
        self.bot.privmsg(self._username, self._channel, "twss")
        self.assertEqual(
            bytes(f"PRIVMSG {self._channel} :{self._username }: {QUOTE}\r\n", 'utf-8'),
            self.fake_transport.value()
        )

    def test_privAttribution(self):
        """If someone attributes the bot in public, they get a public response."""
        # if a user pings bot via the channel we're in, bot responds with a quote
        self.bot.privmsg(self._username, self._channel, self._us + ': foo')
        self.assertEqual(
            bytes(f"PRIVMSG {self._channel} :{self._username}: {QUOTE}\r\n", 'utf-8'),
            self.fake_transport.value()
        )

    def test_privmsgPrivateMessage(self):
        """For private messages, should send quote directly to user"""
        self.bot.privmsg(self._username, self._us, "hi")
        self.assertEqual(
            bytes(f"PRIVMSG {self._username} :{QUOTE}\r\n", 'utf-8'),
            self.fake_transport.value()
        )
