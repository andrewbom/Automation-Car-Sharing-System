import socket
import threading
from database_utils import DatabaseUtils
from passlib.hash import sha256_crypt

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
                    data = self.socket.recv(200)
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
                        data_type = new_data["type"]

                        # There will be 2 types of data that send by agent pi, they are: "credentials" and "location"
                        # check if the data type is "credentials"
                        if data_type == "credentials":

                            # assigning the variables to the user account information that entered in the agent_pi
                            username = new_data["username"]
                            password = new_data["password"]
                            customer_id = new_data["customer_id"]
                            car_id = new_data["car_id"]

                            # checking whether the user account information of agent pi match that on cloud database
                            user_data = db.login_account(username)

                            # if the account information successfully match that on cloud database
                            if user_data is not None and sha256_crypt.verify(password, user_data['password']):

                                # Request from agent pi for unlocking the car
                                if new_data["status"] == "collected":
                                    # validate whether the user has booked the car
                                    verify = db.validate_collection(customer_id, car_id)

                                    # if verify successfully
                                    if verify is not None:
                                        for client in connections:
                                            if client.id == self.id:
                                                client.socket.send(str.encode("The Car has successfully unlocked."))
                                                db.update_booking(verify["booking_id"], new_data["status"])
                                    # if verify failed
                                    else:
                                        for client in connections:
                                            if client.id == self.id:
                                                client.socket.send(str.encode("Unlocking Denied"))

                                # Request from agent pi for returning the car
                                if new_data["status"] == "returned":
                                    # validate whether the user has collected the car before
                                    verify = db.validate_return_car(customer_id, car_id)

                                    # if verify successfully
                                    if verify is not None:
                                        for client in connections:
                                            if client.id == self.id:
                                                client.socket.send(str.encode("Car Return Successfully."))
                                                # booking_status = new_data["status"]
                                                db.update_booking(verify["booking_id"], new_data["status"])
                                    # if verify failed
                                    else:
                                        for client in connections:
                                            if client.id == self.id:
                                                client.socket.send(str.encode("Car Return Denied"))

                            # if the account information DOES NOT match that on cloud database
                            else:
                                for client in connections:
                                    if client.id == self.id:
                                        client.socket.send(str.encode("Username or password is incorrect"))

                        # check if the data type is "location"
                        elif data_type == "location":
                            car_id = new_data["car_id"]
                            longitude = new_data["longitude"]
                            latitude = new_data["latitude"]
                            db.update_car_location(car_id, latitude, longitude)

                        elif data_type == "face recog fail":
                            for client in connections:
                                if client.id == self.id:
                                    client.socket.send(str.encode("Facial Recognition fail."))

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
        # Create new server socket .... Ensure socket option is set to reusable address   
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("192.168.1.7", 5001))
        sock.listen(5)

        # Create new thread to wait for connections
        newConnectionsThread = threading.Thread(target=self.newConnections, args=(sock,))
        newConnectionsThread.start()
