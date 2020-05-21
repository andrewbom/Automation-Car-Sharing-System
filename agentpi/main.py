import socket
import threading
import os
import sys
import datetime
from getpass import getpass
import time
from  recognition import Recognition
from pick import pick
from database_utils import Database_utils
from location_use_case import Car_location

data = ""
connected = False
count = 1
progress = "."

#Wait for incoming data from server
#.decode is used to turn the message in bytes to a string
def receive(socket, signal):
    while signal:
        try:
            data = socket.recv(32)
            print("\n")
            print(str(data.decode("utf-8"))) 
            print("\n")
            
        except:
            print("You have been disconnected from the server")
            signal = False
            break
 
 
def location_update():
   map_initial_time = time.time()
   while(connected == True):
          new_map_time = time.time()- map_initial_time
          if new_map_time >= 10:
              locate = Car_location()
              loc_data = locate.Get_Location()
              #print(loc_data)
              
              sock.sendall(str.encode(loc_data))
              #print("location data sent")
              map_initial_time = time.time()  
              
                       
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
    sock.connect(("192.168.0.3", 5001))
    connected = True
    print("Connected to Server")
    
except:
    print("Connection not established")
    sys.stdout.write("Trying to connect: %s \r" % (progress*count) )
    sys.stdout.flush()

start_time = time.time()
sys.stdout.write("Trying to connect: %s \r" % (progress*count) )
sys.stdout.flush()

#Attempt connection to server
while(connected == False):
       try:
           sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
           sock.connect(("192.168.0.3", 5001))
           connected = True
           print("Connected to Server")
           
       except:
           newtime = time.time()- start_time 
           if newtime >= 3:
                  count+=1
                  sys.stdout.write("Trying to connect: %s \r" % (progress*count) )
                  sys.stdout.flush()
                  start_time = time.time()
                  
#Create new thread to wait for data
receiveThread = threading.Thread(target = receive, args = (sock, True))
receiveThread.start()
locationThread = threading.Thread(target = location_update)
locationThread.start()

#Send data to server
#str.encode is used to turn the string message into bytes so it can be sent across the network
while True:   
       
   # message = '{"customer_id":"6","car_id":"1","username":"abc@gmail.com","password":"123"}'
   clear = lambda: os.system('clear') 
   title = 'Please select an authorization option: '
   options = ['use username and password', 'use face recognition']
   option, index = pick(options, title)
   print(option)
   print("##########")
   print("########## \n")
   
   if(index == 0):
       username = input("Insert Username :")
       print("\n")
       
       password = getpass("Insert password :")
       print("\n")

       customer_id = input("Insert your Customer ID :")
       print("\n")    

       car_id = input("Insert Car ID :")
       print("\n")
       
       #db =  Database_utils()
       #cardata = db.get_car_data()
       #userdata =  db.get_user_data()
       #car_id = cardata[1]
       #customer_id = userdata[3]

       message = '{"type":"credentials","username":"%s","password":"%s","customer_id":"%s","car_id":"%s"}'% (username, password, customer_id, car_id)
       print("\n")
       print(data)
       sock.sendall(str.encode(message))
       time.sleep(10)
       clear()
     
   elif(index == 1):
       recog = Recognition()
       data = recog.start_recognition()
       #message = '{"username":"%s","password":"%s","car_id":"%s"}'% (username,password,car_id)
       sock.sendall(str.encode(data))
       print(data)
       time.sleep(10)
       clear()
       
      
        
    
   

   

   

