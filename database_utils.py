from flask import Flask, render_template, request, redirect, url_for, session
import pymysql  # MySQLdb  # pymysql


class DatabaseUtils:
    app = Flask(__name__)

    HOST = "35.201.23.126"  # google cloud IP address
    USER = "root"  # google cloud sql user name
    PASSWORD = "andrewishandsome"  # google cloud sql password
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
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `Cust_User` (
                    `id` int(11) NOT NULL AUTO_INCREMENT,
                    `username` varchar(50) NOT NULL,
                    `password` varchar(255) NOT NULL,
                    `email` varchar(100) NOT NULL,
                    PRIMARY KEY (`username`),
                    KEY `id` (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `Booking` (
                    `bookingId` int(50) NOT NULL AUTO_INCREMENT,
                    `username` varchar(100) DEFAULT NULL,
                    `Cab` varchar(100) DEFAULT NULL,
                    `startDate` varchar(100) DEFAULT NULL,
                    `endDate` varchar(100) DEFAULT NULL,
                    `Pickup_time` varchar(100) DEFAULT NULL,
                    `Pickup_location` varchar(100) DEFAULT NULL,
                    `Drop_off_location` varchar(100) DEFAULT NULL,
                    `driverId` int(50) DEFAULT NULL,
                    `carid` varchar(100) DEFAULT NULL,
                    `cab_route` varchar(500) DEFAULT NULL,
                    PRIMARY KEY (`bookingId`),
                    KEY `username` (`username`),
                    KEY `driverId` (`driverId`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
            """)  # CONSTRAINT `Booking_ibfk_2` FOREIGN KEY (`driverId`) REFERENCES `Driver` (`driverId`)
            # CONSTRAINT `Booking_ibfk_1` FOREIGN KEY (`username`) REFERENCES `Cust_User` (`username`)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `Car` (
                    `Car_id` varchar(100) NOT NULL,
                    `model_name` varchar(100) DEFAULT NULL,
                    `registration_no` varchar(100) DEFAULT NULL,
                    `seating_capacity` varchar(100) DEFAULT NULL,
                    `Car_type` varchar(100) DEFAULT NULL,
                    `price_per_km` varchar(100) DEFAULT NULL,
                    `status` varchar(100) DEFAULT 'Available',
                    PRIMARY KEY (`Car_id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
            """)
        self.connection.commit()

    def insert_account(self, username, password, email):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO Cust_User VALUES (NULL, %s, %s, %s)", (username, password, email,))
        self.connection.commit()

    def check_exist_username(self, username):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM Cust_User WHERE username = %s', (username,))

        return cursor.fetchone()

    def login_account(self, username, password):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM Cust_User WHERE username = %s AND password = %s", (username, password,))

        return cursor.fetchone()

    def get_an_user(self, username):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM Cust_User WHERE username = %s", (username,))

        return cursor.fetchone()

    def get_available_car(self, car_name):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT Car_id FROM Car WHERE status = 'Available' and Car_type = %s ", [car_name])

        return cursor.fetchone()

    def update_car(self, car_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("UPDATE Car SET status = 'BOOKED' WHERE Car_id = %s", [car_id])

        self.connection.commit()

    def insert_booking(self, userId, cab_name, startDate, endDate, time, pickupLocation, dropoffLocation):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO Booking(userId,Cab,startDate,endDate,Pickup_time,Pickup_location,"
                           "Drop_off_location) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                           (userId, cab_name, startDate, endDate, time, pickupLocation, dropoffLocation))
        self.connection.commit()


