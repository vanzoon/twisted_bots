from configparser import ConfigParser
# from sys import path


# third party modules
from zope.interface import implementer
from twisted.application.service import IServiceMaker, Service
from twisted.internet.endpoints import clientFromString
from twisted.python import usage, log
from twisted.plugin import IPlugin

# path.insert(0, '/home/vanzoon/Projects/PycharmProjects/net_bot')

from talkback.bot import TalkBackBotFactory
from talkback.quote_picker import QuotePicker


class Options(usage.Options):
    # usage module to parse conf
    optParameters = [['config', 'c', 'settings.ini', 'Configuration file.']]
    # two flags: --config and -c twat we could include when twistd twsrs execute
    # twistd shittybot [-c, --config PATH_TO_SETTINGS_INI]


class TalkBackBotService(Service):
    # Service class to start/stop application
    _bot = None

    def __init__(self, endpoint, channel, nickname, realname, quotesFilename, triggers):
        self._endpoint = endpoint
        self._channel = channel
        self._nickname = nickname
        self._realname = realname
        self._quotesFilename = quotesFilename
        self._triggers = triggers

    def startService(self):
        """Construct a client & connect to server."""
        from twisted.internet import reactor
        '''If you import twisted.internet.reactor without first installing 
        a specific reactor implementation, then Twisted will install
         the default reactor for you. The particular one you get will 
         depend on the operating system and Twisted version you are using. 
         For that reason, it is general practice not to import the reactor 
         at the top level of modules to avoid accidentally installing 
         the default reactor. Instead, import the reactor in the same scope 
         in which you use it.'''
        ''' The event loop is a programming construct that waits for and 
        dispatches events or messages in a program. It works by calling some 
        internal or external “event provider”, which generally blocks 
        until an event has arrived, and then calls the relevant event handler 
        (“dispatches the event”). The reactor provides basic interfaces 
        to a number of services, including network communications, threading, 
        and event dispatching.'''

        def connected(bot):
            self._bot = bot

        def failure(err):
            log.err(err, _why="Could not connect to specified server.")
            reactor.stop()

        quotes = QuotePicker(self._quotesFilename)
        client = clientFromString(reactor, self._endpoint)
        factory = TalkBackBotFactory(
            self._channel,
            self._nickname,
            self._realname,
            quotes,
            self._triggers,
        )
        return client.connect(factory).addCallbacks(connected, failure)

    def stopService(self):
        """Disconnect"""
        if self._bot and self._bot.transport.connected:
            self._bot.transport.loseConnection()


@implementer(IServiceMaker, IPlugin)
class BotServiceMarker(object):
    tapname = "shittybot"   # name for plugin, the subcommand of twistd
    description = "IRC bot that provides quotations from notable women"  # what the plugin does
    options = Options  # referring to Options class

    def makeService(self, options):
        """Construct the talkbackbot service."""
        config = ConfigParser()  # read from options parameter config and grabbing
        config.read([options["config"]])
        triggers = [
            trigger.strip()  # strip the null char-s for every trigger in config file (settings.ini)
            for trigger
            in config.get("talkback", "triggers").split("\n")
            if trigger.strip()
        ]

        return TalkBackBotService(
            endpoint=config.get('irc', 'endpoint'),
            channel=config.get('irc', 'channel'),
            nickname=config.get('irc', 'nickname'),
            realname=config.get('irc', 'realname'),
            quotesFilename=config.get('talkback', 'quotesFilename'),
            triggers=triggers,
        )


serviceMaker = BotServiceMarker()
# create an object which *provides* the relevant interface
# of IPlugin and IServiceMaker ??
