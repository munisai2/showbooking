
from flask import Flask, render_template, request, redirect, url_for,session,flash
import sqlite3


app = Flask(__name__)
app.secret_key = 'mysecretkey'

# Create a connection to the SQLite database
conn = sqlite3.connect('mydatabase.db')
cursor = conn.cursor()

# Create an 'admin' table if it doesn't exist already
cursor.execute('''CREATE TABLE IF NOT EXISTS admin
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT NOT NULL,
               password TEXT NOT NULL);''')
conn.commit()


# Create a 'venues' table if it doesn't exist already
cursor.execute('''CREATE TABLE IF NOT EXISTS venues
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               place TEXT NOT NULL,
               location TEXT NOT NULL,
               capacity INTEGER NOT NULL);''')
conn.commit()

# Create a 'shows' table if it doesn't exist already
cursor.execute('''CREATE TABLE IF NOT EXISTS shows
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
               venue_id INTEGER NOT NULL,
               name TEXT NOT NULL,
               ratings INTEGER NOT NULL,
               timings TEXT NOT NULL,
               tags TEXT NOT NULL,
               price INTEGER NOT NULL,
               FOREIGN KEY(venue_id) REFERENCES venues(id));''')
conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
            );''')
conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    show_id INTEGER NOT NULL,
    seats INTEGER NOT NULL,
    num_seats INTEGER NOT NULL,
    total_price REAL NOT NULL,
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (show_id) REFERENCES shows (id)
    );''')
conn.commit()
cursor.execute('''CREATE TABLE IF NOT EXISTS profiles
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL,
              phone TEXT NOT NULL,
              email TEXT NOT NULL)''')
conn.commit()

# Close the connection to the database
conn.close()

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    # redirect to the login page
    return redirect(url_for('index'))

@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Create a connection to the SQLite database
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Check if the admin credentials are correct
        cursor.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
        admin = cursor.fetchone()

        # Close the connection to the database
        conn.close()

        if admin:
            return redirect(url_for('admindashboard2'))
        else:
            return render_template('adminlogin.html', message='Invalid credentials')

    return render_template('adminlogin.html')
@app.route('/userlogin', methods=['GET', 'POST'])
def userlogin():
    error = None  # initialize error message to None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Create a connection to the SQLite database
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Check if the user with the given username and password exists in the 'users' table
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        # Close the connection to the database
        conn.close()

        if user is not None:
            session['user'] = user[0]  # store the user ID in the session
            return redirect(url_for('userdashboard'))
        else:
            error = 'Invalid username or password. Please try again.'

    return render_template('userlogin.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # get user input from the form
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']
        email = request.form['email']

        # insert user data into tables
        conn = sqlite3.connect('mydatabase.db')
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            c.execute("INSERT INTO profiles (username, phone, email) VALUES (?, ?, ?)", (username, phone, email))

            # commit changes to the database
            conn.commit()

            # close the cursor and connection
            c.close()
            conn.close()

            # redirect to login page
            return redirect('/userlogin')
        except Exception as e:
            print(e)
            conn.rollback()

    return render_template('register.html')
@app.route('/admindashboard1', methods=['GET', 'POST'])
def admindashboard1():
    if request.method == 'POST':
        name = request.form['name']
        place = request.form['place']
        location = request.form['location']
        capacity = request.form['capacity']

        # Create a connection to the SQLite database
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Insert the new venue into the 'venues' table
        cursor.execute("INSERT INTO venues (name, place, location, capacity) VALUES (?, ?, ?, ?)", (name, place, location, capacity))
        conn.commit()

        # Close the connection to the database
        conn.close()

        return redirect(url_for('admindashboard2'))

    return render_template('admindashboard1.html')

@app.route('/admindashboard2')
def admindashboard2():
    # Create a connection to the SQLite database
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    # Fetch all the venues from the 'venues' table
    cursor.execute("SELECT * FROM venues")
    venues = cursor.fetchall()

    # Fetch all the shows associated with each venue
    for venue in venues:
        cursor.execute("SELECT * FROM shows WHERE venue_id=?", (venue[0],))
        shows = cursor.fetchall()
        venue_list = list(venue)
        venue_list.append(shows)
        venues[venues.index(venue)] = tuple(venue_list)



    # Close the connection to the database
    conn.close()

    return render_template('admindashboard2.html', venues=venues)



# Function to establish a connection to the SQLite database
def get_db():
    conn = sqlite3.connect('mydatabase.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/editvenue/<int:id>', methods=['GET', 'POST'])
def editvenue(id):
    if request.method == 'POST':
        name = request.form['name']
        place = request.form['place']
        location = request.form['location']
        capacity = request.form['capacity']

        # Create a connection to the SQLite database
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Update the venue in the 'venues
        cursor.execute("UPDATE venues SET name=?, place=?, location=?, capacity=? WHERE id=?", (name, place, location, capacity, id))
        conn.commit()

        # Close the connection to the database
        conn.close()

        return redirect(url_for('admindashboard2'))

    # Create a connection to the SQLite database
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    # Fetch the venue with the given ID from the 'venues' table
    cursor.execute("SELECT * FROM venues WHERE id=?", (id,))
    venue = cursor.fetchone()

    # Close the connection to the database
    conn.close()

    return render_template('editvenue.html', venue=venue)

@app.route('/deletevenue/<int:id>')
def deletevenue(id):
    # Create a connection to the SQLite database
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    # Delete the venue with the given ID from the 'venues' table
    cursor.execute("DELETE FROM venues WHERE id=?", (id,))
    conn.commit()

    # Close the connection to the database
    conn.close()

    return redirect(url_for('admindashboard2'))

@app.route('/createshow/<int:id>', methods=['GET', 'POST'])
def createshow(id):
    if request.method == 'POST':
        name = request.form['name']
        ratings = request.form['ratings']
        timings = request.form['timings']
        tags = request.form['tags']
        price = request.form['price']

        # Create a connection to the SQLite database
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Insert the new show into the 'shows' table
        cursor.execute("INSERT INTO shows (venue_id, name, ratings, timings, tags, price) VALUES (?, ?, ?, ?, ?, ?)", (id, name, ratings, timings, tags, price))
        conn.commit()

        # Close the connection to the database
        conn.close()

        return redirect(url_for('showdetails', id=id))

    return render_template('createshow.html', id=id)

@app.route('/showdetails/<int:id>')
def showdetails(id):
    # Create a connection to the SQLite database
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    # Fetch the venue with the given ID from the 'venues' table
    cursor.execute("SELECT * FROM venues WHERE id=?", (id,))
    venue = cursor.fetchone()

    # Fetch all the shows for the given venue from the 'shows' table
    cursor.execute("SELECT * FROM shows WHERE venue_id=?", (id,))
    shows = cursor.fetchall()

    # Close the connection to the database
    conn.close()

    return render_template('showdetails.html', venue=venue, shows=shows)

@app.route('/editshow/<int:id>', methods=['GET', 'POST'])
def editshow(id):
    if request.method == 'POST':
        name = request.form['name']
        ratings = request.form['ratings']
        timings = request.form['timings']
        tags = request.form['tags']
        price = request.form['price']

        # Create a connection to the SQLite database
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Update the show with the given ID in the 'shows' table
        cursor.execute("UPDATE shows SET name=?, ratings=?, timings=?, tags=?, price=? WHERE id=?", (name, ratings, timings, tags, price, id))
        conn.commit()

        # Fetch the venue ID for the show with the given ID from the 'shows' table
        cursor.execute("SELECT venue_id FROM shows WHERE id=?", (id,))
        venue_id = cursor.fetchone()[0]

        # Close the connection to the database
        conn.close()

        return redirect(url_for('showdetails', id=venue_id))

    # Create a connection to the SQLite database
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    # Fetch the show with the given ID from the 'shows' table
    cursor.execute("SELECT * FROM shows WHERE id=?", (id,))
    show = cursor.fetchone()

    # Check if show is not None before accessing its elements
    if show is not None:
        return render_template('editshow.html', show=show)
    else:
        return "Show not found"
        
    # Close the connection to the database
    conn.close()


@app.route('/deleteshow/<int:id>')
def deleteshow(id):
    # Create a connection to the SQLite database
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    # Fetch the venue ID for the show with the given ID from the 'shows' table
    cursor.execute("SELECT venue_id FROM shows WHERE id=?", (id,))
    venue_id = cursor.fetchone()[0]

    # Delete the show with the given ID from the 'shows' table
    cursor.execute("DELETE FROM shows WHERE id=?", (id,))
    conn.commit()

    # Close the connection to the database
    conn.close()

    return redirect(url_for('showdetails', id=venue_id))

@app.route('/addvenue', methods=['GET', 'POST'])
def addvenue():
    if request.method == 'POST':
        name = request.form['name']
        place = request.form['place']
        location = request.form['location']
        capacity = request.form['capacity']

        # Create a connection to the SQLite database
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Insert the new venue into the 'venues' table
        cursor.execute("INSERT INTO venues (name, place, location, capacity) VALUES (?, ?, ?, ?)", (name, place, location, capacity))
        conn.commit()

        # Close the connection to the database
        conn.close()

        return redirect(url_for('admindashboard2'))

    return render_template('addvenue.html')

@app.route('/addshow/<int:id>', methods=['GET', 'POST'])
def addshow(id):
    if request.method == 'POST':
        name = request.form['name']
        ratings = request.form['ratings']
        timings = request.form['timings']
        tags = request.form['tags']
        price = request.form['price']

        # Create a connection to the SQLite database
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Insert the new show into the 'shows' table
        cursor.execute("INSERT INTO shows (venue_id, name, ratings, timings, tags, price) VALUES (?, ?, ?, ?, ?, ?)", (id, name, ratings, timings, tags, price))
        conn.commit()

        # Close the connection to the database
        conn.close()

        return redirect(url_for('showdetails', id=id))

    return render_template('addshow.html', id=id)

@app.route('/userdashboard')
def userdashboard():
    # Get the selected venue from the URL parameter (if any)
    selected_venue_id = request.args.get('venue')

    # Get the search query from the URL parameter (if any)
    search_query = request.args.get('q')

    # Create a connection to the SQLite database
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    # Fetch all venues from the 'venues' table
    cursor.execute("SELECT * FROM venues")
    venues = cursor.fetchall()

    # If a search query is provided, search for venues that match the query
    if search_query:
        cursor.execute("SELECT * FROM venues WHERE name LIKE ? OR address LIKE ?",
                       ('%{}%'.format(search_query), '%{}%'.format(search_query)))
        venues = cursor.fetchall()

    # If a venue is selected, fetch all shows for that venue from the 'shows' table
    if selected_venue_id:
        cursor.execute("SELECT * FROM shows WHERE venue_id=?", (selected_venue_id,))
        shows = cursor.fetchall()
    else:
        # Otherwise, fetch all shows from the 'shows' table
        cursor.execute("SELECT * FROM shows")
        shows = cursor.fetchall()

    # If a search query is provided, search for shows that match the query
    if search_query:
        cursor.execute("SELECT * FROM shows WHERE name LIKE ? OR description LIKE ?",
                       ('%{}%'.format(search_query), '%{}%'.format(search_query)))
        shows = cursor.fetchall()

    # Close the connection to the database
    conn.close()

    return render_template('userdashboard.html', venues=venues, shows=shows, selected_venue_id=selected_venue_id, search_query=search_query)


@app.route('/bookshow/<int:id>', methods=['GET', 'POST'])
def bookshow(id):
    # Create a connection to the SQLite database
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    # Fetch the show with the given ID from the 'shows' table
    cursor.execute("SELECT * FROM shows WHERE id=?", (id,))
    show = cursor.fetchone()

    # Fetch the venue for the show from the 'venues' table
    cursor.execute("SELECT * FROM venues WHERE id=?", (show[1],))
    venue = cursor.fetchone()

    # Get the price of the show from the 'shows' table
    price = show[6]

    # Calculate the number of available seats for the show
    cursor.execute("SELECT COALESCE(SUM(num_seats), 0) FROM bookings WHERE show_id=?", (id,))
    num_booked_seats = cursor.fetchone()[0]

    num_available_seats = venue[4] - num_booked_seats

    # Define num_seats and total_price variables with default values of zero
    num_seats = 0
    total_price = 0

    if request.method == 'POST':
        num_seats = int(request.form['num_seats'])
        total_price = num_seats * price

        # Check if there are enough available seats for the show
        if num_seats <= num_available_seats:
            user_id = session.get('user')

            # Insert the booking into the 'bookings' table
            cursor.execute("INSERT INTO bookings (user_id, show_id, seats, num_seats, total_price) VALUES (?, ?, ?, ?, ?)", (user_id, id, num_seats, num_seats, total_price))
            conn.commit()

            # Close the connection to the database
            conn.close()

            flash('Booking confirmed!')
            return redirect(url_for('bookings', user_id=user_id))

        else:
            flash('Sorry, the show is housefull!')

    # Pass the variables to the HTML template
    return render_template('bookshow.html', show=show, venue=venue, num_available_seats=num_available_seats, num_seats=num_seats, total_price=total_price)

@app.route('/bookings/<int:user_id>')
def bookings(user_id):
    # Create a connection to the SQLite database
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    # Fetch all bookings for the user with the given ID from the 'bookings' table
    cursor.execute("SELECT bookings.id, shows.name, venues.name, bookings.seats, bookings.total_price, bookings.booking_time FROM bookings JOIN shows ON bookings.show_id=shows.id JOIN venues ON shows.venue_id=venues.id WHERE bookings.user_id=?", (user_id,))
    bookings = cursor.fetchall()

    # Close the connection to the database
    conn.close()

    # Pass the bookings data to the HTML template
    return render_template('bookings.html', bookings=bookings)



   
if __name__ == '__main__':
    app.run(debug=True)