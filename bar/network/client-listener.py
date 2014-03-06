import optparse, os, psutil, time, zlib
from twisted.internet.protocol import ServerFactory, ClientFactory, Protocol
from twisted.protocols import basic
from twisted.python import log
from Crypto.Cipher import AES

class ListenerProtocol(Protocol):

    def dataReceived(self, data):

        splitdata = data.split("|||")
        label = splitdata[0]

        import sqlite3 as lite
        import sys

        con = lite.connect('bar/db/bar.db')

        with con:                
            cur = con.cursor() 
            cur.execute("SELECT * FROM contacts WHERE label=:label", {"label":label})

            row = cur.fetchone()

            if row != None:

                start = time.time()
                encrypted = splitdata[1]
                cleartext = self.AESdecrypt(row[4], encrypted)
                newlabel = cleartext.split("|||")[0]

                cur.execute("INSERT INTO messages(message) VALUES(?);", (cleartext.split("|||")[1].decode('ascii'),))
                cur.execute("UPDATE contacts SET label=? WHERE label=?", (newlabel, label))
            else:
                print "Couldn't find the retrieved label. Rejecting the message."

    def AESdecrypt(self, skey, c):
        '''
        Decrypt given message with shared key.
        '''

        iv = '\x00' * 16
        stream=AES.new(skey, AES.MODE_CFB, iv)
        return stream.decrypt(c)


class ListenerFactory(ServerFactory):

    protocol = ListenerProtocol

    def __init__(self, reactor):
        self.reactor = reactor

def main():

    from twisted.internet import reactor

    factory = ListenerFactory(reactor)

    print "Starting reactor..."
    port = reactor.listenTCP(options.port or 4333, factory,
                             interface=options.iface)

    print 'Listening on %s.' % (port.getHost())

    reactor.run()

if __name__ == '__main__':
    main()