import sqlite3
from sqlite3 import Error


class Database_utils:
    def __init__(self, connection=None):
        self.database_name = 'agentpi_db'
        self.con = self.sql_connection()
        self.sql_initialize()

    def sql_initialize(self):
        self.sql_table()
        self.sql_insert_data()

    def sql_connection(self):
        try:
            con = sqlite3.connect(self.database_name)
            return con

        except Error:
            print(Error)

    def sql_table(self):
        cursorObj = self.con.cursor()

        cursorObj.execute("""
             DROP TABLE IF EXISTS user_details
        """)

        # Create a car details' TABLE in the local database
        cursorObj.execute("""
            CREATE TABLE IF NOT EXISTS car_details(
                id integer PRIMARY KEY,
                car_id real,
                make_name text,
                model_name text,
                seating_capacity real, 
                colour text, 
                car_type text,
                registration_no real,
                lat real ,lng real)
        """)

        # Create a user details' TABLE in the local database
        cursorObj.execute("""
            CREATE TABLE IF NOT EXISTS user_details(
                id integer PRIMARY KEY, 
                username text, 
                password text,
                customer_id integer,
                face_id real)
        """)
        self.con.commit()

    def sql_insert_data(self):
        cursorObj = self.con.cursor()
        cursorObj.execute("INSERT INTO car_details(car_id , make_name ,model_name ,seating_capacity, colour, car_type ,registration_no ,lat ,lng ) VALUES (1 ,'Sedan' ,'Toyota' ,4 ,'red' ,'suv' ,32 ,-9 ,-9 )")
        cursorObj.execute("INSERT INTO user_details(username , password ,customer_id ,face_id) VALUES ('john@gmail.com' ,'123' ,2 ,2)")
        cursorObj.execute("INSERT INTO user_details(username , password ,customer_id ,face_id) VALUES ('anna@gmail.com' ,'123' ,3 ,1)")

        # # Set 1 Car information that connected to 1 agent pi in the local database
        # cursorObj.execute("""
        #     INSERT INTO car_details(
        #         car_id,
        #         make_name,
        #         model_name,
        #         seating_capacity,
        #         colour,
        #         car_type,
        #         registration_no,
        #         lat,
        #         lng)
        #     VALUES (1, 'Sedan', 'Toyota', 4, 'red', 'suv', 32, -9, -9)
        # """)
        #
        # # Set the default user information in the local database
        # cursorObj.execute("""
        #     INSERT INTO user_details(
        #         username,
        #         password,
        #         customer_id,
        #         face_id)
        #     VALUES ('john@gmail.com', '123', 2, 1)
        # """)
        self.con.commit()

    def update_car_location(self, lat, lng):
        cursorObj = self.con.cursor()
        cursorObj.execute('UPDATE car_details SET lat = {} and lng = {} where id = 1'.format(lat, lng))
        self.con.commit()

    def get_car_data(self):
        cursorObj = self.con.cursor()
        cursorObj.execute('SELECT * FROM car_details')
        return cursorObj.fetchone()

    def get_face_data(self, face_id):
        cursorObj = self.con.cursor()
        cursorObj.execute('SELECT * FROM user_details WHERE face_id = {}'.format(face_id))
        return cursorObj.fetchone()

    def get_user_data(self):
        cursorObj = self.con.cursor()
        cursorObj.execute('SELECT * FROM user_details')
        return cursorObj.fetchone()
