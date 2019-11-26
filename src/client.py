import argparse, socket, logging, concurrent.futures, sys, time

# Comment out the line below to not print the INFO messages
logging.basicConfig(level=logging.INFO)

RED_DURATION = 10 #Variable to control the timer for red lights (in seconds)

def recvall(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            logging.error('Did not receive all the expected bytes from server.')
            break
        data += more
    return data


def client(host ,port):
    # connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host ,port))
    isGreen = False
    logging.info('Connect to server: ' + host + ' on port: ' + str(port))

    # exchange messages
    sock.sendall(b'100 HELO')
    logging.info('Sent: 100 HELO')
    message = recvall(sock, 6).decode('utf-8')
    logging.info('Received: ' + message)
    if message.startswith('200'):
        logging.info('All OK')
    else:
        logging.info('We sent a bad request.')

    # REGISTRATION
    message = recvall(sock, 3).decode('utf-8')
    logging.info('Received: ' + message)
    if message.startswith('110'):
        clientRole = 'N'
        isGreen = True
        logging.info('Role is ' + clientRole)
    elif message.startswith('120'):
        clientRole = 'E'
        logging.info('Role is ' + clientRole)
    elif message.startswith('130'):
        clientRole = 'S'
        isGreen = True
        logging.info('Role is ' + clientRole)
    elif message.startswith('140'):
        clientRole = 'W'
        logging.info('Role is ' + clientRole)
    else:
        logging.info('Received error: ' + message)
        clientRole = ''

    message = recvall(sock, 3).decode('utf-8')
    logging.info(clientRole + ' Received: ' + message)

    while True:
        if isGreen:
            message = recvall(sock, 7).decode('utf-8')
            logging.info(clientRole + ' Received: ' + message)
            if message.startswith("400"):
                isGreen = False
                sendMessage = ("100 " + clientRole + " R").encode('utf-8')
                sock.sendall(sendMessage)
                logging.info(clientRole + ' Sent:' + sendMessage.decode('utf-8'))
            else:
                sys.exit(-1)
        else: # light is Red
            time.sleep(RED_DURATION)
            sendMessage = ("200 " + clientRole + " G").encode('utf-8')
            sock.sendall(sendMessage)
            logging.info(clientRole + ' Sent: ' + sendMessage.decode('utf-8'))
            message = recvall(sock, 7).decode('utf-8')
            logging.info(clientRole + ' Received: ' + message)
            if message.startswith("300"):
                isGreen = True
            else:
                sys.exit(-1)


if __name__ == '__main__':
    port = 9001

    parser = argparse.ArgumentParser(description='Basic Traffic Light Simulator')
    parser.add_argument('host', help='IP address of the server.')
    args = parser.parse_args()

    with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor:
        for i in range(4):
            executor.submit(client, args.host, port)
