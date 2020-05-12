import socket
import threading
from database_utils import DatabaseUtils

try:
    import json
except ImportError:
    import simplejson as json 

#Variables for holding information about connections
connections = []
total_connections = 0

class ServerClass:
#Client class, new instance created for each connected client
#Each instance has the socket and address that is associated with items
#Along with an assigned ID and a name chosen by the client
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
        
        #Attempt to get data from client
        #If unable to, assume client has disconnected and remove him from server data
        #If able to and we get data back, print it in the server and send it back to every
        #client aside from the client that has sent it
        #.decode is used to convert the byte data into a printable string
        def run(self):
            while self.signal:
                try:
                    data = self.socket.recv(100)
                except:
                    print("Client " + str(self.address) + " has disconnected")
                    self.signal = False
                    connections.remove(self)
                    break
                if data != "":
                   # print("ID " + str(self.id) + ": " + str(data.decode("utf-8")))
                    newdata = json.loads(data)
                    #date = newdata["date"]
                    username = newdata["username"]
                    password = newdata["password"]
                    customer_id = newdata["customer_id"]
                    car_id = newdata["car_id"]
                    
                    db = DatabaseUtils()
                    userdata = db.login_account(username ,password)

                    if(userdata is not None):   
                        verify = db.validate_collection(customer_id,car_id)
                        if(verify is not None):
                            for client in connections:
                                if client.id == self.id:
                                    client.socket.send("unlocking accepted")
                        else:
                            for client in connections:
                                if client.id == self.id:
                                   client.socket.send("unlocking denied") 

                    else:
                        for client in connections:
                            if client.id == self.id:
                               client.socket.send("unlocking denied")
                      
    #Wait for new connections
    def newConnections(self ,socket):
        while True:
            sock, address = socket.accept()
            global total_connections
            connections.append(self.Client(sock, address, total_connections, "Name", True))
            connections[len(connections) - 1].start()
            print("New connection at ID " + str(connections[len(connections) - 1]))
            total_connections += 1

    def Serve(self):
        #Get host and port
        #host = input("Host: ")
        #port = int(input("Port: "))

        #Create new server socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1",5001))
        sock.listen(5)

        #Create new thread to wait for connections
        newConnectionsThread = threading.Thread(target = self.newConnections, args = (sock,))
        newConnectionsThread.start()
        


