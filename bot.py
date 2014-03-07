#!/usr/bin/env python

import sys
import logging
import getpass
import re
import urllib2
from BeautifulSoup import BeautifulSoup
from mechanize import Browser
from optparse import OptionParser

import sleekxmpp

sys.setdefaultencoding('utf8')


class MUCBot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password, room, nick):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.room = room
        self.nick = nick

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("groupchat_message", self.muc_message)
        #self.add_event_handler("muc::%s::got_online" % self.room, self.muc_online)


    def start(self, event):

        self.get_roster()
        self.send_presence()
        self.plugin['xep_0045'].joinMUC(self.room, self.nick, wait=True)

    def muc_message(self, msg):

        if msg['mucnick'] != self.nick and "http" in msg['body']:
            link = re.search("(?P<url>https?://[^\s]+)", msg['body']).group("url")
            request = urllib2.Request(link)
            urlopen = urllib2.urlopen(request)
            info = urlopen.info()
            status = urlopen.getcode()
            type = info['content-type']
            mime = re.sub(r'\; charset\=(.*)', '', type)
            mime = re.sub(r'\;charset\=(.*)', '', mime)
            if status < 400:
                if mime == "text/html" or mime == "application/xhtml+xml":
                        data = urlopen.read()
                        soup = BeautifulSoup(data)
                        title = soup.find('title')
                        title = str(title)
                        title = title.replace("<title>", "")
                        title = title.replace("</title>", "")
                        self.send_message(mto=msg['from'].bare, mbody="Link-Titel: %s" % title, mtype='groupchat')
                else:
                        self.send_message(mto=msg['from'].bare, mbody="Ich fuehle mich geehrt, dass du meine Dienste in Anspruch nimmst, %s. Um aber nicht als Bandbreitenvernichter zu fungieren, werde ich diesen Link nicht weiter parsen. Danke fuer dein Verstaendnis." % msg['mucnick'], mtype='groupchat')

            else:
                self.send_message(mto=msg['from'].bare, mbody="*ERROR: %s*" % status, mtype='groupchat')

    logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')

xmpp = MUCBot("USER@jabber.c3d2.de/versionNULLpunktEINS", "PASSWORD", "c3d2@chat.c3d2.de", "2 BetaBOT")
xmpp.register_plugin('xep_0030') # Service Discovery
xmpp.register_plugin('xep_0045') # Multi-User Chat
xmpp.register_plugin('xep_0199') # XMPP Ping
xmpp.connect()
xmpp.process(block=True)

