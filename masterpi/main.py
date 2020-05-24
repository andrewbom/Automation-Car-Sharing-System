from flask import Flask, render_template, request, redirect, url_for, session, flash
from passlib.hash import sha256_crypt
from flask_googlemaps import GoogleMaps, Map
from database_utils import DatabaseUtils
from datetime import datetime
import re
from server import ServerClass
from decimal import Decimal

try:
    import json
except ImportError:
    import simplejson as json

app = Flask(__name__)
db = DatabaseUtils()
db.create_account_table()

# you can set key as config
app.config['GOOGLEMAPS_KEY'] = "AIzaSyA9CEaJcH6rooo1xohj-uE9ErU0KweRw-8"
app.config['SECRET_KEY'] = 'thisismysecretkey'

# Initialize Google map
GoogleMaps(app)


# --------------------------------------------LOGIN PAGE-----------------------------------------------------

# http://localhost:5000/carrental/ - this will be the login page, we need to use both GET and POST requests
@app.route('/')
@app.route('/carrental', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Remove session data, this will log the user out
    session.clear()
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST':
        # Create variables for easy access
        email = request.form['username']
        password = request.form['password']

        # query the account from the database by passing the input username and password
        account = db.login_account(email)

        # Check if the account exists in the accounts table of database
        # If account exists, redirect to home page
        if account:
            # Verifying hashed Password
            if sha256_crypt.verify(password, account['password']):
                # Create session data, we can access these data in other routes
                session['loggedin'] = True
                session['id'] = account['customer_id']
                session['firstname'] = account['first_name']
                session['lastname'] = account['last_name']
                session['email'] = account['email']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Account doesnt exist or username/password incorrect
                msg = 'Incorrect username/passwords!'

        # If account doesn't exist, show the error message and pass it to index.html
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


# --------------------------------------------LOGOUT PAGE-----------------------------------------------------

# http://localhost:5000/carrental/logout - this will be the logout page
@app.route('/carrental/logout')
def logout():
    # Remove session data, this will log the user out
    session.clear()
    # Redirect to the login page
    return redirect(url_for('login'))


# --------------------------------------------REGISTER PAGE-----------------------------------------------------

# http://localhost:5000/carrental/register - this will be the registration page,
# we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
# @app.route('/carrental/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST':
        # Create variables for easy access
        firstname = request.form['first_name']
        lastname = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        hashedpassword = sha256_crypt.using(rounds=1000).hash(password)

        # check whether the email has already registered in the database
        account = db.get_an_user(email)

        # If account exists show error and validation checks
        if account:
            msg = 'Account with this email has already existed!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not firstname or not lastname or not email or not password:
            msg = 'Please fill out the form!'

        # if account doesn't existed, show the successful message and back to the login page
        else:
            db.insert_account(firstname, lastname, email, hashedpassword)
            msg = 'You have successfully registered!'
            return render_template('index.html', msg=msg)

    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# --------------------------------------------HOME PAGE-----------------------------------------------------

# http://localhost:5000/carrental/home - this will be the home page, only accessible for loggedin users
@app.route('/carrental/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is logged in show them the home page
        return render_template('home.html', username=session['firstname'])
    # User is not logged in and redirect to login page
    return redirect(url_for('login'))


# --------------------------------------------PROFILE PAGE-----------------------------------------------------

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for logged in users
@app.route('/carrental/profile')
def profile():
    # Check if user is logged in
    if 'loggedin' in session:
        account = db.get_an_user(session['email'])

        # Show the profile page with account info
        return render_template('profile.html', account=account, username=session['firstname'])

    # User is not logged in redirect to login page
    return redirect(url_for('login'))


# --------------------------------------------SEARCH PAGE-----------------------------------------------------

# http://localhost:5000/carrental/search - this will be the search page, only accessible for logged in users
@app.route('/carrental/search', methods=['GET', 'POST'])
@app.route('/carrental/search/<carid>/<amount>')
def search(carid=0, amount=0):
    # Check if user is logged in and has filled the form
    if 'loggedin' in session:
        cars = []
        date_format = "%d-%m-%Y %H:%M"

        # this if statement happens when the user click the "Search Now" button
        if request.method == 'POST':
            # get the user input selection data from html file and set them into different variables
            car_make = request.form['carMake']
            car_type = request.form['carType']
            car_colour = request.form['carColor']
            car_seat = request.form['carSeat']
            pickup_date = request.form['pickupDate']
            pickup_time = request.form['pickupTime']
            return_date = request.form['returnDate']
            return_time = request.form['returnTime']

            # Create session data, we can access these data in other routes
            if car_type or car_make or car_colour or car_seat:
                session['car_make'] = request.form['carMake']
                session['car_type'] = request.form['carType']
                session['car_colour'] = request.form['carColor']
                session['car_seat'] = request.form['carSeat']
                session['pickup_date'] = request.form['pickupDate']
                session['pickup_time'] = request.form['pickupTime']
                session['return_date'] = request.form['returnDate']
                session['return_time'] = request.form['returnTime']

                # check the time
                date_one = datetime.strptime(pickup_date + ' ' + pickup_time, date_format)
                date_two = datetime.strptime(return_date + ' ' + return_time, date_format)
                days_diff = date_two - date_one
                get_hours = days_diff.total_seconds() / 60 ** 2

                # Setting Renting Time Length and the display message
                session['renting_length'] = "Your renting time period is: " + str(days_diff) + " hours"

                conflict = db.check_booking_dates_conflict(str(pickup_date), str(return_date))
                print(conflict)

                # check whether the car has been booked within the input time period
                # if yes, conflict['count'] will be greater than 0
                if conflict['count'] > 0:

                    # get the car by filtering out those booked car within that input period
                    cars = db.get_all_available_car_type(str(car_make), str(car_type), str(car_colour), str(car_seat), str(pickup_date), str(return_date))

                    if not cars:
                        flash("No cars available for your search range, Sorry!")
                        return redirect(url_for('search'))
                    elif cars:
                        for value in cars:
                            value["price_total"] = float(value["price_per_hour"]) * float(get_hours)

                # if there is no conflict
                else:
                    cars = db.get_all_available_car_type(str(car_make), str(car_type), str(car_colour), str(car_seat), str(pickup_date), str(return_date))
                    if not cars:
                        flash("No cars available for your search range, Sorry!")
                        return redirect(url_for('search'))
                    elif cars:
                        for value in cars:
                            value["price_total"] = float(value["price_per_hour"]) * float(get_hours)

        # this if statement happens when user decides to book a car from the search result after the searching process
        if carid != 0:
            # Need changes in the order
            db.insert_booking(session['id'], carid, session['pickup_date'], session['pickup_time'],
                              session['return_date'], session['return_time'], 'booked', amount)

            # Removing search query from the session
            session.pop('car_make', None)
            session.pop('car_type', None)
            session.pop('car_colour', None)
            session.pop('car_seat', None)
            session.pop('pickup_date', None)
            session.pop('pickup_time', None)
            session.pop('return_date', None)
            session.pop('return_time', None)
            session.pop('renting_length', None)

            return redirect(url_for('bookinghistory'))

        # this if statement happens every time before user entering to New Booking Page
        # Removing search query from the session
        if request.method != 'POST' and carid == 0:
            session.pop('car_make', None)
            session.pop('car_type', None)
            session.pop('car_colour', None)
            session.pop('car_seat', None)
            session.pop('pickup_date', None)
            session.pop('pickup_time', None)
            session.pop('return_date', None)
            session.pop('return_time', None)
            session.pop('renting_length', None)

        # reload the new_booking page with showing the searching result
        return render_template('new_booking.html', username=session['firstname'], carlist=cars)

    # User is not logged in and redirect to login page
    return redirect(url_for('login'))


# --------------------------------------------BOOKING HISTORY PAGE-----------------------------------------------------

# http://localhost:5000/carrental/bookinghistory - this will be the booking history page,
# only accessible for logged in users
@app.route('/carrental/bookinghistory')
@app.route('/carrental/bookinghistory/<bookingid>')
def bookinghistory(bookingid=0):
    # Check if user is loggedin
    if 'loggedin' in session:
        customerid = session['id']

        # check the booking history of logged in customer
        booking_history = db.get_customer_booking_history(customerid)

        if bookingid != 0:
            db.update_booking(bookingid, "booked")
            booking_history = db.get_customer_booking_history(customerid)

        # Show the Cars List
        return render_template('booking_history.html', username=session['firstname'], history=booking_history)

    # User is not logged in redirect to login page
    return redirect(url_for('login'))


# --------------------------------------------BOOKING HISTORY PAGE-----------------------------------------------------

@app.route('/carrental/location')
def map_bounded():
    # Check if user is loggedin
    if 'loggedin' in session:
        # creating a map in the view
        cars = db.get_all_car_location()
        print(cars)
        # getting car's location information from cloud database
        location_detail = [{
            "infobox": str(item["infobox"]),
            "lat": float(item["lat"]),
            "lng": float(item["lng"])} for item in cars]

        # initialize the google map page
        carsmap = Map(
            identifier="carsmap",
            lat=-37.8047,
            lng=144.9580,
            zoom=13,
            style="height:1000px;width:100%;margin-left:auto;margin-right:auto;margin-top:auto;margin-bottom:auto",
            markers=location_detail
        )
        return render_template('location.html', carsmap=carsmap)

    # User is not logged in and redirect to login page
    return redirect(url_for('login'))


if __name__ == "__main__":
    sv = ServerClass()
    sv.Serve()
    app.run(debug=False)
