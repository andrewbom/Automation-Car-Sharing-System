from flask import Flask, render_template, request, redirect, url_for, session
import pymysql  # MySQLdb  # pymysql


class DatabaseUtils:
    app = Flask(__name__)

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
            # cursor.execute("DROP TABLE customers;")
            cursor.execute("DROP TABLE cars_list;")
            cursor.execute("DROP TABLE bookings;")

            #### I removed the username field
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `customers` (
                    `customer_id` int(11) NOT NULL AUTO_INCREMENT,
                    `first_name` varchar(100) NOT NULL,
                    `last_name` varchar(100) NOT NULL,
                    `email` varchar(100) NOT NULL,
                    `password` varchar(50) NOT NULL,
                    PRIMARY KEY (`customer_id`),
                    UNIQUE(`email`),
                    KEY `id` (`customer_id`)
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
            """)
            cursor.execute("INSERT IGNORE INTO `customers` VALUES (NULL, 'John', 'Mathew', 'john@gmail.com', '123');")
            cursor.execute("INSERT IGNORE INTO `customers` VALUES (NULL, 'Anna', 'Williams', 'anna@gmail.com', '123');")
            cursor.execute("INSERT IGNORE INTO `customers` VALUES (NULL, 'Harry', 'Robert', 'harry@gmail.com', '123');")
            cursor.execute("INSERT IGNORE INTO `customers` VALUES (NULL, 'Charlie', 'William', 'carlie@gmail.com', '123');")
            cursor.execute("INSERT IGNORE INTO `customers` VALUES (NULL, 'Oliver', 'Michelle', 'oliver@gmail.com', '123');")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `cars_list` (
                    `car_id` int(15) NOT NULL AUTO_INCREMENT,
                    `make_name` varchar(100) NOT NULL,
                    `model_name` varchar(100) DEFAULT NULL,
                    `registration_no` varchar(10) DEFAULT NULL,
                    `seating_capacity` varchar(1) DEFAULT NULL,
                    `car_type` int(1) DEFAULT NULL COMMENT '1:Sedan | 2:Hatch | 3:SUV',
                    `price_per_km` decimal(10,2) NOT NULL,
                    `status` varchar(10) NOT NULL,
                    UNIQUE(`registration_no`),
                    PRIMARY KEY (`car_id`)                    
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
            """)
            cursor.execute("INSERT IGNORE INTO `cars_list` VALUES (NULL, 'Toyota', 'Camry', '1AB 2CD', '4', 1, '15', 'Available');")
            cursor.execute("INSERT IGNORE INTO `cars_list` VALUES (NULL, 'Mazda', 'CX-5', '2YM 5CD', '4', 3, '20', 'Available');")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `bookings` (
                    `booking_id` int(11) NOT NULL AUTO_INCREMENT,
                    `user_id` int(11) NOT NULL,
                    `car_id` int(11) NOT NULL,
                    `start_date` varchar(30) NOT NULL,
                    `end_date` varchar(30) NOT NULL,
                    `pickup_time` varchar(30) NOT NULL,
                    `booking_amount` decimal(10,2) NOT NULL,
                    `booking_status` varchar(30) NOT NULL,
                    `canceled_date_time` timestamp NULL DEFAULT NULL,
                    PRIMARY KEY (`booking_id`)                  
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
            """)
            cursor.execute("INSERT IGNORE INTO `bookings` VALUES (NULL, 1, 2, '07-04-2020', '10-04-2020', '13:45', '155.00', 'booked', NULL);")
            cursor.execute("INSERT IGNORE INTO `bookings` VALUES (NULL, 1, 2, '10-03-2020', '15-03-2020', '13:45', '123.00', 'Canceled', NULL);")

        self.connection.commit()

    def insert_account(self, firstname, lastname, email, password):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO customers VALUES (NULL, %s, %s, %s, %s)", (firstname, lastname, email, password))
        self.connection.commit()

    def check_exist_username(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM customers WHERE email = %s', (email))

        return cursor.fetchone()

    def login_account(self, email, password):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM customers WHERE email = %s AND password = %s", (email, password))

        return cursor.fetchone()

    def get_an_user(self, username):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM Cust_User WHERE username = %s", (username))

        return cursor.fetchone()

    def get_all_available_cars(self):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM cars_list WHERE status = 'Available'")

        return cursor.fetchall()

    def get_customer_booking_history(self, customerid):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM bookings b INNER JOIN cars_list c ON b.car_id = c.car_id")

        # cursor.execute("SELECT bookings.*, cars_list.* FROM bookings b INNER JOIN cars_list c ON b.car_id = c.car_id WHERE user_id = %s", (customerid))

        # SELECT Orders.OrderID, Customers.CustomerName, Orders.OrderDate
        # FROM Orders
        # INNER JOIN Customers ON Orders.CustomerID=Customers.CustomerID;

        return cursor.fetchall()

    def get_available_car(self, car_type):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM cars_list WHERE status = 1 and car_type = %s", car_type)

        return cursor.fetchall()

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


