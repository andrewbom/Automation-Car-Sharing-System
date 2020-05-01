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

        account = db.login_account(email, password)

        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['customer_id']
            session['firstname'] = account['first_name']
            session['lastname'] = account['last_name']
            session['email'] = account['email']
            # Redirect to home page
            return redirect(url_for('home'))
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
    # Redirect to login page
    return redirect(url_for('login'))


# --------------------------------------------REGISTER PAGE-----------------------------------------------------

# http://localhost:5000/carrental/register - this will be the registration page,
# we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
@app.route('/carrental/register', methods=['GET', 'POST'])
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
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        # elif not re.match(r'[A-Za-z0-9]+', email):
        #     msg = 'Username must contain only characters and numbers!'
        elif not firstname or not lastname or not email or not password:
            msg = 'Please fill out the form!'
        else:
            db.insert_account(firstname, lastname, email, password)
            msg = 'You have successfully registered!'

    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# --------------------------------------------HOME PAGE-----------------------------------------------------

# http://localhost:5000/carrental/home - this will be the home page, only accessible for loggedin users
@app.route('/carrental/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['firstname'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# --------------------------------------------PROFILE PAGE-----------------------------------------------------

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        account = db.get_an_user(session['username'])

        # Show the profile page with account info
        return render_template('profile.html', account=account)

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# --------------------------------------------BOOKING PAGE-----------------------------------------------------

# http://localhost:5000/carrental/booking - this will be the home page, only accessible for loggedin users
@app.route('/carrental/booking/', methods=['GET', 'POST'])
def booking():
    # Get input from the user
    # then search cars
    # fetch cars
    if request.method == 'POST':
        # Check if user is logged in
        if 'loggedin' in session:
            # account = db.get_an_user(session['username'])
            
            print(request.form)
            car_type = request.form.get('carType')  # this grab the value of the selection in booking.html file
            start_date = request.form.get('startDate')
            end_Date = request.form.get('endDate')
            pickup_time = request.form.get('pickupTime')
            

            # check the availability of the Car
            cars = db.get_available_car(car_type)
            print(cars)
            if not cars:
                flash("The Car is currently not available")
                return redirect(url_for('booking'))


            # pick_up_location = request.form["pickupLocation"]
            # drop_off_location = request.form["dropoffLocation"]

            # check the availability of the Car
            # car_id = db.get_available_car(car_type)
            # if not car_id:
            #     flash("The Car is currently not available")
            #     return redirect(url_for('booking'))

            # db.update_car(car_id)
            # db.insert_booking(session['username'], car_id, start_date, end_Date, _time)

            # global CARID
            # CARID = carid[:]
            # global b_actual_id

            # Show the booking page
            return render_template('new_booking.html', username=session['firstname'])

        else:
            # User is not logged in and redirect to login page
            flash("You have been logged out. Please login again.")
            return redirect(url_for('login'))

    return render_template('new_booking.html', username=session['firstname'])

# --------------------------------------------CAR LIST PAGE-----------------------------------------------------

# http://localhost:5000/carrental/profile - this will be the Cars List page, only accessible for loggedin users
@app.route('/carrental/carslist')
def carslist():
    # Check if user is loggedin
    if 'loggedin' in session:

        # check the availability of the Cars List
        carlist = db.get_all_available_cars()

        # Show the Cars List
        return render_template('cars.html', username=session['firstname'], cars=carlist)

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# --------------------------------------------BOOKING HISTORY PAGE-----------------------------------------------------

# http://localhost:5000/carrental/profile - this will be the Cars List page, only accessible for loggedin users
@app.route('/carrental/bookinghistory')
def bookinghistory():
    # Check if user is loggedin
    if 'loggedin' in session:

        customerid = session['id']

        # check the booking history of logged in customer
        bookingshistory = db.get_customer_booking_history(customerid)
        print(bookingshistory)

        # Show the Cars List
        return render_template('booking_history.html', username=session['firstname'], bookings=bookingshistory)

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
