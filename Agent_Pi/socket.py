import socket
import threading
import sys
import datetime
from getpass import getpass

# Wait for incoming data from server
# .decode is used to turn the message in bytes to a string
def receive(socket, signal):
    while signal:
        try:
            data = socket.recv(32)
            print(str(data.decode("utf-8")))
        except:
            print("You have been disconnected from the server")
            signal = False
            break


# Get host and port
# host = input("Host:localhost")
# port = int(input("Port:8080"))


# Attempt connection to server
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 5001))
except:
    print("Could not make a connection to the server")
    input("Press enter to quit")
    sys.exit(0)

# Create new thread to wait for data
receiveThread = threading.Thread(target=receive, args=(sock, True))
receiveThread.start()

# Send data to server
# str.encode is used to turn the string message into bytes so it can be sent across the network
while True:
    # message = '{"customer_id":"6","car_id":"1","username":"abc@gmail.com","password":"123"}'
    username = input("Insert Username :")
    print("\n")

    password = getpass("Insert password :")
    print("\n")

    customer_id = input("Insert your Customer ID :")
    print("\n")

    car_id = input("Insert Car ID :")
    print("\n")

    message = '{"username":"%s","password":"%s","customer_id":"%s","car_id":"%s"}' % (
        username, password, customer_id, car_id)
    print("\n")
    sock.sendall(str.encode(message))
