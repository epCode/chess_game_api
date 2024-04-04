from twisted.internet import reactor, protocol

class MyServer(protocol.Protocol):
    def connectionMade(self):
        print("Client connected")
        self.transport.write(b"Welcome to the server!")

    def dataReceived(self, data):
        print("Received data from client:", data.decode())

class MyServerFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return MyServer()

def chess():
    print("S")


# Start the reactor
reactor.callWhenRunning(chess)
reactor.run()
