from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
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
            cursor.execute("DROP TABLE customers;")
            cursor.execute("DROP TABLE cars_list;")
            cursor.execute("DROP TABLE bookings;")

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
                    `seating_capacity` varchar(1) DEFAULT NULL,
                    `colour` varchar(20) DEFAULT NULL,
                    `car_type` int(1) DEFAULT NULL COMMENT '1:Sedan | 2:Hatch | 3:SUV',
                    `price_per_hour` decimal(10,2) NOT NULL,
                    `registration_no` varchar(10) DEFAULT NULL,
                    `status` varchar(15) NOT NULL,
                    UNIQUE(`registration_no`),
                    PRIMARY KEY (`car_id`)                    
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
            """)
            cursor.execute("INSERT IGNORE INTO `cars_list` VALUES (NULL, 'Toyota', 'Camry', '4', 'Red', 1, 15, '1AB 2CD', 'available');")
            cursor.execute("INSERT IGNORE INTO `cars_list` VALUES (NULL, 'Mazda', 'CX-5', '4', 'Yellow', 3, 20, '2YM 5CD', 'available');")
            cursor.execute("INSERT IGNORE INTO `cars_list` VALUES (NULL, 'Nissan', 'Altima', '5', 'Black', 1, 10, '5GH 3XC', 'available');")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `bookings` (
                    `booking_id` int(11) NOT NULL AUTO_INCREMENT,
                    `customer_id` int(11) NOT NULL,
                    `car_id` int(11) NOT NULL,
                    `start_date` DATE NOT NULL,
                    `end_date` DATE NOT NULL,
                    `pickup_time` varchar(30) NOT NULL,
                    `booking_amount` decimal(10,2) NOT NULL,
                    `booking_status` varchar(30) NOT NULL,
                    `canceled_date_time` timestamp NULL DEFAULT NULL,
                    PRIMARY KEY (`booking_id`)                  
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
            """)
            # cursor.execute("INSERT IGNORE INTO `bookings` VALUES (NULL, 1, 1, '07-04-2020', '10-04-2020', '13:45', "
            #                "'155.00', 'booked', NULL);")
            # cursor.execute("INSERT IGNORE INTO `bookings` VALUES (NULL, 1, 2, '10-03-2020', '15-03-2020', '13:45', "
            #                "'123.00', 'booked', NULL);")

        self.connection.commit()

    def insert_account(self, firstname, lastname, email, password):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO customers VALUES (NULL, %s, %s, %s, %s)",
                           (firstname, lastname, email, password))
        self.connection.commit()

    def check_exist_username(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM customers WHERE email = %s', email)

        return cursor.fetchone()

    def login_account(self, email, password):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM customers WHERE email = %s AND password = %s", (email, password))

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
        cursor.execute("SELECT b.booking_id, c.first_name, c.last_name, b.start_date, b.end_date, b.pickup_time, "
                       "b.booking_amount, b.booking_status, cl.make_name, cl.model_name "
                       "FROM customers c "
                       "JOIN bookings b on c.customer_id = b.customer_id JOIN "
                       "cars_list cl on b.car_id = cl.car_id "
                       "WHERE c.customer_id = %s "
                       "ORDER BY b.start_date DESC",
                       customer_id)

        return cursor.fetchall()

    def check_booking_dates_conflict(self, pickup_date, return_date):
        print(pickup_date)
        print(return_date)

        conflicts_arr = {}

        pickup_oldformat = pickup_date
        pickup_datetimeobject = datetime.strptime(pickup_oldformat,'%d-%m-%Y')
        pickup_newformat = pickup_datetimeobject.strftime('%Y-%m-%d')

        return_oldformat = return_date
        return_datetimeobject = datetime.strptime(return_oldformat,'%d-%m-%Y')
        return_newformat = return_datetimeobject.strftime('%Y-%m-%d')

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT car_id FROM bookings WHERE (%s <= end_date AND %s >= start_date) OR (%s <= end_date AND %s >= start_date)", (pickup_newformat, return_newformat, pickup_newformat, return_newformat))
        count = cursor.rowcount

        if count > 0:
            conflicts_arr['count'] = count
            conflicts_arr['cars'] = cursor.fetchall()
        else:
            conflicts_arr['count'] = count
            conflicts_arr['cars'] = ''
        # print(count)
        # cursor.execute("SELECT * FROM bookings WHERE (%s <= end_date AND %s >= start_date) OR (%s <= end_date AND %s >= start_date)", (pickup_newformat, return_newformat, pickup_newformat, return_newformat))

        return conflicts_arr

    def get_all_available_car_type(self, car_type):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        # cursor.execute("SELECT * FROM cars_list WHERE status = 'available' AND car_type = %s", car_type)
        cursor.execute("SELECT * FROM cars_list WHERE status = 'available' AND car_type = %s", car_type)

        return cursor.fetchall()

    def insert_booking(self, customer_id, car_id, pickupDate, returnDate, _time, booking_status, booking_amount):
        with self.connection.cursor() as cursor:
            pickup_oldformat = pickupDate
            pickup_datetimeobject = datetime.strptime(pickup_oldformat,'%d-%m-%Y')
            pickup_newformat = pickup_datetimeobject.strftime('%Y-%m-%d')

            return_oldformat = returnDate
            return_datetimeobject = datetime.strptime(return_oldformat,'%d-%m-%Y')
            return_newformat = return_datetimeobject.strftime('%Y-%m-%d')

            cursor.execute("INSERT INTO bookings (customer_id, car_id, start_date, end_date, pickup_time, "
                           "booking_status, booking_amount) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                           (customer_id, car_id, pickup_newformat, return_newformat, _time, booking_status, booking_amount))
        self.connection.commit()

    # Can you simplify the queries here ??????????????????????????????????????
    def update_booking(self, bookingid):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("UPDATE bookings "
                       "SET booking_status = 'cancelled' "
                       "WHERE booking_id = %s",
                       bookingid)
        self.connection.commit()
