import sqlite3
from sqlite3 import Error
from datetime import datetime
import math
import unittest
from database_utils import Database_utils


class TestDatabaseUtils(unittest.TestCase):
	database_name = 'agentpi_db'
			
			
	def setUp(self):
		self.con = sqlite3.connect(TestDatabaseUtils.database_name)
		cursorObj = self.con.cursor()
	    
		cursorObj.execute("DROP TABLE IF EXISTS car_details")
		cursorObj.execute("DROP TABLE IF EXISTS user_details")
		cursorObj.execute("CREATE TABLE IF NOT EXISTS car_details(id integer PRIMARY KEY, car_id real, make_name text,model_name text,seating_capacity real, colour text, car_type text,registration_no real ,lat real ,lng real ,UNIQUE(`car_id` ,`registration_no`))")
		cursorObj.execute("CREATE TABLE IF NOT EXISTS user_details(id integer PRIMARY KEY, username text, password text,customer_id ,face_id real ,UNIQUE(customer_id,face_id))")
		
		cursorObj.execute("INSERT OR IGNORE INTO car_details(car_id , make_name ,model_name ,seating_capacity, colour, car_type ,registration_no ,lat ,lng ) VALUES (1 ,'Sedan' ,'Toyota' ,4 ,'red' ,'suv' ,32 ,-9 ,-9 )")
		cursorObj.execute("INSERT OR IGNORE INTO user_details(username , password ,customer_id ,face_id) VALUES ('abc@gmail.com' ,'123' ,6 ,1)")
		
		self.con.commit()
					
	def tearDown(self):
		try:
			self.con.sqlite3_close()
		except:
			pass
		finally:
			self.con = None

	def countUserEntries(self):
			cursorObj = self.con.cursor()
			cursorObj.execute("select count(*) from user_details")
			return cursorObj.fetchone()[0]

	def countCarEntries(self):
			cursorObj = self.con.cursor()
			cursorObj.execute("select count(*) from car_details")
			return cursorObj.fetchone()[0]      
                       
            
	def test_getCarData(self):
		db = Database_utils(self.con) 	
		data = db.get_car_data()
		
		if data:
			count = 1
		else:
			count = 0
	
		self.assertTrue(self.countCarEntries() == count)

	def test_getFaceData(self):
		db = Database_utils(self.con) 	
		data = db.get_face_data(1)
		
		if data:
			count = 1
		else:
			count = 0
			
		self.assertTrue(self.countUserEntries() == count)


	def test_getUserData(self):
		db = Database_utils(self.con) 	
		data = db.get_user_data()
		
		if data:
			count = 1
		else:
			count = 0
			
		self.assertTrue(self.countUserEntries() == count)


if __name__ == "__main__":
    unittest.main(verbosity=2)

