import socket
import threading
import os
import sys
from getpass import getpass
import time
from recognition import Recognition
from pick import pick
from location_use_case import Car_location


data = ""
connected = False
count = 1
progress = "."
start_time = time.time()

# Attempt connection to server of the master pi
while not connected:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # local host of the master pi
        sock.connect(("192.168.0.3", 5001))
        connected = True
        print("Successfully connected to Master Pi Server")
        time.sleep(5)

        # Wait for the incoming data from Master Pi server
        # .decode is used to turn the message from bytes to a string
        def receive(socket, signal):
            # if there is a signal, run the following coding
            while signal:
                try:
                    # receiving the data from agent_pi
                    data = socket.recv(200)
                    print("\n")
                    print(str(data.decode("utf-8")))
                    print("\n")

                except:
                    # show the message that signal is disconnected
                    print("You have been disconnected from the server")
                    signal = False
                    break

        # Function to gain the Mac address that connected to the raspberry pi (agent pi) from location_use_case.py
        # The gained value represents the address of the raspberry pi (agent pi) and send to master pi
        def location_update():
            map_initial_time = time.time()
            while connected:
                new_map_time = time.time() - map_initial_time

                # refresh the location data every minute
                if new_map_time >= 10:
                    locate = Car_location()

                    # Getting the latitude and longitude value of Mac
                    loc_data = locate.Get_Location()

                    # encode the location data and send it to Master pi
                    sock.sendall(str.encode(loc_data))
                    map_initial_time = time.time()


        # Create new thread to wait for data and wait for location update
        receiveThread = threading.Thread(target=receive, args=(sock, True))
        receiveThread.start()
        locationThread = threading.Thread(target=location_update)
        locationThread.start()

        # Loop for menu of agent pi in console and collect user inputs
        while True:
            clear = lambda: os.system('clear')
            title = 'Please select an option: '
            options = ['Unlock Booked Car', 'Return Car']
            option, index = pick(options, title)
            print(option)
            print("##########")
            print("########## \n")

            # if the option is 'Unlock Booked Car'
            if index == 0:
                status = "collected"

                title = 'Please select an authorization option: '
                options = ['use username and password', 'use face recognition']
                option, index = pick(options, title)
                print(option)
                print("##########")
                print("########## \n")

                # if the option is 'use username and password'
                if index == 0:
                    username = input("Insert Username :")
                    print("\n")

                    password = getpass("Insert password :")
                    print("\n")

                    customer_id = input("Insert your Customer ID :")
                    print("\n")

                    car_id = input("Insert Car ID :")
                    print("\n")

                    message = '{"type": "credentials", "status": "%s", "username": "%s", "password": "%s", "customer_id": "%s", "car_id": "%s"}' % (
                        status, username, password, customer_id, car_id)

                    # sending back the credentials data to Master Pi for data validation
                    # Master Pi will return the message of validation result
                    sock.sendall(str.encode(message))
                    time.sleep(10)
                    clear()

                # if the option is 'use face recognition'
                elif index == 1:
                    recog = Recognition()
                    data = recog.start_recognition(status)
                    sock.sendall(str.encode(data))
                    time.sleep(10)
                    clear()

            # if the option is 'Return Car'
            elif index == 1:
                status = "returned"
                title = 'Please select an authorization option: '
                options = ['use username and password', 'use face recognition']
                option, index = pick(options, title)
                print(option)
                print("##########")
                print("########## \n")

                # if the option is 'use username and password'
                if index == 0:
                    username = input("Insert Username :")
                    print("\n")

                    password = getpass("Insert password :")
                    print("\n")

                    customer_id = input("Insert your Customer ID :")
                    print("\n")

                    car_id = input("Insert Car ID :")
                    print("\n")

                    message = '{"type": "credentials", "status": "%s", "username": "%s", "password": "%s", "customer_id": "%s", "car_id": "%s"}' % (
                        status, username, password, customer_id, car_id)

                    # sending back the credentials data to Master Pi for data validation
                    # Master Pi will return the message of validation result
                    sock.sendall(str.encode(message))
                    time.sleep(10)
                    clear()

                # if the option is 'use face recognition'
                elif index == 1:
                    recog = Recognition()
                    data = recog.start_recognition(status)
                    sock.sendall(str.encode(data))
                    time.sleep(10)
                    clear()

    # if the agent pi still attempts to build the connection to server of the master pi
    except:
        newtime = time.time() - start_time

        # if the connection time has exceeded more than 3 seconds
        if newtime >= 3:
            # flush the "." which represents the number of attempt that connect to the master pi
            count += 1
            sys.stdout.write("Trying to connect: %s \r" % (progress * count))
            sys.stdout.flush()
            start_time = time.time()
