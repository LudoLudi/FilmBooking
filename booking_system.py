import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import datetime
import random

# Connect to SQLite database
conn = sqlite3.connect("film_booking.db")
cursor = conn.cursor()

# Main Page
def main_page():
    root = tk.Tk()
    root.title("Welcome")

    tk.Button(root, text="Login", command=login_gui).pack(side=tk.LEFT, padx=10, pady=10)
    tk.Button(root, text="Register", command=register_gui).pack(side=tk.RIGHT, padx=10, pady=10)

    root.mainloop()
    
    
# Register system
def register_gui():
    register_window = tk.Toplevel()
    register_window.title("Register")

    tk.Label(register_window, text="Choose User ID:").grid(row=0, column=0)
    user_id_entry = tk.Entry(register_window)
    user_id_entry.grid(row=0, column=1)

    tk.Label(register_window, text="Choose Password:").grid(row=1, column=0)
    password_entry = tk.Entry(register_window, show="*")
    password_entry.grid(row=1, column=1)

    tk.Button(register_window, text="Register", command=lambda: attempt_register(user_id_entry.get(), password_entry.get(), register_window)).grid(row=2, columnspan=2)

    def attempt_register(user_id, password, window):
        role = "customer"
        if user_id and password:  # Ensure that neither field is empty
            try:
                user_check = user_id_entry.get()
                # Check if the user already exists
                cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_check,))
                if cursor.fetchone() is not None:
                    messagebox.showerror(f"Registration Failed", f"User ID {user_check} already exists.")
                    return

                # Insert the new user into the database
                cursor.execute("INSERT INTO users (user_id, password, role) VALUES (?, ?, ?)", (user_id, password, role))
                conn.commit()
                messagebox.showinfo("Registration Success", "You have successfully registered!")
                window.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Registration Failed", f"User ID {user_check} already exists.")
            except Exception as e:
                messagebox.showerror("Registration Failed", f"An error occurred: {str(e)}")
        else:
            messagebox.showerror("Registration Failed", "User ID and password cannot be empty.")
        
        
# Login system
def login(user_id, password):
    cursor.execute("SELECT role FROM users WHERE user_id=? AND password=?", (user_id, password))
    result = cursor.fetchone()
    if result:
        return True, result[0]
    else:
        return False, ""

# GUI for login
def login_gui():
    login_window = tk.Toplevel()
    login_window.title("Login")

    tk.Label(login_window, text="User ID:").grid(row=0, column=0)
    user_id_entry = tk.Entry(login_window)
    user_id_entry.grid(row=0, column=1)

    tk.Label(login_window, text="Password:").grid(row=1, column=0)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.grid(row=1, column=1)

    def attempt_login():
        user_id = user_id_entry.get()
        password = password_entry.get()
        success, user_type = login(user_id, password)
        if success:
            global current_user_id
            current_user_id = user_id  
            login_window.destroy()
            if user_type == "admin":
                admin_gui()
            elif user_type == "manager":
                manager_gui()
                
            elif user_type == "booking_staff":
                booking_staff_gui()
            else:
                customer_gui()
        else:
            messagebox.showerror("Login Failed", "Invalid user ID or password.")

    login_button = tk.Button(login_window, text="Login", command=attempt_login)
    login_button.grid(row=2, column=0, columnspan=2)
    
    
    
    login_window.mainloop()


# GUI for customer view
def customer_gui():
    customer_window = tk.Toplevel()
    customer_window.title("Customer View")
    # user Tab

 # Create the cursor object
    cursor = conn.cursor()

# Create an instance of the A CustomerTab class
    customer_tab = BookingTab(customer_window, cursor)
    customer_tab.pack(fill=tk.BOTH, expand=True)

# Booking Tab
class BookingTab(ttk.Frame):
    def __init__(self, parent, cursor):
        super().__init__(parent)
        self.cursor = cursor

        ttk.Label(self, text="Film").grid(row=0, column=0, padx=10, pady=5)
        self.film_var = tk.StringVar()
        self.film_menu = ttk.Combobox(self, textvariable=self.film_var)
        self.film_menu.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self, text="Showtime").grid(row=1, column=0, padx=10, pady=5)
        self.showtimes_var = tk.StringVar()
        self.showtimes_menu = ttk.Combobox(self, textvariable=self.showtimes_var)
        self.showtimes_menu.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(self, text="Seat Type").grid(row=2, column=0, padx=10, pady=5)
        self.seat_var = tk.StringVar()
        self.seat_menu = ttk.Combobox(self, textvariable=self.seat_var)
        self.seat_menu.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(self, text="Cinema").grid(row=3, column=0, padx=10, pady=5)
        self.cinema_var = tk.StringVar()
        self.cinema_menu = ttk.Combobox(self, textvariable=self.cinema_var)
        self.cinema_menu.grid(row=3, column=1, padx=10, pady=5)

        self.display_films()
        
        self.display_seats()
        
        self.display_cinemas()
        

        self.film_menu.bind("<<ComboboxSelected>>", self.display_showtimes)
        
        #self.seat_menu.bind("<<ComboboxSelected>>", self.display_seats)

        ttk.Label(self, text="Number of Tickets").grid(row=4, column=0, padx=10, pady=5)
        self.ticket_count_var = tk.IntVar()
        self.ticket_count_var.set(1)
        ttk.Entry(self, textvariable=self.ticket_count_var).grid(row=4, column=1, padx=10, pady=5)

        ttk.Button(self, text="Check Seats", command=self.check_seats).grid(row=5, column=0, columnspan=2, padx=10, pady=5)

        self.booking_result = ttk.Label(self, text="")
        self.booking_result.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

    def display_films(self):
        # Populate films from the database
        self.cursor.execute("SELECT title FROM films")
        films = [film[0] for film in self.cursor.fetchall()]
        self.film_menu.config(values=films)
        
    def display_cinemas(self):
        # Populate cinemas from the database
        self.cursor.execute("SELECT cinema_name FROM cinemas")
        cinemas = [cinema[0] for cinema in self.cursor.fetchall()]
        self.cinema_menu.config(values=cinemas)
        
    def display_seats(self):
        seats = ["Lower Hall", "Upper Hall", "VIP"]
        self.seat_menu.config(values=seats)

    def display_showtimes(self, event):
        selected_film = self.film_var.get()
        #self.cursor.execute("SELECT showtimes FROM films WHERE title = ?", (selected_film,))
        #film_id = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT showtimes FROM films WHERE title = ?", (selected_film,))
        showtimes = self.cursor.fetchone()
        #showtimes = [st[0] for st in self.cursor.fetchall()]

        self.showtimes_var.set(showtimes[0])
        self.showtimes_menu.config(values=showtimes)

    def check_seats(self):
        selected_film = self.film_var.get()
        selected_seat = self.seat_var.get()
        selected_showtime = self.cursor.execute("SELECT showtimes FROM films WHERE title = ?", (selected_film,))
        selected_showtime = self.cursor.fetchone()
        
        #SPENT TOO MUCH TIME TRYING TO FIGURE OUT WHY THIS STUFF WASNT BEING STORED IN THE DATABASE. TURNS OUT THE ABOVE "selected_showtime" CODE GIVES A TUPLE AND THAT WAS THE PROBLEM THE WHOLE TIME.
        selected_showtime = selected_showtime[0]  # Accessing the first (and only) item in the tuple
        
        #if check seats button dont work this line below is the problem
        customer_name = current_user_id
        #selected_showtime = self.showtimes_var.get()
        
        #Seat Price Calculation
        if selected_seat == "VIP":
            price = 39.99
            
        elif selected_film == "Lower Hall":
            price = 19.99
        else:
            price = 9.99
            
        #Ticket * Price Calculation
        

        # Randomly determine seat availability
        if random.choice([True, False]):
            booking_ref = str(random.randint(1000, 9999))
            ticket_count = self.ticket_count_var.get()
            booking_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            total_price = price * ticket_count
            cinema = self.cinema_var.get()

            self.booking_result.config(
                text=f"Booking confirmed!\nReference: {booking_ref}\nFilm: {selected_film}\nShowtime: {selected_showtime}\nTickets: {ticket_count}\nCustomer Name: {customer_name}\nBooking Date: {booking_date}\nTotal Price: ${total_price}"
            )

            # Insert booking into the database
            
            
            self.cursor.execute(
                "INSERT INTO bookings (film, showtime, ticket_count, booking_reference, booking_date, total_price, cinema, customer_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (selected_film, selected_showtime, ticket_count, booking_ref, booking_date, total_price, cinema, customer_name)
            )
            
            conn.commit()
            

        else:
            self.booking_result.config(text="Seats not available. Please try again later.")

# MAYBE USEFUL LATER
    #def get_logged_in_username(self):
    # Assuming 'current_user_id' is available and contains the ID of the logged-in user
        #try:
            # Execute the query to fetch the username of the logged-in user
            #self.cursor.execute("SELECT user_id FROM users WHERE id = ?", (current_user_id,))
            # Fetch the result
            #username = self.cursor.fetchone()
            #if username:
                #return username[0]  # Return the username if available
            #else:
                #return None  # Return None if no user is found
        #except Exception as e:
            #print(f"Error getting logged in username: {e}")
            #return None 

    def get_film_id(self, film_title):
        self.cursor.execute("SELECT id FROM films WHERE title = ?", (film_title,))
        return self.cursor.fetchone()[0]

    def get_showtime_id(self, showtime):
        selected_film = self.film_var.get()
        self.cursor.execute("SELECT id FROM showtimes WHERE film_id = ? AND time = ?", (self.get_film_id(selected_film), showtime))
        return self.cursor.fetchone()[0]

# Cancellation Tab
class CancellationTab(ttk.Frame):
    def __init__(self, parent, cursor):
        super().__init__(parent)
        self.cursor = cursor

        ttk.Label(self, text="Booking Reference").grid(row=0, column=0, padx=10, pady=5)
        self.cancellation_ref = tk.StringVar()
        ttk.Entry(self, textvariable=self.cancellation_ref).grid(row=0, column=1, padx=10, pady=5)

        ttk.Button(self, text="Cancel Booking", command=self.cancel_booking).grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        self.cancellation_result = ttk.Label(self, text="")
        self.cancellation_result.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

    def cancel_booking(self):
        ref = self.cancellation_ref.get()

        # Simulate cancellation logic
        self.cursor.execute("DELETE FROM bookings WHERE booking_reference = ?", (ref,))
        conn.commit()

        if self.cursor.rowcount > 0:
            self.cancellation_result.config(text=f"Booking {ref} has been cancelled.")
        else:
            self.cancellation_result.config(text="Invalid booking reference.")
            
            
# GUI for admin view
def admin_gui():
    admin_window = tk.Toplevel()
    admin_window.title("Admin View")
    # Admin Tab

 # Create the cursor object
    cursor = conn.cursor()

# Create an instance of the AdminTab class
    admin_tab = AdminTab(admin_window, cursor)
    admin_tab.pack(fill=tk.BOTH, expand=True)

# Admin Tab
class AdminTab(ttk.Frame):
    def __init__(self, parent, cursor):
        super().__init__(parent)
        self.cursor = cursor
        
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        add_film_tab = AddFilmTab(notebook, cursor, conn)
        film_list_tab = FilmList(notebook)
        edit_film_tab = EditFilmTab(notebook, cursor, conn)
        user_list_tab = UserList(notebook)
        manage_staff_tab = ManageStaffTab(notebook, cursor, conn)
        booking_reports_tab = BookingReports(notebook, cursor)
        revenue_reports_tab = RevenueReports(notebook, cursor)

        notebook.add(add_film_tab, text="Add Film")
        notebook.add(film_list_tab, text="Film List")
        notebook.add(edit_film_tab, text="Edit Film")
        notebook.add(user_list_tab, text="User List")
        notebook.add(manage_staff_tab, text="Manage Staff")
        notebook.add(booking_reports_tab, text="Booking Reports")
        notebook.add(revenue_reports_tab, text="Revenue Reports")
        

class AddFilmTab(ttk.Frame):
    def __init__(self, parent, cursor, conn):
        super().__init__(parent)
        self.cursor = cursor
        self.conn = conn
        
        # Fields for managing films
        ttk.Label(self, text="Film Title").grid(row=0, column=0, padx=10, pady=5)
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(self, textvariable=self.title_var)
        title_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self, text="Description").grid(row=1, column=0, padx=10, pady=5)
        self.description_var = tk.StringVar()
        description_entry = ttk.Entry(self, textvariable=self.description_var)
        description_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(self, text="Actors").grid(row=2, column=0, padx=10, pady=5)
        self.actors_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.actors_var).grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(self, text="Genre").grid(row=3, column=0, padx=10, pady=5)
        self.genre_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.genre_var).grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(self, text="Age Rating").grid(row=4, column=0, padx=10, pady=5)
        self.age_rating_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.age_rating_var).grid(row=4, column=1, padx=10, pady=5)
        
        ttk.Label(self, text="Show Times").grid(row=5, column=0, padx=10, pady=5)
        self.showtimes_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.showtimes_var).grid(row=5, column=1, padx=10, pady=5)

        ttk.Button(self, text="Add Film", command=self.add_film).grid(row=6, column=0, columnspan=2, padx=10, pady=5)

        self.add_film_result = ttk.Label(self, text="")
        self.add_film_result.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

    def add_film(self):
        new_film = {
            "title": self.title_var.get(),
            "description": self.description_var.get(),
            "actors": self.actors_var.get(),
            "genre": self.genre_var.get(),
            "age_rating": self.age_rating_var.get(),
            "showtimes": self.showtimes_var.get()
        }

        self.cursor.execute(
            "INSERT INTO films (title, description, actors, genre, age_rating, showtimes) VALUES (?, ?, ?, ?, ?, ?)",
            (new_film["title"], new_film["description"], new_film["actors"], new_film["genre"], new_film["age_rating"], new_film["showtimes"])
        )

        conn.commit()
        self.add_film_result.config(text=f"Film '{new_film['title']}' added successfully.")

       
class FilmList(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.cursor = cursor

        self.tree = ttk.Treeview(self, columns=("Title", "Description", "Actors", "Genre", "Age Rating", "Showtimes"))
        self.tree.heading("#0", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Actors", text="Actors")
        self.tree.heading("Genre", text="Genre")
        self.tree.heading("Age Rating", text="Age Rating")
        self.tree.heading("Showtimes", text="Showtimes")
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.populate_treeview()

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        try:
            self.cursor.execute("SELECT * FROM films")
            films = self.cursor.fetchall()
            for film in films:
                self.tree.insert("", "end", text=film[0], values=(film[1], film[2], film[3], film[4], film[5], film[6]))
        except Exception as e:
            print(f"Error fetching films: {e}")
        
        
class EditFilmTab(ttk.Frame):
    def __init__(self, parent, cursor, conn):
        super().__init__(parent)
        self.cursor = cursor
        self.conn = conn

        # Setup the Treeview to display films
        # (Your existing code for setting up Treeview)

        # Components for selecting a film by ID
        ttk.Label(self, text="Enter Film ID to Edit:").grid(row=0, column=0, padx=10, pady=5)
        self.film_id_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.film_id_var).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(self, text="Load Film", command=self.load_film).grid(row=0, column=2, padx=10, pady=5)
        self.edit_film_result = ttk.Label(self, text="")
        self.edit_film_result.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        # Fields for editing film details
        ttk.Label(self, text="Title").grid(row=2, column=0, padx=10, pady=5)
        self.title_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.title_var).grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(self, text="Description").grid(row=3, column=0, padx=10, pady=5)
        self.description_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.description_var, width=50).grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Label(self, text="Actors").grid(row=4, column=0, padx=10, pady=5)
        self.actors_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.actors_var, width=50).grid(row=4, column=1, padx=10, pady=5)

        ttk.Label(self, text="Genre").grid(row=5, column=0, padx=10, pady=5)
        self.genre_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.genre_var, width=50).grid(row=5, column=1, padx=10, pady=5)

        ttk.Label(self, text="Age Rating").grid(row=6, column=0, padx=10, pady=5)
        self.age_rating_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.age_rating_var).grid(row=6, column=1, padx=10, pady=5)

        ttk.Label(self, text="Showtimes").grid(row=7, column=0, padx=10, pady=5)
        self.showtimes_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.showtimes_var, width=50).grid(row=7, column=1, padx=10, pady=5)

        ttk.Button(self, text="Update Film", command=self.update_film).grid(row=8, column=0, columnspan=3, padx=10, pady=5)

    def load_film(self):
        film_id = self.film_id_var.get()
        try:
            self.cursor.execute("SELECT * FROM films WHERE id = ?", (film_id,))
            film = self.cursor.fetchone()
            if film:
                # Display film details in the entry fields
                self.title_var.set(film[1])
                self.description_var.set(film[2])
                self.actors_var.set(film[3])
                self.genre_var.set(film[4])
                self.age_rating_var.set(film[5])
                self.showtimes_var.set(film[6])
                
                self.edit_film_result.config(text=f"Loaded Film ID '{film_id}'")
            else:
                self.edit_film_result.config(text="No film found with that ID.")
        except Exception as e:
            self.edit_film_result.config(text=f"Error loading film: {e}")

    def update_film(self):
        film_id = self.film_id_var.get()
        title = self.title_var.get()
        description = self.description_var.get()
        actors = self.actors_var.get()
        genre = self.genre_var.get()
        age_rating = self.age_rating_var.get()
        showtimes = self.showtimes_var.get()

        try:
            self.cursor.execute(
            "UPDATE films SET title = ?, description = ?, actors = ?, genre = ?, age_rating = ?, showtimes = ? WHERE id = ?",
            (title, description, actors, genre, age_rating, showtimes, film_id)  # Update this line
        )
            self.conn.commit()
            self.edit_film_result.config(text=f"Film ID '{film_id}' updated successfully.")
        except Exception as e:
            self.edit_film_result.config(text=f"Error updating film: {e}")
            

class UserList(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.cursor = cursor

        self.tree = ttk.Treeview(self, columns=("Username", "Role"))
        self.tree.heading("#0", text="ID")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Role", text="Role")
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.populate_treeview()

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        try:
            self.cursor.execute("SELECT id, user_id, role FROM users")
            users = self.cursor.fetchall()
            for user in users:
                self.tree.insert("", "end", text=user[0], values=(user[1], user[2]))
        except Exception as e:
            print(f"Error fetching users: {e}")
   
        
class ManageStaffTab(ttk.Frame):
    def __init__(self, parent, cursor, conn):
        super().__init__(parent)
        self.cursor = cursor
        self.conn = conn

        
        # Components for selecting a user by ID
        ttk.Label(self, text="Enter User ID:").grid(row=0, column=0, padx=10, pady=5)
        self.user_id_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.user_id_var).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(self, text="Load User Details", command=self.load_user).grid(row=0, column=2, padx=10, pady=5)
        self.edit_user_result = ttk.Label(self, text="")
        self.edit_user_result.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        # Fields for editing user details
        ttk.Label(self, text="Username").grid(row=2, column=0, padx=10, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.username_var).grid(row=2, column=1, padx=10, pady=5)

        #ttk.Label(self, text="Password").grid(row=3, column=0, padx=10, pady=5)
        #self.password_var = tk.StringVar()
        #ttk.Entry(self, textvariable=self.password_var, width=50).grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Label(self, text="Role").grid(row=4, column=0, padx=10, pady=5)
        self.role_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.role_var, width=50).grid(row=4, column=1, padx=10, pady=5)

        

        ttk.Button(self, text="Update User Details", command=self.update_user).grid(row=8, column=0, columnspan=3, padx=10, pady=5)

    def load_user(self):
        user_id = self.user_id_var.get()
        try:
            self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = self.cursor.fetchone()
            if user:
                # Display user details in the entry fields
                self.username_var.set(user[1])
                #self.password_var.set(user[2])
                self.role_var.set(user[3])
                
                
                self.edit_user_result.config(text=f"Loaded User ID '{user_id}'")
            else:
                self.edit_user_result.config(text="No User found with that ID.")
        except Exception as e:
            self.edit_user_result.config(text=f"Error loading user: {e}")

    def update_user(self):
        user_id = self.user_id_var.get()
        username = self.username_var.get()
        #password = self.password_var.get()
        role = self.role_var.get()
        

        try:
            self.cursor.execute(
            "UPDATE users SET user_id = ?, role = ? WHERE id = ?",  # user_id here is because table has column user_id
            (username, role, user_id)  # We use username variable here for updating the user_id in the table, because we used a user_id variable before in this class with numbers
        )
            self.conn.commit()
            self.edit_user_result.config(text=f"User ID '{user_id}' updated successfully.")
        except Exception as e:
            self.edit_user_result.config(text=f"Error updating user: {e}")
            

class BookingReports(ttk.Frame):
    def __init__(self, parent, cursor):
        super().__init__(parent)
        self.cursor = cursor

        self.tree = ttk.Treeview(self, columns=("Film", "Showtime", "Tickets", "Booking Reference", "Booking Date", "Total Price", "Cinema", "Customer Name", "Status"))
        self.tree.heading("#0", text="ID")
        self.tree.heading("Film", text="Film")
        self.tree.heading("Showtime", text="Showtime")
        self.tree.heading("Tickets", text="Tickets")
        self.tree.heading("Booking Reference", text="Booking Reference")
        self.tree.heading("Booking Date", text="Booking Date")
        self.tree.heading("Total Price", text="Total Price")
        self.tree.heading("Cinema", text="Cinema")
        self.tree.heading("Customer Name", text="Customer Name")
        self.tree.heading("Status", text="Status")
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.populate_treeview()

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        try:
            self.cursor.execute("SELECT * FROM booking_report")
            bookings = self.cursor.fetchall()
            for booking in bookings:
                self.tree.insert("", "end", text=booking[0], values=(booking[1], booking[2], booking[3], booking[4], booking[5], booking[6], booking[7], booking[8], booking[9]))
        except Exception as e:
            print(f"Error fetching bookings: {e}")
            
            
class RevenueReports(ttk.Frame):
    def __init__(self, parent, cursor):
        super().__init__(parent)
        self.cursor = cursor
        
        
        # Set up a dropdown (Combobox) for cinema selection
        self.tree = ttk.Treeview(self, columns=("Cinema", "Money Earned"))
        self.tree.heading("#0", text="ID")
        self.tree.heading("Cinema", text="Cinema")
        self.tree.heading("Money Earned", text="Money Earned")
        self.tree.grid(row=0, column=0, sticky="nsew")
        

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        
        ttk.Label(self, text="Cinema").grid(row=0, column=1, padx=10, pady=5)
        self.cinema_var = tk.StringVar()
        self.cinema_menu = ttk.Combobox(self, textvariable=self.cinema_var)
        self.cinema_menu.grid(row=0, column=2, padx=10, pady=5)

        
        self.display_cinemas()
        
        #Loaded the function normally before like the above line
        
        # Bind the Combobox selection event
        self.cinema_menu.bind('<<ComboboxSelected>>', lambda e: self.load_filtered())
        
        #Generate Report Button
        
        ttk.Button(self, text=f"Generate Revenue Report For Selected Cinema", command=self.generate_report).grid(row=0, column=3, columnspan=2, padx=10, pady=5)
        
        
    def display_cinemas(self):
        # Populate cinemas from the database
        self.cursor.execute("SELECT cinema_name FROM cinemas")
        cinemas = [cinema[0] for cinema in self.cursor.fetchall()]
        self.cinema_menu.config(values=cinemas)



    def load_filtered(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        selected_cinema = self.cinema_var.get()
        selected_status = "approved"
        
        try:
            self.cursor.execute(
                "SELECT id, cinema, total_price FROM booking_report WHERE status = ? AND cinema = ?", (selected_status, selected_cinema)
                )
            
            
            reports = self.cursor.fetchall()
            

            
            for report in reports:
                self.tree.insert("", "end", text=report[0], values=(report[1], report[2]))  #SPENT SO MUCH TIME WITH THE WRONG INDEX VALUES 
        except Exception as e:
            print(f"Error fetching data: {e}")
            
            
    def generate_report(self):
        
        self.report_result = ttk.Label(self, text="")
        self.report_result.grid(row=1, column=1, columnspan=2, padx=10, pady=5)
        
        selected_cinema = self.cinema_var.get()
        selected_status = "approved"
        
        # Calculate the sum of a specific column in the database table
        self.cursor.execute("SELECT SUM (total_price) FROM booking_report WHERE status = ? AND cinema = ?", (selected_status, selected_cinema))
        total_sum = self.cursor.fetchone()[0]  # Fetch the sum value from the query result
        
        self.report_result.config(
                text=f"Total Money Earned by {selected_cinema} = {total_sum}"
            )
       
        
        
        
        
# GUI for manager view
def manager_gui():
    manager_window = tk.Toplevel()
    manager_window.title("Manager View")
    # manager Tab

 # Create the cursor object
    cursor = conn.cursor()

# Create an instance of the ManagerTab class
    manager_tab = ManagerTab(manager_window, cursor)
    manager_tab.pack(fill=tk.BOTH, expand=True)

# Manager Tab
class ManagerTab(ttk.Frame):
    def __init__(self, parent, cursor):
        super().__init__(parent)
        self.cursor = cursor

        # Fields for adding new cinemas
        ttk.Label(self, text="City").grid(row=0, column=0, padx=10, pady=5)
        self.city_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.city_var).grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self, text="Cinema Name").grid(row=1, column=0, padx=10, pady=5)
        self.cinema_name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.cinema_name_var).grid(row=1, column=1, padx=10, pady=5)

        ttk.Button(self, text="Add Cinema", command=self.add_cinema).grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        self.add_cinema_result = ttk.Label(self, text="")
        self.add_cinema_result.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

    def add_cinema(self):
        city = self.city_var.get()
        cinema_name = self.cinema_name_var.get()

        if city and cinema_name:
            self.cursor.execute(
                "INSERT INTO cinemas (city, cinema_name) VALUES (?, ?)",
                (city, cinema_name)
            )

            conn.commit()
            self.add_cinema_result.config(text=f"Cinema '{cinema_name}' added to city '{city}'.")
        else:
            self.add_cinema_result.config(text="City or Cinema Name cannot be empty.")
            
# GUI for booking staff view
def booking_staff_gui():
    bookings_window = tk.Toplevel()
    bookings_window.title("Booking Staff View")
    # user Tab

 # Create the cursor object
    cursor = conn.cursor()

# Create an instance of the A BookingsTab class
    bookings_tab = Booking_Staff_Tab(bookings_window, cursor)
    bookings_tab.pack(fill=tk.BOTH, expand=True)
    
    
# Admin Tab
class Booking_Staff_Tab(ttk.Frame):
    def __init__(self, parent, cursor):
        super().__init__(parent)
        self.cursor = cursor
        
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        
        bookings_list_tab = BookingsTab(notebook, cursor)
        approve_booking_tab = ManageBookings(notebook, cursor, conn)
        

        
        notebook.add(bookings_list_tab, text="Bookings List")
        notebook.add(approve_booking_tab, text="Approve/Reject Bookings")
        
    
    
class BookingsTab(ttk.Frame):
    def __init__(self, parent, cursor):
        super().__init__(parent)
        self.cursor = cursor

        self.tree = ttk.Treeview(self, columns=("Film", "Showtime", "Tickets", "Booking Reference Number", "Date", "Total Price", "Cinema", "Username"))
        self.tree.heading("#0", text="ID")
        self.tree.heading("Film", text="Film")
        self.tree.heading("Showtime", text="Showtime")
        self.tree.heading("Tickets", text="Tickets")
        self.tree.heading("Booking Reference Number", text="Booking Reference Number")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Total Price", text="Total Price")
        self.tree.heading("Cinema", text="Cinema")
        self.tree.heading("Username", text="Username")
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.populate_treeview()

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        try:
            self.cursor.execute("SELECT * FROM bookings")
            bookings = self.cursor.fetchall()
            for booking in bookings:
                self.tree.insert("", "end", text=booking[0], values=(booking[1], booking[2], booking[3], booking[4], booking[5], booking[6], booking[7], booking[8]))
        except Exception as e:
            print(f"Error fetching bookings: {e}")
            

class ManageBookings(ttk.Frame):
    def __init__(self, parent, cursor, conn):
        super().__init__(parent)
        self.cursor = cursor
        self.conn = conn

        # Setup the Treeview to display films
        # (Your existing code for setting up Treeview)

        # Components for selecting a film by ID
        ttk.Label(self, text="Enter Booking ID to Edit:").grid(row=0, column=0, padx=10, pady=5)
        self.booking_id_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.booking_id_var).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(self, text="Load Booking", command=self.load_booking).grid(row=0, column=2, padx=10, pady=5)
        self.edit_booking_result = ttk.Label(self, text="")
        self.edit_booking_result.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        # Fields for editing booking details
        ttk.Label(self, text="Film").grid(row=2, column=0, padx=10, pady=5)
        self.film_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.film_var).grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(self, text="Showtime").grid(row=3, column=0, padx=10, pady=5)
        self.showtime_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.showtime_var, width=50).grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Label(self, text="Tickets").grid(row=4, column=0, padx=10, pady=5)
        self.tickets_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.tickets_var, width=50).grid(row=4, column=1, padx=10, pady=5)

        ttk.Label(self, text="Booking Reference Number").grid(row=5, column=0, padx=10, pady=5)
        self.ref_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.ref_var, width=50).grid(row=5, column=1, padx=10, pady=5)

        ttk.Label(self, text="Date").grid(row=6, column=0, padx=10, pady=5)
        self.date_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.date_var).grid(row=6, column=1, padx=10, pady=5)
        
        ttk.Label(self, text="Total Price").grid(row=7, column=0, padx=10, pady=5)
        self.total_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.total_var).grid(row=7, column=1, padx=10, pady=5)
        
        ttk.Label(self, text="Cinema").grid(row=8, column=0, padx=10, pady=5)
        self.cinema_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.cinema_var).grid(row=8, column=1, padx=10, pady=5)

        ttk.Label(self, text="Username").grid(row=9, column=0, padx=10, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.username_var, width=50).grid(row=9, column=1, padx=10, pady=5)
        
        #status variable
        self.status_var = tk.StringVar()

        ttk.Button(self, text="Approve Booking", command=self.approve_booking).grid(row=10, column=0, columnspan=3, padx=10, pady=5)
        ttk.Button(self, text="Reject Booking", command= self.reject_booking).grid(row=11, column=0, columnspan=3, padx=10, pady=5)

    def load_booking(self):
        booking_id = self.booking_id_var.get()
        try:
            self.cursor.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
            booking = self.cursor.fetchone()
            if booking:
                # Display booking details in the entry fields
                self.film_var.set(booking[1])
                self.showtime_var.set(booking[2])
                self.tickets_var.set(booking[3])
                self.ref_var.set(booking[4])
                self.date_var.set(booking[5])
                self.total_var.set(booking[6])
                self.cinema_var.set(booking[7])
                self.username_var.set(booking[8])
                self.status_var.set("approved")
                
                self.edit_booking_result.config(text=f"Loaded Booking ID '{booking_id}'")
            else:
                self.edit_booking_result.config(text="No Booking found with that ID.")
        except Exception as e:
            self.edit_booking_result.config(text=f"Error loading Booking: {e}")

    def approve_booking(self):
        status = self.status_var.get()
        booking_id = self.booking_id_var.get()
        film = self.film_var.get()
        showtime = self.showtime_var.get()
        tickets = self.tickets_var.get()
        ref = self.ref_var.get()
        date = self.date_var.get()
        total = self.total_var.get()
        cinema = self.cinema_var.get()
        username = self.username_var.get()
        

        try:
            
            
            self.cursor.execute(
            "INSERT INTO booking_report (film, showtime, tickets, booking_reference, booking_date, total_price, cinema, customer_name, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (film, showtime, tickets, ref, date, total, cinema, username, status)  # Update this line
        )
            self.conn.commit()
            self.edit_booking_result.config(text=f"Booking ID '{booking_id}' has been approved.")
        except Exception as e:
            self.edit_booking_result.config(text=f"Error updating booking: {e}")
            
    def reject_booking(self):
        status = "rejected"
        booking_id = self.booking_id_var.get()
        film = self.film_var.get()
        showtime = self.showtime_var.get()
        tickets = self.tickets_var.get()
        ref = self.ref_var.get()
        date = self.date_var.get()
        total = self.total_var.get()
        cinema = self.cinema_var.get()
        username = self.username_var.get()
        

        try:
            
            
            self.cursor.execute(
           "INSERT INTO booking_report (film, showtime, tickets, booking_reference, booking_date, total_price, cinema, customer_name, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (film, showtime, tickets, ref, date, total, cinema, username, status)  # Update this line
        )
            self.conn.commit()
            self.edit_booking_result.config(text=f"Booking ID '{booking_id}' has been rejected.")
        except Exception as e:
            self.edit_booking_result.config(text=f"Error updating booking: {e}")

# Main application execution
#if __name__ == "__main__":
    #app = FilmBookingSystem()
    #app.protocol("WM_DELETE_WINDOW", app.on_closing)
    #app.mainloop()

# Main function to start the application
def main():
    login_gui()

if __name__ == "__main__":
    main_page()