import uuid
import requests
import json
from database_utils import Database_utils
import math


# This class reads the mac address and sends it to the google geolocation API.
# The API returns latitude and longitude of the Mac address which is connecting with the raspberry pi.
# The latitude and longitude is therefore representing the address of the raspberry pi (agent pi) and send to master pi
class Car_location:

    def __init__(self):
        # print ("The MAC address in formatted way is : ", end="")
        self.mac_address = (':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                                      for ele in range(0, 8 * 6, 8)][::-1]))

        self.URL = "https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyCntWQD7A7rjkkwSi0-5ehvZt_eg3_6Dqs"

    def truncate(self, number, digits) -> float:
        multiplier = 10.0 ** digits
        return math.trunc(multiplier * number) / multiplier

    def Get_Location(self):
        headers = {
            'Content-type': 'application/json',
        }

        PARAMS = {
            "macAddress": self.mac_address,
            "signalStrength": -43,
            "age": 0,
            "channel": 11,
            "signalToNoiseRatio": 0
        }

        data = json.dumps(PARAMS)

        # sending get request and saving the response as response object
        r = requests.post(url=self.URL, headers=headers, data=data)

        data = json.loads(r.text)
        latitude = (data['location']['lat'])
        longitude = (data['location']['lng'])

        # get the car information from local database
        db = Database_utils()
        cardata = db.get_car_data()
        car_id = cardata[1]

        location_data = {
            "type": "location",
            "car_id": car_id,
            "latitude": self.truncate(latitude, 7),
            "longitude": self.truncate(longitude, 7)
        }
        dataTosend = json.dumps(location_data)

        db.update_car_location(latitude, longitude)
        return dataTosend
