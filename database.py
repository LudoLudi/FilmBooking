import sqlite3

# Connect to (or create) the SQLite database
conn = sqlite3.connect("film_booking.db")
cursor = conn.cursor()


# Create table for users
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
''')

# Create table for films
cursor.execute("""
CREATE TABLE IF NOT EXISTS films (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    actors TEXT,
    genre TEXT,
    age_rating TEXT,
    showtimes TEXT
)
""")

# Create table for booking report
cursor.execute("""
CREATE TABLE IF NOT EXISTS booking_report (
    id INTEGER PRIMARY KEY,
    film TEXT,
    showtime TEXT,
    tickets INTEGER,
    booking_reference TEXT,
    booking_date TEXT,
    total_price INTEGER,
    cinema TEXT,
    customer_name TEXT,
    status TEXT
)
""")

# Create table for bookings
cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY,
    film TEXT,
    showtime TEXT,
    ticket_count INTEGER,
    booking_reference TEXT,
    booking_date TEXT,
    total_price INTEGER,
    cinema TEXT,
    customer_name TEXT
)
""")

# Create table for cinemas
cursor.execute("""
CREATE TABLE IF NOT EXISTS cinemas (
    id INTEGER PRIMARY KEY,
    city TEXT,
    cinema_name TEXT
)
""")

# Commit and close the connection
conn.commit()
conn.close()

print("Database setup completed successfully.")
