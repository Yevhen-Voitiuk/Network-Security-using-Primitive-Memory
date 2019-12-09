import argparse, socket, logging, threading, sys
import time

# Comment out the line below to not print the INFO messages
logging.basicConfig(level=logging.INFO)

class ClientThread(threading.Thread):

    lightToChange = threading.Lock()
    changeMutex = threading.Lock()
    roleLock = threading.Lock()
    clearLock = threading.Lock()

    changeLight = False

    roles = ['N', 'E', 'S', 'W']

    NChangeEvent = threading.Event()
    SChangeEvent = threading.Event()
    EChangeEvent = threading.Event()
    WChangeEvent = threading.Event()
    changeEvents = {
            'N': NChangeEvent,
            'S': SChangeEvent,
            'E': EChangeEvent,
            'W': WChangeEvent
            }

    NisTaken = False
    EisTaken = False
    SisTaken = False
    WisTaken = False
        
    def __init__(self, address, socket):
        threading.Thread.__init__(self)
        self.addr = address
        self.csock = socket
        self.isGreen = False
        logging.info('New connection added.')

    def run(self):
        # exchange messages
        message = self.recvall(8)
        msg = message.decode('utf-8')
        logging.info('Received a message from client: ' + msg)

        if msg.startswith('100'):
            self.csock.sendall(b'200 OK')
            logging.info('Received HELO ok from client.')
        else:
            self.csock.sendall(b'500 BAD REQUEST')
            logging.warning('Bad request from client.')

        # Pre-connection
        # Assign traffic light
        with ClientThread.roleLock:
            if not ClientThread.NisTaken:
                self.role = 0
                ClientThread.NisTaken = True
                self.isGreen = True
                self.csock.sendall(b'110')
                ClientThread.NChangeEvent.set()
            elif not ClientThread.EisTaken:
                self.role = 1
                ClientThread.EisTaken = True
                self.csock.sendall(b'120')
                ClientThread.EChangeEvent.set()
            elif not ClientThread.SisTaken:
                self.role = 2
                ClientThread.SisTaken = True
                self.isGreen = True
                self.csock.sendall(b'130')
                ClientThread.SChangeEvent.set()
            elif not ClientThread.WisTaken:
                self.role = 3
                ClientThread.WisTaken = True
                self.csock.sendall(b'140')
                ClientThread.WChangeEvent.set()
            else:
                self.csock.sendall(b'105')



        # Game on
        # Send 900: game start trigger
        message = '900'.encode('utf-8')
        ClientThread.NChangeEvent.wait()
        ClientThread.EChangeEvent.wait()
        ClientThread.SChangeEvent.wait()
        ClientThread.WChangeEvent.wait()

        ClientThread.NChangeEvent.clear()
        ClientThread.EChangeEvent.clear()
        ClientThread.SChangeEvent.clear()
        ClientThread.WChangeEvent.clear()

        self.csock.sendall(message)
        logging.info('Sent: 900')

        # Main loop of the Traffic Light simulation
        while True:
            if self.isGreen:
                ClientThread.changeEvents[ ClientThread.roles[(self.role + 1) % 2] ].wait()
                ClientThread.changeEvents[ ClientThread.roles[( (self.role + 1) % 2) + 2] ].wait()
                message = ("400 " + ClientThread.roles[self.role] + " R").encode('utf-8')

                self.csock.sendall(message)
                logging.info('Sent to ' + ClientThread.roles[self.role] + ': 400 ' + ClientThread.roles[self.role] + ' R')
                message = self.recvall(7).decode('utf-8')
                if message.startswith('700'):
                    #message += self.recvall(15).decode('utf-8')
                    logging.error('Received fatal error from ' + ClientThread.roles[self.role] + ': ' + message)
                    break
                #else:
                #    message += self.recvall(4).decode('utf-8')
                logging.info('Received from ' + ClientThread.roles[self.role] + ': ' + message)
                self.isGreen = False
                
                ClientThread.changeEvents[ClientThread.roles[self.role]].set()
 
            else:
                message = self.recvall(7).decode('utf-8')
                if message.startswith('700'):
                    #message += self.recvall(15).decode('utf-8')
                    logging.error('Received fatal error from ' + ClientThread.roles[self.role] + ': ' + message)
                #else:
                #    message += self.recvall(4).decode('utf-8')
                logging.info('Received from ' + ClientThread.roles[self.role] + ': ' + message)

                adjacent = (self.role + 1) % 2
                while (ClientThread.changeEvents[ClientThread.roles[adjacent]].isSet() or ClientThread.changeEvents[ClientThread.roles[adjacent + 2]].isSet()):
                    message = ('800 ' + ClientThread.roles[self.role] + ' G').encode('utf-8')
                    self.csock.sendall(message)
                    logging.info('Sent to ' + ClientThread.roles[self.role] + ':800 ' + ClientThread.roles[self.role] + ' G')
                    time.sleep(0.5)

                ClientThread.changeEvents[ClientThread.roles[self.role]].set()
                
                #wait on changeEvents['N']
                ClientThread.changeEvents[ClientThread.roles[(self.role+1) % 4]].wait()
                #wait on changeEvents['S']
                ClientThread.changeEvents[ClientThread.roles[(self.role+2) % 4]].wait()
                #wait on changeEvents['E']
                ClientThread.changeEvents[ClientThread.roles[(self.role+3) % 4]].wait()
                #clear all events

                time.sleep(1) #Removing the sleep desynchronizes the system. Potential break for machine learning alrgorithm to catch

                self.clearEvents()

                message = ("300 " + ClientThread.roles[self.role] + " G").encode('utf-8')
                self.csock.sendall(message)
                logging.info('Sent to ' + ClientThread.roles[self.role] + ': 300 ' + ClientThread.roles[self.role] + ' G')
                self.isGreen = True


    def recvall(self, length):
        data = b''
        while len(data) < length:
            more = self.csock.recv(length - len(data))
            if not more:
                logging.error('Did not receive all the expected bytes from server.')
                break
            data += more
        return data

    def qrecvall(self, length):
        data = b''
        while len(data) < length:
            more = self.csock.recv(length - len(data), socket.MSG_DONTWAIT)
            if not more:
                logging.error('Did not receive all the expected bytes from server.')
                break
            data += more
        return data

    def clearEvents(self):
        ClientThread.changeEvents['N'].clear()
        ClientThread.changeEvents['S'].clear()
        ClientThread.changeEvents['E'].clear()
        ClientThread.changeEvents['W'].clear()

                


def server():

    # get ip from args
    parser = argparse.ArgumentParser(description='Basic Traffic Light Simulator')
    parser.add_argument('host', help='IP address of the server.')
    args = parser.parse_args()

    # start serving (listening for clients)
    port = 9001
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((args.host, port))

    while True:
        sock.listen(1)
        logging.info('Server is listening on port ' + str(port))

        # client has connected
        sc ,sockname = sock.accept()
        logging.info('Accepted connection.')
        t = ClientThread(sockname, sc)
        t.start()

# Initiate the server
server()
