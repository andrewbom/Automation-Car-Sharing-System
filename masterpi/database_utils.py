from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import sha256_crypt
from datetime import datetime
import pymysql  # MySQLdb  # pymysql
import math


class DatabaseUtils:
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
            cursor.execute("INSERT IGNORE INTO `customers` VALUES (NULL, 'Wayne', 'Wayne', 'abc@gmail.com', '" + hashedpassword + "')")
            cursor.execute("INSERT IGNORE INTO `customers` VALUES (NULL, 'John', 'Mathew', 'john@gmail.com', '" + hashedpassword + "')")
            cursor.execute("INSERT IGNORE INTO `customers` VALUES (NULL, 'Anna', 'Williams', 'anna@gmail.com', '" + hashedpassword + "')")
            cursor.execute("INSERT IGNORE INTO `customers` VALUES (NULL, 'Harry', 'Robert', 'harry@gmail.com', '" + hashedpassword + "')")
            cursor.execute("INSERT IGNORE INTO `customers` VALUES (NULL, 'Charlie', 'William', 'carlie@gmail.com', '" + hashedpassword + "')")
            cursor.execute("INSERT IGNORE INTO `customers` VALUES (NULL, 'Oliver', 'Michelle', 'oliver@gmail.com', '" + hashedpassword + "')")

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
                    `latitude` varchar(20)  NOT NULL,
                    `longitude` varchar(20) NOT NULL,
                    UNIQUE(`registration_no`),
                    PRIMARY KEY (`car_id`)                    
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
            """)
            cursor.execute("INSERT IGNORE INTO `cars_list` VALUES (NULL, 'Toyota', 'Camry', '4', 'Red', 1, 15, "
                           "'Flinders', 'available' , -35.8183, 146.9671);")
            cursor.execute("INSERT IGNORE INTO `cars_list` VALUES (NULL, 'Mazda', 'CX-5', '4', 'Yellow', 3, 20, "
                           "'Box hills', 'available', -37.8181, 145.1239);")
            cursor.execute("INSERT IGNORE INTO `cars_list` VALUES (NULL, 'Nissan', 'Altima', '5', 'Black', 1, 10, "
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
            # cursor.execute(
            #     "INSERT IGNORE INTO `bookings` VALUES (NULL,1, 1, '2020-04-07', '13:45', '2020-04-10', '14:45', "
            #     "'155.00', 'booked' ,NULL);")
            # cursor.execute("INSERT IGNORE INTO `bookings` VALUES (NULL, 1, 2, '10-03-2020', '15-03-2020', '13:45', "
            #                "'123.00', 'booked', NULL);")

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
        print(pickup_date)
        print(return_date)

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
        # print(count)
        # cursor.execute("SELECT * FROM bookings WHERE (%s <= return_date AND %s >= pickup_date) OR (%s <= return_date AND %s >= pickup_date)", (pickup_newformat, return_newformat, pickup_newformat, return_newformat))

        return conflicts_arr

    def get_all_available_car_type(self, car_make, car_type, car_colour, car_seat, pickup_date, return_date):

        # subquery_car_make = ""
        # if car_make != "":
        #     subquery_car_make = " AND make_name = '" + car_make + "' "
        #
        # subquery_car_type = ""
        # if car_type != "":
        #     subquery_car_type = " AND car_type = '" + car_type + "' "
        #
        # subquery_colour = ""
        # if colour != "":
        #     subquery_colour = " AND colour = '" + colour + "' "
        #
        # subquery_seating_capacity = ""
        # if seating_capacity != "":
        #     subquery_seating_capacity = " AND seating_capacity = '" + seating_capacity + "' "

        pickup_oldformat = pickup_date
        pickup_datetimeobject = datetime.strptime(pickup_oldformat, '%d-%m-%Y')
        pickup_newformat = pickup_datetimeobject.strftime('%Y-%m-%d')

        return_oldformat = return_date
        return_datetimeobject = datetime.strptime(return_oldformat, '%d-%m-%Y')
        return_newformat = return_datetimeobject.strftime('%Y-%m-%d')

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select * "
                       "from cars_list "
                       "where "
                       "status = 'available' "
                       "AND car_type = %s "
                       "AND car_id NOT IN ( "
                       "    SELECT car_id "
                       "    FROM bookings "
                       "    WHERE ( %s <= return_date AND %s >= pickup_date) "
                       "    OR( %s <= return_date AND %s >= pickup_date))",
                       (car_type, pickup_newformat, return_newformat, pickup_newformat, return_newformat))

        return cursor.fetchall()

    # `make_name` varchar(100) NOT NULL,
    # `model_name` varchar(100) DEFAULT NULL,
    # `seating_capacity` varchar(1) DEFAULT NULL,
    # `colour` varchar(20) DEFAULT NULL,
    # `car_type` int(1) DEFAULT NULL

    # def get_all_available_car_type(self, car_type):
    #     cursor = self.connection.cursor(pymysql.cursors.DictCursor)
    #     # cursor.execute("SELECT * FROM cars_list WHERE status = 'available' AND car_type = %s", car_type)
    #     cursor.execute("SELECT * FROM cars_list WHERE status = 'available' AND car_type = %s", car_type)
    #
    #     # variable_name = ''
    #     # if cartype != 0:
    #     #     variable_name .= 'car_type = variable+passed AND'
    #     # elif car_make != 0:
    #     #     variable_name .= 'carmake= varialbe+passed'
    #     # elif color != 0:
    #     #     variable_name .= 'carmake= varialbe+passed'
    #
    #     # cursor.execute("SELECT * FROM cars_list WHERE variable_name", str(avoid_lis))
    #
    #     return cursor.fetchall()

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
