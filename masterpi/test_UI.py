import os
import unittest
from main import app


class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()
        self.assertEqual(app.debug, False)

    def tearDown(self):
        pass

    def Register(self, firstname, lastname, email, password):
        return self.app.post(
            '/register',
            data=dict(first_name=firstname, last_name=lastname, email=email, password=password),
            follow_redirects=True
        )

    def Login(self, email, password):
        return self.app.post(
            '/carrental',
            data=dict(email=email, password=password),
            follow_redirects=True
        )

    def Logout(self, email, password):
        return self.app.get(
            '/carrental/logout',
            follow_redirects=True
        )

    def test_mainHomePage(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_carRental(self):
        response = self.app.get('/carrental', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_Logout(self):
        response = self.app.get('/carrental/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_Register(self):
        response = self.app.get('/register', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        registeruser = self.Register('xyz', 'abc', 'xyz@gmail.com', '123')
        self.assertEqual(registeruser.status_code, 200)
        self.assertIn(b'You have successfully registered!', registeruser.data)

    def test_Login(self):
        response = self.app.get('/carrental', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_carRentalHome(self):
        response = self.app.get('/carrental/home', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_carRentalProfile(self):
        response = self.app.get('/carrental/profile', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_carRentalSearch(self):
        response = self.app.get('/carrental/search', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_carRentalBookingHistory(self):
        response = self.app.get('/carrental/bookinghistory', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_carRentalBookingLocation(self):
        response = self.app.get('/carrental/location', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
