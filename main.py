from flask import Flask, render_template, request, redirect, url_for, session, flash
from database_utils import DatabaseUtils
import re

app = Flask(__name__)
app.secret_key = 'secret'
db = DatabaseUtils()
db.create_account_table()


# --------------------------------------------LOGIN PAGE-----------------------------------------------------

# http://localhost:5000/carrental/ - this will be the login page, we need to use both GET and POST requests
@app.route('/')
@app.route('/carrental/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST':
        # Create variables for easy access
        email = request.form['username']
        password = request.form['password']

        # query the account from the database by passing the input username and password
        account = db.login_account(email, password)

        # Check if the account exists in the accounts table of database
        # If account exists, redirect to home page
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['customer_id']
            session['firstname'] = account['first_name']
            session['lastname'] = account['last_name']
            session['email'] = account['email']
            # Redirect to home page
            return redirect(url_for('home'))

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
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to the login page
    return redirect(url_for('login'))


# --------------------------------------------REGISTER PAGE-----------------------------------------------------

# http://localhost:5000/carrental/register - this will be the registration page,
# we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
@app.route('/carrental/register', methods=['GET', 'POST'])  # why there are 2 routes
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST':
        # Create variables for easy access
        firstname = request.form['first_name']
        lastname = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

        account = db.check_exist_username(email)
        print(account)
        # If account exists show error and validation checks
        if account:
            msg = 'Account has already existed!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not firstname or not lastname or not email or not password:
            msg = 'Please fill out the form!'

        # if account doesn't existed, show the successful message and back to the login page
        else:
            db.insert_account(firstname, lastname, email, password)
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
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is logged in
    if 'loggedin' in session:
        account = db.get_an_user(session['email'])

        # Show the profile page with account info
        return render_template('profile.html', account=account, username=session['firstname'])

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# --------------------------------------------SEARCH PAGE-----------------------------------------------------

# http://localhost:5000/carrental/search - this will be the search page, only accessible for loggedin users
@app.route('/carrental/search/', methods=['GET', 'POST'])
def search():

    # Check if user is logged in and has filled the form
    if 'loggedin' in session and 'carType' in request.form and 'startDate' in request.form \
            and 'endDate' in request.form and 'pickupTime' in request.form:

        # check the availability of the Car by getting the value of the selection in new_booking.html file
        cars = db.get_all_available_car_type(int(request.form.get('carType')))
        print(cars)
        if not cars:
            flash("The car type that you have selected is currently NOT available")
            return redirect(url_for('search'))
        elif cars:
            # Create session data, we may access these data in booking routes for future booking
            session['car_type'] = int(request.form.get('carType'))
            session['start_Date'] = request.form.get('startDate')
            session['end_Date'] = request.form.get('endDate')
            session['pick_up_Time'] = request.form.get('pickupTime')
            session['booking_status'] = 'booked'
            session['car_id'] = 888  # don't know how to fetch a particular car_id from searching result

        # reload the new_booking page with showing the searching result
        return render_template('new_booking.html', username=session['firstname'], cars=cars)

    # Check if user has logged in ONLY
    elif 'loggedin' in session:
        return render_template('new_booking.html')

    else:
        # User is not logged in and redirect to login page
        flash("You have been logged out. Please login again.")
        return redirect(url_for('login'))

# --------------------------------------------BOOK THE CAR PAGE-----------------------------------------------------

# http://localhost:5000/carrental/booking - this will be the booking page, only accessible for logged in users
@app.route('/carrental/booking', methods=['GET', 'POST'])
def booking():
    # Check if user is logged in
    if 'loggedin' in session:
        session['booking_status'] = 'booked'

        db.insert_booking(session['id'],
                          session['car_id'],
                          session['start_Date'],
                          session['end_Date'],
                          session['pick_up_Time'],
                          session['booking_status'],
                          123.00)

        # Remove session data after inserting a new booking
        session.pop('id', None)
        session.pop('car_id', None)
        session.pop('start_Date', None)
        session.pop('loggedin', None)
        session.pop('end_Date', None)
        session.pop('booking_status', None)

        # User is logged in show them the home page
        return render_template('booking.html', username=session['firstname'])

    # User is not logged in and redirect to login page
    else:
        return redirect(url_for('login'))



# --------------------------------------------CAR LIST PAGE-----------------------------------------------------

# http://localhost:5000/carrental/carslist - this will be the Cars List page, only accessible for logged in users
@app.route('/carrental/carslist')
def carslist():
    # Check if user is logged in
    if 'loggedin' in session:
        # get and show the list of all available cars
        carlist = db.get_all_available_cars()

        # Show the Cars List
        return render_template('cars.html', username=session['firstname'], cars=carlist)

    # User is not logged in redirect to login page
    return redirect(url_for('login'))


# --------------------------------------------BOOKING HISTORY PAGE-----------------------------------------------------

# http://localhost:5000/carrental/bookinghistory - this will be the booking history page,
# only accessible for logged in users
@app.route('/carrental/bookinghistory')
def bookinghistory():
    # Check if user is loggedin
    if 'loggedin' in session:
        customerid = session['id']

        # check the booking history of logged in customer
        booking_history = db.get_customer_booking_history(customerid)
        print(booking_history)

        # Show the Cars List
        return render_template('booking_history.html', username=session['firstname'], history=booking_history)

    # User is not logged in redirect to login page
    return redirect(url_for('login'))


# --------------------------------------------CANCEL BOOKING PAGE-----------------------------------------------------

# http://localhost:5000/carrental/cancelbooking - this will be the cancel booking page,
# only accessible for logged in users
@app.route('/carrental/bookinghistory/cancelbooking', methods=['GET', 'POST'])
def cancel_booking():
    # Check if user is logged in
    if 'loggedin' in session:
        customerid = session['id']
        # update the booking status to 'cancel' and set car's status to 'Available'
        db.update_booking(customerid)

        # check the booking history of logged in customer
        booking_history = db.get_customer_booking_history(customerid)
        print(booking_history)

        flash("The booking is successfully cancelled!!!")
        return render_template('booking_history.html', username=session['firstname'], history=booking_history)

    # User is not logged in redirect to login page
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
