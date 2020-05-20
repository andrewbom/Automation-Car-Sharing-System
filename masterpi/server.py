import socket
import threading
from database_utils import DatabaseUtils
import math

try:
    import json
except ImportError:
    import simplejson as json

# Variables for holding information about connections
connections = []
total_connections = 0
db = DatabaseUtils()


class ServerClass:
    # Client class, new instance created for each connected client
    # Each instance has the socket and address that is associated with items
    # Along with an assigned ID and a name chosen by the client
    class Client(threading.Thread):
        def __init__(self, socket, address, id, name, signal):
            threading.Thread.__init__(self)
            self.socket = socket
            self.address = address
            self.id = id
            self.name = name
            self.signal = signal

        def __str__(self):
            return str(self.id) + " " + str(self.address)

        # Attempt to get data from client
        # If unable to, assume client has disconnected and remove him from server data
        # If able to and we get data back, print it in the server and send it back to every
        # client aside from the client that has sent it
        # .decode is used to convert the byte data into a printable string

        def run(self):
            # if there is a signal, run the following coding
            while self.signal:
                try:
                    # receiving the data from agent_pi
                    data = self.socket.recv(120)
                except:
                    # show the message that signal is disconnected
                    print("Client " + str(self.address) + " has disconnected")
                    self.signal = False
                    connections.remove(self)
                    break

                if data:
                    try:
                        new_data = json.loads(data)
                        print("ID " + str(self.id) + ": " + str(data.decode("utf-8")))
                        # date = new_data["date"]
                        data_type = new_data["type"]

                        # check if the data type is credentials
                        if data_type == "credentials":

                            # assigning the variables to the user account information that entered in the agent_pi
                            username = new_data["username"]
                            password = new_data["password"]
                            customer_id = new_data["customer_id"]
                            car_id = new_data["car_id"]

                            # checking whether the user account information of agent pi match that on cloud database
                            user_data = db.login_account(username, password)

                            # if the account information match that on cloud database
                            if user_data is not None:
                                # validate whether the user has booked the car
                                verify = db.validate_collection(customer_id, car_id)

                                # if verify successfully
                                if verify is not None:
                                    for client in connections:
                                        if client.id == self.id:
                                            client.socket.send(str.encode("Unlocking Accepted"))
                                            booking_status = "Collected"
                                            db.update_booking(verify["booking_id"], booking_status)

                                # if verify failed
                                else:
                                    for client in connections:
                                        if client.id == self.id:
                                            client.socket.send(str.encode("Unlocking Denied"))

                            # if the account information DOES NOT match that on cloud database
                            else:
                                for client in connections:
                                    if client.id == self.id:
                                        client.socket.send(str.encode("Your account or password is wrong! Please try again."))

                        # check if the data type is location
                        elif data_type == "location":
                            car_id = new_data["car_id"]
                            longitude = new_data["longitude"]
                            latitude = new_data["latitude"]
                            db.update_car_location(car_id, latitude, longitude)

                    # if the received data from agent_pi cannot loaded properly
                    except:
                        pass

    # Wait for new connections
    def newConnections(self, socket):
        while True:
            sock, address = socket.accept()
            global total_connections
            connections.append(self.Client(sock, address, total_connections, "Name", True))
            connections[len(connections) - 1].start()
            print("New connection at ID " + str(connections[len(connections) - 1]))
            total_connections += 1

    def Serve(self):
        # Get host and port
        # host = input("Host: ")
        # port = int(input("Port: "))

        # Create new server socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("192.168.0.3", 5001))
        sock.listen(5)

        # Create new thread to wait for connections
        newConnectionsThread = threading.Thread(target=self.newConnections, args=(sock,))
        newConnectionsThread.start()
