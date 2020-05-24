====
MAIN
====

.. code-block:: python

from flask import Flask, render_template, request, redirect, url_for, session, flash
from calendar_api.calendar_api import google_calendar_api

import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


import os
from passlib.hash import sha256_crypt
from flask_googlemaps import GoogleMaps, Map
from database_utils import DatabaseUtils
from datetime import datetime
import re
from server import ServerClass
from decimal import Decimal

try:
    import json
except ImportError:
    import simplejson as json

app = Flask(__name__)
db = DatabaseUtils()
db.create_account_table()

# you can set key as config
app.config['GOOGLEMAPS_KEY'] = "AIzaSyA9CEaJcH6rooo1xohj-uE9ErU0KweRw-8"
app.config['SECRET_KEY'] = 'thisismysecretkey'

# Initialize Google map
GoogleMaps(app)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']



# --------------------------------------------LOGIN PAGE-----------------------------------------------------

# http://localhost:5000/carrental/ - this will be the login page, we need to use both GET and POST requests
@app.route('/')
@app.route('/carrental', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Remove session data, this will log the user out
    session.clear()
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST':
        # Create variables for easy access
        email = request.form['username']
        password = request.form['password']

        # query the account from the database by passing the input username and password
        account = db.login_account(email)

        # Check if the account exists in the accounts table of database
        # If account exists, redirect to home page
        if account:
            # Verifying hashed Password
            if sha256_crypt.verify(password, account['password']):
                # Create session data, we can access these data in other routes
                session['loggedin'] = True
                session['id'] = account['customer_id']
                session['firstname'] = account['first_name']
                session['lastname'] = account['last_name']
                session['email'] = account['email']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Account doesnt exist or username/password incorrect
                msg = 'Incorrect username/passwords!'

        # If account doesn't exist, show the error message and pass it to index.html
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


# --------------------------------------------LOGOUT PAGE-----------------------------------------------------

# http://localhost:5000/carrental/logout - this will be the logout page
@app.route('/carrental/logout')
def logout():
    # Remove session data, this will log the user out
    session.clear()
    # Redirect to the login page
    return redirect(url_for('login'))


# --------------------------------------------REGISTER PAGE-----------------------------------------------------

# http://localhost:5000/carrental/register - this will be the registration page,
# we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
# @app.route('/carrental/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST':
        # Create variables for easy access
        firstname = request.form['first_name']
        lastname = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        hashedpassword = sha256_crypt.using(rounds=1000).hash(password)

        # check whether the email has already registered in the database
        account = db.get_an_user(email)

        # If account exists show error and validation checks
        if account:
            msg = 'Account with this email has already existed!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not firstname or not lastname or not email or not password:
            msg = 'Please fill out the form!'

        # if account doesn't existed, show the successful message and back to the login page
        else:
            db.insert_account(firstname, lastname, email, hashedpassword)
            msg = 'You have successfully registered!'
            return render_template('index.html', msg=msg)

    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# --------------------------------------------HOME PAGE-----------------------------------------------------

# http://localhost:5000/carrental/home - this will be the home page, only accessible for loggedin users
@app.route('/carrental/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is logged in show them the home page
        return render_template('home.html', username=session['firstname'])
    # User is not logged in and redirect to login page
    return redirect(url_for('login'))


# --------------------------------------------PROFILE PAGE-----------------------------------------------------

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for logged in users
@app.route('/carrental/profile')
def profile():
    # Check if user is logged in
    if 'loggedin' in session:
        account = db.get_an_user(session['email'])

        # Show the profile page with account info
        return render_template('profile.html', account=account, username=session['firstname'])

    # User is not logged in redirect to login page
    return redirect(url_for('login'))


# --------------------------------------------SEARCH PAGE-----------------------------------------------------

# http://localhost:5000/carrental/search - this will be the search page, only accessible for logged in users
@app.route('/carrental/search', methods=['GET', 'POST'])
@app.route('/carrental/search/<carid>/<amount>')
def search(carid=0, amount=0):
    # Check if user is logged in and has filled the form
    if 'loggedin' in session:
        cars = []
        date_format = "%d-%m-%Y %H:%M"

        # this if statement happens when the user click the "Search Now" button
        if request.method == 'POST':
            # get the user input selection data from html file and set them into different variables
            car_make = request.form['carMake']
            car_type = request.form['carType']
            car_colour = request.form['carColor']
            car_seat = request.form['carSeat']
            pickup_date = request.form['pickupDate']
            pickup_time = request.form['pickupTime']
            return_date = request.form['returnDate']
            return_time = request.form['returnTime']

            # Create session data, we can access these data in other routes
            if car_type or car_make or car_colour or car_seat:
                session['car_make'] = request.form['carMake']
                session['car_type'] = request.form['carType']
                session['car_colour'] = request.form['carColor']
                session['car_seat'] = request.form['carSeat']
                session['pickup_date'] = request.form['pickupDate']
                session['pickup_time'] = request.form['pickupTime']
                session['return_date'] = request.form['returnDate']
                session['return_time'] = request.form['returnTime']

                # check the time
                date_one = datetime.strptime(pickup_date + ' ' + pickup_time, date_format)
                date_two = datetime.strptime(return_date + ' ' + return_time, date_format)
                days_diff = date_two - date_one
                get_hours = days_diff.total_seconds() / 60 ** 2

                # Setting Renting Time Length and the display message
                session['renting_length'] = "Your renting time period is: " + str(days_diff) + " hours"

                conflict = db.check_booking_dates_conflict(str(pickup_date), str(return_date))
                print(conflict)

                # check whether the car has been booked within the input time period
                # if yes, conflict['count'] will be greater than 0
                if conflict['count'] > 0:

                    # get the car by filtering out those booked car within that input period
                    cars = db.get_all_available_car_type(str(car_make), str(car_type), str(car_colour), str(car_seat), str(pickup_date), str(return_date))

                    if not cars:
                        flash("No cars available for your search range, Sorry!")
                        return redirect(url_for('search'))
                    elif cars:
                        for value in cars:
                            value["price_total"] = float(value["price_per_hour"]) * float(get_hours)

                # if there is no conflict
                else:
                    cars = db.get_all_available_car_type(str(car_make), str(car_type), str(car_colour), str(car_seat), str(pickup_date), str(return_date))
                    if not cars:
                        flash("No cars available for your search range, Sorry!")
                        return redirect(url_for('search'))
                    elif cars:
                        for value in cars:
                            value["price_total"] = float(value["price_per_hour"]) * float(get_hours)

        # this if statement happens when user decides to book a car from the search result after the searching process
        if carid != 0:
            # Need changes in the order
            db.insert_booking(session['id'], carid, session['pickup_date'], session['pickup_time'],
                              session['return_date'], session['return_time'], 'booked', amount)

            # Removing search query from the session
            session.pop('car_make', None)
            session.pop('car_type', None)
            session.pop('car_colour', None)
            session.pop('car_seat', None)
            session.pop('pickup_date', None)
            session.pop('pickup_time', None)
            session.pop('return_date', None)
            session.pop('return_time', None)
            session.pop('renting_length', None)

            return redirect(url_for('bookinghistory'))

        # this if statement happens every time before user entering to New Booking Page
        # Removing search query from the session
        if request.method != 'POST' and carid == 0:
            session.pop('car_make', None)
            session.pop('car_type', None)
            session.pop('car_colour', None)
            session.pop('car_seat', None)
            session.pop('pickup_date', None)
            session.pop('pickup_time', None)
            session.pop('return_date', None)
            session.pop('return_time', None)
            session.pop('renting_length', None)


        # reload the new_booking page with showing the searching result
        return render_template('new_booking.html', username=session['firstname'], carlist=cars)

    # User is not logged in and redirect to login page
    return redirect(url_for('login'))


# --------------------------------------------BOOKING HISTORY PAGE-----------------------------------------------------

# http://localhost:5000/carrental/bookinghistory - this will be the booking history page,
# only accessible for logged in users
@app.route('/carrental/bookinghistory')
@app.route('/carrental/bookinghistory/<bookingid>')
def bookinghistory(bookingid=0):
    # Check if user is loggedin
    if 'loggedin' in session:
        customerid = session['id']

        # check the booking history of logged in customer
        booking_history = db.get_customer_booking_history(customerid)

        if bookingid != 0:
            db.update_booking(bookingid, "booked")
            booking_history = db.get_customer_booking_history(customerid)

        # Show the Cars List
        return render_template('booking_history.html', username=session['firstname'], history=booking_history)

    # User is not logged in redirect to login page
    return redirect(url_for('login'))


# --------------------------------------------BOOKING HISTORY PAGE-----------------------------------------------------

@app.route('/carrental/location')
def map_bounded():
    # Check if user is loggedin
    if 'loggedin' in session:
        # creating a map in the view
        cars = db.get_all_car_location()
        print(cars)
        # getting car's location information from cloud database
        location_detail = [{
            "infobox": str(item["infobox"]),
            "lat": float(item["lat"]),
            "lng": float(item["lng"])} for item in cars]

        # initialize the google map page
        carsmap = Map(
            identifier="carsmap",
            lat=-37.8047,
            lng=144.9580,
            zoom=13,
            style="height:1000px;width:100%;margin-left:auto;margin-right:auto;margin-top:auto;margin-bottom:auto",
            markers=location_detail
        )
        return render_template('location.html', carsmap=carsmap)

    # User is not logged in and redirect to login page
    return redirect(url_for('login'))


if __name__ == "__main__":
    sv = ServerClass()
    sv.Serve()
    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='127.0.0.1', port=port, debug=False)
    app.run(debug=False)

======
SERVER
======

.. code-block:: python

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


==============
DATABASE_UTILS
==============

.. code-block:: python

from passlib.hash import sha256_crypt
from datetime import datetime
import pymysql  # MySQLdb or pymysql both able to use


class DatabaseUtils:
    HOST = "34.87.232.2"  # google cloud IP address
    USER = "root"  # google cloud sql user name
    PASSWORD = "123456789"  # google cloud sql password
    DATABASE = "Pythonlogin"

    def __init__(self, connection=None):
        if connection is None:
            connection = pymysql.connect(DatabaseUtils.HOST, DatabaseUtils.USER,
                                         DatabaseUtils.PASSWORD, DatabaseUtils.DATABASE)
        self.connection = connection

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def create_account_table(self):
        with self.connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS customers")
            cursor.execute("DROP TABLE IF EXISTS cars_list")
            cursor.execute("DROP TABLE IF EXISTS bookings")

            # Creating default password and converting to hashing
            hashedpassword = sha256_crypt.using(rounds=1000).hash("123")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `customers` (
                    `customer_id` int(11) NOT NULL AUTO_INCREMENT,
                    `first_name` varchar(100) NOT NULL,
                    `last_name` varchar(100) NOT NULL,
                    `email` varchar(100) NOT NULL,
                    `password` text NOT NULL,
                    PRIMARY KEY (`customer_id`),
                    UNIQUE(`email`),
                    KEY `id` (`customer_id`)
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
            """)
            cursor.execute(
                "INSERT IGNORE INTO `customers` VALUES (NULL, 'Wayne', 'Wayne', 'abc@gmail.com', '" + hashedpassword + "')")
            cursor.execute(
                "INSERT IGNORE INTO `customers` VALUES (NULL, 'John', 'Mathew', 'john@gmail.com', '" + hashedpassword + "')")
            cursor.execute(
                "INSERT IGNORE INTO `customers` VALUES (NULL, 'Anna', 'Williams', 'anna@gmail.com', '" + hashedpassword + "')")
            cursor.execute(
                "INSERT IGNORE INTO `customers` VALUES (NULL, 'Harry', 'Robert', 'harry@gmail.com', '" + hashedpassword + "')")
            cursor.execute(
                "INSERT IGNORE INTO `customers` VALUES (NULL, 'Charlie', 'William', 'carlie@gmail.com', '" + hashedpassword + "')")
            cursor.execute(
                "INSERT IGNORE INTO `customers` VALUES (NULL, 'Oliver', 'Michelle', 'oliver@gmail.com', '" + hashedpassword + "')")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `cars_list` (
                    `car_id` int(15) NOT NULL AUTO_INCREMENT,
                    `make_name` varchar(100) NOT NULL,
                    `model_name` varchar(100) DEFAULT NULL,
                    `seating_capacity` varchar(1) DEFAULT NULL,
                    `colour` varchar(20) DEFAULT NULL,
                    `car_type` varchar(20) DEFAULT NULL COMMENT '1:Sedan | 2:Hatch | 3:SUV',
                    `price_per_hour` decimal(10,2) NOT NULL,
                    `registration_no` varchar(10) DEFAULT NULL,
                    `status` varchar(15) NOT NULL,
                    `latitude` varchar(20)  NOT NULL,
                    `longitude` varchar(20) NOT NULL,
                    UNIQUE(`registration_no`),
                    PRIMARY KEY (`car_id`)                    
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
            """)
            cursor.execute("INSERT IGNORE INTO `cars_list` VALUES (NULL, 'Toyota', 'Camry', '4', 'Red', 'Sedan', 15, "
                           "'Flinders', 'available' , -35.8183, 146.9671);")
            cursor.execute("INSERT IGNORE INTO `cars_list` VALUES (NULL, 'Mazda', 'CX-5', '4', 'Yellow', 'SUV', 20, "
                           "'Box hills', 'available', -37.8181, 145.1239);")
            cursor.execute(
                "INSERT IGNORE INTO `cars_list` VALUES (NULL, 'Nissan', 'Altima', '5', 'Black', 'Sedan', 10, "
                "'North Melbourne', 'available', -37.7992, 144.9467);")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `bookings` (
                    `booking_id` int(11) NOT NULL AUTO_INCREMENT,
                    `customer_id` int(11) NOT NULL,
                    `car_id` int(11) NOT NULL,
                    `pickup_date` DATE NOT NULL,
                    `pickup_time` varchar(30) NOT NULL,
                    `return_date` DATE NOT NULL,
                    `return_time` varchar(30) NOT NULL,
                    `booking_amount` decimal(10,2) NOT NULL,
                    `booking_status` varchar(30) NOT NULL,
                    `canceled_date_time` timestamp NULL DEFAULT NULL,
                    PRIMARY KEY (`booking_id`)                  
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
            """)

        self.connection.commit()

    def insert_account(self, firstname, lastname, email, password):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO customers VALUES (NULL, %s, %s, %s, %s)",
                           (firstname, lastname, email, password))
        self.connection.commit()

    def login_account(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM customers WHERE email = %s", (email))

        return cursor.fetchone()

    def get_an_user(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM customers WHERE email = %s", email)

        return cursor.fetchone()

    def get_all_available_cars(self):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM cars_list WHERE status = 'available'")

        return cursor.fetchall()

    # show a list of cars that current user has booked
    def get_customer_booking_history(self, customer_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT b.booking_id, c.first_name, c.last_name, b.pickup_date, b.return_date, b.pickup_time, "
                       "b.booking_amount, b.booking_status, cl.make_name, cl.model_name "
                       "FROM customers c "
                       "JOIN bookings b on c.customer_id = b.customer_id JOIN "
                       "cars_list cl on b.car_id = cl.car_id "
                       "WHERE c.customer_id = %s "
                       "ORDER BY b.pickup_date DESC",
                       customer_id)

        return cursor.fetchall()

    def check_booking_dates_conflict(self, pickup_date, return_date):
        conflicts_arr = {}

        # Reformatting the datetime data of pickup_date and return_date
        pickup_oldformat = pickup_date
        pickup_datetimeobject = datetime.strptime(pickup_oldformat, '%d-%m-%Y')
        pickup_newformat = pickup_datetimeobject.strftime('%Y-%m-%d')

        return_oldformat = return_date
        return_datetimeobject = datetime.strptime(return_oldformat, '%d-%m-%Y')
        return_newformat = return_datetimeobject.strftime('%Y-%m-%d')

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            "SELECT car_id FROM bookings WHERE (%s <= return_date AND %s >= pickup_date) OR (%s <= return_date "
            "AND %s >= pickup_date)",
            (pickup_newformat, return_newformat, pickup_newformat, return_newformat))
        count = cursor.rowcount

        if count > 0:
            conflicts_arr['count'] = count
            conflicts_arr['cars'] = cursor.fetchall()
        else:
            conflicts_arr['count'] = count
            conflicts_arr['cars'] = ''

        return conflicts_arr

    def get_all_available_car_type(self, car_make, car_type, car_colour, car_seat, pickup_date, return_date):

        mainquery = "SELECT * FROM cars_list WHERE status = 'available' AND car_id NOT IN (SELECT car_id FROM bookings WHERE ( %s <= return_date AND %s >= pickup_date) OR ( %s <= return_date AND %s >= pickup_date))"

        if car_make != "any":
            mainquery += " AND make_name = '" + car_make + "' "

        if car_type != "any":
            mainquery += " AND car_type = '" + car_type + "' "

        if car_colour != "any":
            mainquery += " AND colour = '" + car_colour + "' "

        if car_seat != "any":
            mainquery += " AND seating_capacity = '" + car_seat + "' "

        pickup_oldformat = pickup_date
        pickup_datetimeobject = datetime.strptime(pickup_oldformat, '%d-%m-%Y')
        pickup_newformat = pickup_datetimeobject.strftime('%Y-%m-%d')

        return_oldformat = return_date
        return_datetimeobject = datetime.strptime(return_oldformat, '%d-%m-%Y')
        return_newformat = return_datetimeobject.strftime('%Y-%m-%d')

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(mainquery, (pickup_newformat, return_newformat, pickup_newformat, return_newformat))

        return cursor.fetchall()

    def insert_booking(self, customer_id, car_id, pickupDate, piuckup_time, returnDate, return_time, booking_status,
                       booking_amount):
        with self.connection.cursor() as cursor:
            pickup_oldformat = pickupDate
            pickup_datetimeobject = datetime.strptime(pickup_oldformat, '%d-%m-%Y')
            pickup_newformat = pickup_datetimeobject.strftime('%Y-%m-%d')

            return_oldformat = returnDate
            return_datetimeobject = datetime.strptime(return_oldformat, '%d-%m-%Y')
            return_newformat = return_datetimeobject.strftime('%Y-%m-%d')

            cursor.execute(
                "insert into bookings (customer_id, car_id, pickup_date, pickup_time, return_date, return_time, booking_status, booking_amount) values (%s,%s,%s,%s,%s,%s,%s,%s)",
                (customer_id, car_id, pickup_newformat, str(piuckup_time), return_newformat, str(return_time),
                 booking_status, booking_amount))
        self.connection.commit()

    def update_booking(self, bookingid, booking_status):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("UPDATE bookings "
                       "SET booking_status = %s "
                       "WHERE booking_id = %s",
                       (booking_status, bookingid))

        self.connection.commit()

    # validate whether the user has booked the car and fetch that information
    def validate_collection(self, customer_id, car_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select * "
                       "from bookings "
                       "where "
                       "customer_id = %s "
                       "AND car_id = %s "
                       "AND booking_status = 'booked'",
                       (customer_id, car_id))

        return cursor.fetchone()

    # validate whether the user has collected the car and fetch that information
    def validate_return_car(self, customer_id, car_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select * "
                       "from bookings "
                       "where "
                       "customer_id = %s "
                       "AND car_id = %s "
                       "AND booking_status = 'collected'",
                       (customer_id, car_id))

        return cursor.fetchone()

    def get_all_car_location(self):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select `registration_no` as `infobox`,`latitude` as `lat`,`longitude` as `lng`"
                       "from cars_list ")

        return cursor.fetchall()

    def update_car_location(self, car_id, latitude, longitude):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("UPDATE cars_list "
                       "SET latitude = %s ,"
                       "longitude = %s "
                       "WHERE car_id = %s ",
                       (latitude, longitude, car_id))
        self.connection.commit()

