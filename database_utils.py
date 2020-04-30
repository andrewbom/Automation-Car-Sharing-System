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
                CREATE TABLE IF NOT EXISTS `Cars_list` (
                    `car_id` int(15) NOT NULL AUTO_INCREMENT,
                    `make_name` varchar(100) NOT NULL,
                    `model_name` varchar(100) DEFAULT NULL,
                    `registration_no` varchar(10) DEFAULT NULL,
                    `seating_capacity` varchar(1) DEFAULT NULL,
                    `car_type` int(1) DEFAULT NULL COMMENT '1:Sedan | 2:Hatch | 3:SUV',
                    `price_per_km` varchar(10) DEFAULT NULL,
                    `status` int(1) DEFAULT NULL COMMENT '1:Available | 2:Not Available',
                    PRIMARY KEY (`car_id`)                    
                ) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8;
            """)
            cursor.execute("""
                INSERT INTO `Cars_list` VALUES (NULL, 'Toyota', 'Camry', 'ASDQWE', '4', 1, '15', 1);

            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `Booking` (
                    `booking_id` int(11) NOT NULL AUTO_INCREMENT,
                    `start_date` varchar(30) NOT NULL,
                    `end_date` varchar(30) NOT NULL,
                    `pickup_time` varchar(30) NOT NULL,
                    `booking_amount` decimal(10,0) NOT NULL,
                    `booking_status` int(11) NOT NULL COMMENT '1:Booked | 2:Canceled',
                    `canceled_date_time` timestamp NULL DEFAULT NULL,
                    `username` varchar(50),
                    `car_id` int(15),
                    PRIMARY KEY (`booking_id`),
                    FOREIGN KEY (`username`) REFERENCES Cust_User(`username`) ON UPDATE CASCADE,
                    FOREIGN KEY (`car_id`) REFERENCES Cars_list(`car_id`) ON UPDATE CASCADE                    
                ) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8;
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

    def get_available_car(self, car_type):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT car_id FROM Cars_list WHERE status = 1 and car_type = %d ", car_type)

        return cursor.fetchone()

    def update_car(self, car_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("UPDATE Cars_list SET status = 2 WHERE car_id = %s", car_id)

        self.connection.commit()

    def insert_booking(self, userId, car_id, startDate, endDate, _time):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO Booking(username,car_id,start_date,end_date,pickup_time) "
                           "VALUES (%s,%s,%s,%s,%s)",
                           (userId, car_id, startDate, endDate, _time))
            cursor.execute("UPDATE Booking SET booking_status = 1 WHERE car_id = %s", car_id)
        self.connection.commit()


