from flask import Flask, render_template, request, redirect, url_for, session, flash
from database_utils import DatabaseUtils
import re

app = Flask(__name__)
app.secret_key = 'secret'
db = DatabaseUtils()
db.create_account_table()


# --------------------------------------------LOGIN PAGE-----------------------------------------------------

# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/')
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        account = db.login_account(username, password)

        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


# --------------------------------------------LOGOUT PAGE-----------------------------------------------------

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))


# --------------------------------------------REGISTER PAGE-----------------------------------------------------

# http://localhost:5000/pythinlogin/register - this will be the registration page,
# we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        account = db.check_exist_username(username)
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            db.insert_account(username, password, email)
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# --------------------------------------------HOME PAGE-----------------------------------------------------

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
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

@app.route('/bookingNow/', methods=['GET', 'POST'])
def booking():
    cabs_list = ["Hatchback", "Sedan", "SUV"]
    try:
        car_empty = False
        driver_empty = False

        userId = request.form["userId"]
        account = db.check_exist_username(userId)
        # If account exists show error and validation checks
        if not account:
            flash("Entered Username does not Exist !!!")
            return render_template('booking.html')

        cab = int(request.form["cab"])
        cab_name = cabs_list[cab]
        startDate = request.form["startDate"]
        endDate = request.form["endDate"]
        time = request.form["time"]
        pickupLocation = request.form["pickupLocation"]
        dropoffLocation = request.form["dropoffLocation"]

        # check the availability of the Car
        car = db.get_available_car(cab_name)
        if not car:
            flash("The Car is currently not available")
            return redirect(url_for('allbooked'))

        car_id = car['Car_id']
        db.update_car(car_id)
        db.insert_booking(userId, cab_name, startDate, endDate, time, pickupLocation, dropoffLocation)

        # global CARID
        # CARID = carid[:]
        # global b_actual_id
        # cursor.execute("""select bookingId from Booking where Pickup_time=%s and startDate=%s """, [time, startDate])
        # b_id = cursor.fetchall()
        # b_actual_id = b_id[0][0]
        # print(b_actual_id)
        # print("Booked")
        # print("Booked")

    except Exception as e:
        return str(e)

    return render_template('booking.html')


# --------------------------------------------ALL BOOKED PAGE-----------------------------------------------------

@app.route('/allbooked/', methods=['GET', 'POST'])
def allbooked():
    print("Entered")  # Testing

    return render_template("allbooked.html")


if __name__ == "__main__":
    app.run(debug=True)
