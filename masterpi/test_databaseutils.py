from datetime import datetime
import pymysql  # MySQLdb  # pymysql
import math
import unittest
from database_utils import DatabaseUtils


class TestDatabaseUtils(unittest.TestCase):
    HOST = "35.201.23.126"  # google cloud IP address
    USER = "root"  # google cloud sql user name
    PASSWORD = "andrewishandsome"  # google cloud sql password
    DATABASE = "Pythonlogin"

    def setUp(self):
        self.connection = pymysql.connect(TestDatabaseUtils.HOST, TestDatabaseUtils.USER,
                                          TestDatabaseUtils.PASSWORD, TestDatabaseUtils.DATABASE)

        with self.connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS customers")
            cursor.execute("DROP TABLE IF EXISTS cars_list")
            cursor.execute("DROP TABLE IF EXISTS bookings")

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
            cursor.execute(
                "INSERT IGNORE INTO `customers` VALUES (NULL, 'Wayne', 'Wayne', 'abc@gmail.com','123');")  # custome_id = 1
            cursor.execute(
                "INSERT IGNORE INTO `customers` VALUES (NULL, 'Mary', 'Mary', 'xyz@gmail.com','123');")  # custome_id = 2

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
                    `latitude` decimal(40,15) NOT NULL,
                    `longitude` decimal(40,15) NOT NULL,
                    UNIQUE(`registration_no`),
                    PRIMARY KEY (`car_id`)                    
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
            """)
            cursor.execute(
                "INSERT IGNORE INTO `cars_list` VALUES (NULL, 'Toyota', 'Camry', '4', 'Red', 1, 15, "  # car_id = 1
                "'1AB 2CD', 'available' , 37  , 95.6 );")
            cursor.execute(
                "INSERT IGNORE INTO `cars_list` VALUES (NULL, 'Nissan', 'Sunny', '4', 'Blue', 1, 15, "  # car_id = 2
                "'1AB 2AB', 'available' , 37  , 95.6 );")

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

            cursor.execute(
                "INSERT IGNORE INTO `bookings` VALUES (NULL,1, 1, '2020-04-07', '13:45', '2020-04-10', '14:45', "
                "'155.00', 'booked' ,NULL);")

            self.connection.commit()

    def tearDown(self):
        try:
            self.connection.close()
        except:
            pass
        finally:
            self.connection = None

    def countCars(self):
        with self.connection.cursor() as cursor:
            cursor.execute("select count(*) from cars_list")
            return cursor.fetchone()[0]

    def countBookedCars(self):
        with self.connection.cursor() as cursor:
            cursor.execute("select count(*) from bookings where booking_status = 'booked'")
            return cursor.fetchone()[0]

    def countAvailableCarTypes(self):
        with self.connection.cursor() as cursor:
            cursor.execute("select * ,count(distinct car_type) from cars_list where status = 'available'")
            return cursor.fetchone()[0]

    def countAvailableCars(self):
        with self.connection.cursor() as cursor:
            cursor.execute("select count(*) from cars_list where status = 'available'")
            return cursor.fetchone()[0]

    def countCustomers(self):
        with self.connection.cursor() as cursor:
            cursor.execute("select count(*) from customers")
            return cursor.fetchone()[0]

    def countBookings(self):
        with self.connection.cursor() as cursor:
            cursor.execute("select count(*) from bookings")
            return cursor.fetchone()[0]

    def carExists(self, car_id):
        with self.connection.cursor() as cursor:
            cursor.execute("select count(*) from cars_list where car_id = %s", (car_id,))
            return cursor.fetchone()

    def accountExists(self, email):
        with self.connection.cursor() as cursor:
            cursor.execute("select count(*) from customers where email= %s", (email,))
            return cursor.fetchone()[0]

    def bookingExists(self, customer_id, car_id):
        with self.connection.cursor() as cursor:
            cursor.execute("select count(*) from bookings where customer_id= %s and car_id= %s", (customer_id, car_id))
            return cursor.fetchone()[0]

    def countBookingHistory(self, booking_id):
        with self.connection.cursor() as cursor:
            cursor.execute("select count(*) from bookings where booking_id= %s ", (booking_id,))
            return cursor.fetchone()[0]

    def countCarConflicts(self, pickup_date, return_date):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT car_id FROM bookings WHERE (%s <= return_date AND %s >= pickup_date)",
                           (pickup_date, return_date))
            return cursor.fetchone()

    def test_insertAccount(self):
        with DatabaseUtils(self.connection) as db:
            count = self.countCustomers()
            db.insert_account('John', 'Doe', 'john@gmail.com', '123')
            self.assertTrue(count + 1 == self.countCustomers())

    def test_loginAccount(self):
        with DatabaseUtils(self.connection) as db:
            results = db.login_account('abc@gmail.com', '123')
            if (results == None):
                count = 0
            else:
                count = 1
            self.assertTrue(self.accountExists('abc@gmail.com') == count)

    def test_getUser(self):
        with DatabaseUtils(self.connection) as db:
            results = db.get_an_user('abc@gmail.com')
            if results == None:
                count = 0
            else:
                count = 1
            self.assertTrue(self.accountExists("abc@gmail.com") == count)

    def test_getAllAvailableCars(self):
        with DatabaseUtils(self.connection) as db:
            self.assertTrue(self.countAvailableCars() == len(db.get_all_available_cars()))

    def test_getCustomerBookingHistory(self):
        with DatabaseUtils(self.connection) as db:
            count = self.countBookingHistory('1')
            self.assertTrue(count == len(db.get_customer_booking_history('1')))

    def test_InsertBooking(self):
        with DatabaseUtils(self.connection) as db:
            count = self.countBookings()
            db.insert_booking(1, 1, '07-4-2020', '13:45', '10-4-2020', '13:45', "booked", 100)
            self.assertTrue(count + 1 == self.countBookings())
            db.insert_booking(2, 2, '07-4-2020', '13:45', '10-4-2020', '13:45', "booked", 155)
            self.assertTrue(count + 2 == self.countBookings())

    def test_updateBooking(self):
        with DatabaseUtils(self.connection) as db:
            count = self.countBookedCars()
            db.update_booking('1', 'available')
            self.assertTrue((count - 1 == self.countBookedCars()))

    def test_validateCollection(self):
        with DatabaseUtils(self.connection) as db:
            results = db.validate_collection('1', '1')
            if (results == None):
                dbcount = 0
            else:
                dbcount = 1
            existcount = self.bookingExists('1', '1')
            self.assertTrue(existcount == dbcount)
 

if __name__ == "__main__":
    unittest.main(verbosity=2)
