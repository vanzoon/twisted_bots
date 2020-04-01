from twisted.internet import protocol
from twisted.python import log
from twisted.words.protocols import irc


class TalkBackBot(irc.IRCClient):

    def connectionMade(self):
        """Called when a connection is made."""
        # initialization/setup of IRC protocol
        self.nickname = self.factory.nickname
        self.realname = self.factory.realname
        irc.IRCClient.connectionMade(self)
        log.msg("ConnectionMade")

    def connectionLost(self, reason):
        """called when a connection is lost."""
        irc.IRCClient.connectionLost(self, reason)
        log.msg(f"ConnectionLost {str(reason)}")

    # callbacks for events

    def signedOn(self):
        """called when bot has successfully signed on to server."""
        log.msg("Signed on")
        if self.nickname != self.factory.nickname:
            log.msg(f"Your nickname was already occupied, actual name is {self.nickname}.")
            # server will often give you a modified nick with the trailing _.
        self.join(self.factory.channel)

    def joined(self, channel):
        """called when bot joins the channel."""
        log.msg(f"{self.nickname} has joined {self.factory.channel}")

    def privmsg(self, user, channel, msg):
        """Called when the bot receives a message."""
        # what happens when someone say trigger (that's what she said)
        # in our channel
        sendTo = None
        prefix = ''
        senderNick = user.split("!", 1)[0] #what is the shit here
        # the user who prompts the bot with the trigger.
        if channel == self.nickname:
            # private massage comes, reply on /MSG
            sendTo = senderNick
        elif msg.startswith(self.nickname):
            # message with the bot's nickname within the channel
            # reply back on the channel
            sendTo = channel
            prefix = senderNick + ": "
        else:
            # message only with trigger sent to channel
            msg = msg.lower()
            for trigger in self.factory.triggers:
                if msg in trigger:
                    sendTo = channel
                    prefix = senderNick + ": "
                    break

        if sendTo:
            # if sendTo is None it's execute???
            quote = self.factory.quotes.pick()
            self.msg(sendTo, prefix + quote)
            log.msg(f"sent message to {sendTo}, triggered by {senderNick}:\n\t{quote}")


class TalkBackBotFactory(protocol.ClientFactory):
    # create/instantiate the TalkBackBot IRC protocol
    # inheritance allows make use of creating a connection between
    # client and the protocol (our IRC connection) and handle errors

    protocol = TalkBackBot
    # this call an internal method buildProtocol() which inst-s
    # a ClientFactory to be able to handle input of an incoming server conn-n

    def __init__(self, channel, nickname, realname, quotes, triggers):
        self.channel = channel
        self.nickname = nickname
        self.realname = realname
        self.quotes = quotes
        self.triggers = triggers
