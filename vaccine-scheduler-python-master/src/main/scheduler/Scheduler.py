from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patient WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def login_patient(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
    if len(tokens) != 2:
        print("Please try again!")
        return
    cm = ConnectionManager()
    conn = cm.create_connection()
    search = 'SELECT A.Username, V.Name, V.Doses FROM Availabilities AS A, Vaccines AS V WHERE A.Time = %s ORDER BY A.Username;'
    search_2 = "SELECT A.Username, V.Name, V.Doses FROM Availabilities AS A, Vaccines AS V WHERE A.Time = %s AND A.Username not IN (SELECT C.Username FROM Appointmentcheck AS C WHERE C.Time = %s) ORDER BY A.Username;"
    date = tokens[1]
    month, day, year = date.split('-')
    date = datetime.datetime(int(year),int(month),int(day))
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(search_2, (date,date))
        for row in cursor:
            print(str(row['Username']) + ' ' + str(row['Name']) + ' ' + str(row["Doses"]))
    except Exception as e:
        print("please try again")
        print("Error:", e)
    finally:
        cm.close_connection()
    return



def reserve(tokens):
    global current_caregiver
    global current_patient
    if current_patient is None and current_caregiver is None:
        print("please login first")
        return
    elif current_caregiver is not None:
        print("please login as patient!")
        return
    if len(tokens) != 3:
        print("Please try again!")
        return
    cm = ConnectionManager()
    conn = cm.create_connection()
    find_caregiver = "SELECT A.Username, A.Time FROM Availabilities AS A WHERE A.Time = %s AND A.Username not IN (SELECT C.Username FROM Appointmentcheck AS C WHERE C.Time = %s)ORDER BY A.Username;"
    add_appointment = "INSERT INTO Appointment (patientname, Vaccinesname) VALUES (%s, %s);"
    find_id = "SELECT * FROM Appointment ORDER BY Appointmentid DESC;"
    insert_into_check = "INSERT INTO Appointmentcheck (Time, Username, Appointmentid) VALUES (%s, %s, %s);"
    get_left_doses = "SELECT Doses FROM Vaccines WHERE Name = %s"
    reduce_doses = "UPDATE Vaccines SET Doses = %d WHERE Name = %s"
    date = tokens[1]
    month, day, year = date.split('-')
    date = datetime.datetime(int(year),int(month),int(day))
    vaccine = str(tokens[2])
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(find_caregiver, (date, date))
        row = cursor.fetchone()
    #check whether there is caregiver at that time.
        if row is None:
            print("no Caregiver is availiable!")
            return
        else:
            caregiver_name = str(row["Username"])
    #check whether there are enough vaccine.
        cursor.execute(get_left_doses, vaccine)
        row = cursor.fetchone()
        if row is None:
            print("no such vaccine is availiable!")
            return
        else:
            doses = int(row["Doses"])
        if doses <= 0:
            print("Not enough available doses!")
            return
    #add this in appointment_records.
        cursor.execute(add_appointment, (current_patient.username, vaccine))
        cursor.execute(find_id)
        row = cursor.fetchone()
        id = int(row["Appointmentid"])
    #add this in appointmentcheck.
        cursor.execute(insert_into_check, (date, caregiver_name, id))
    #reduce one dose for desired vaccine.
        cursor.execute(reduce_doses, (doses -1, vaccine))
        conn.commit()
        print("AppointmentID: " + str(id) + ", Caregiver username: " + caregiver_name)
        print("reserve successfully")
    except Exception as e:
        print("please try again")
        print("Error:", e)
    finally:
        cm.close_connection()
    return





def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
    elif current_caregiver is None:
        name = current_patient.username
        identity = 'p'
    else:
        name = current_caregiver.username
        identity = 'c'
    if len(tokens) != 2:
        print("Please try again!")
        return
    cm = ConnectionManager()
    conn = cm.create_connection()
    find_id = 'SELECT * FROM Appointmentcheck AS C WHERE C.Appointmentid = %s;'
    find_id_patient = 'SELECT * FROM Appointment AS C WHERE C.Appointmentid = %s;'
    delete_appointment = 'DELETE FROM Appointmentcheck WHERE Appointmentid = %s;'
    delete_appointment_record = 'DELETE FROM Appointment WHERE Appointmentid = %s;'
    find_vaccine = 'SELECT * FROM Appointment WHERE Appointmentid = %s;'
    find_doses = 'SELECT * FROM Vaccines WHERE Name = %s;'
    add_doses = "UPDATE Vaccines SET Doses = %d WHERE Name = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(find_id, int(tokens[1]))
        row = cursor.fetchone()
        #check the appointment exist or not.
        if row is None:
            print("no that appointment")
            return
        id = int(row['Appointmentid'])
        name_caregiver = str(row['Username'])
        cursor.execute(find_id_patient, int(tokens[1]))
        name_patient = str(cursor.fetchone()['patientname'])
        #check whether the canceller is one of pateint or caregiver.
        if identity == 'c' and name_caregiver != name:
            print('you do not have the access')
            return
        elif identity == 'p' and name_patient != name:
            print('you do not have the access')
            return
        cursor.execute(find_vaccine, id)
        row = cursor.fetchone()
        v_name = str(row['Vaccinesname'])
        cursor.execute(find_doses, v_name)
        row = cursor.fetchone()
        doses = int(row['Doses'])
        #add the dose back.
        cursor.execute(add_doses, (doses+1, v_name))
        #delete the id from appointmentcheck and appointment.
        cursor.execute(delete_appointment, id)
        cursor.execute(delete_appointment_record, id)
        conn.commit()
        print("cancel successfully")
    except pymssql.Error as e:
        print("please try again")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("please try again")
        print("Error:", e)
        return



def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
    if len(tokens) != 1:
        print("Please try again!")
        return
    cm = ConnectionManager()
    conn = cm.create_connection()
    for_patient = "SELECT A.Appointmentid, A.Vaccinesname, C.Time, C.Username AS name FROM Appointment AS A, Appointmentcheck AS C WHERE A.patientname = %s AND A.Appointmentid = C.Appointmentid ORDER BY A.Appointmentid;"
    for_caregivers ="SELECT C.Appointmentid, A.Vaccinesname, C.Time, A.patientname AS name FROM Appointment AS A, Appointmentcheck AS C WHERE C.Username = %s AND A.Appointmentid = C.Appointmentid ORDER BY C.Appointmentid;"
    try:
        cursor = conn.cursor(as_dict=True)
        if current_patient is not None:
            cursor.execute(for_patient, current_patient.username)
        elif current_caregiver is not None:
            cursor.execute(for_caregivers, current_caregiver.username)
        for row in cursor:
            print(str(row['Appointmentid']) + ' ' + str(row['Vaccinesname']) + ' ' + str(row['Time']) + ' ' + str(row['name']))
        print("show successfully")
    except Exception as e:
        print("please try again")
        print("Error:", e)
    finally:
        cm.close_connection()
    return



def logout(tokens):
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
    if len(tokens) != 1:
        print("Please try again!")
        return
    try:
        current_caregiver = None
        current_patient = None
    except Exception as e:
        print("please try again")
        print("Error:", e)
    return


def print_start():
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()

def start():
    stop = False
    # print()
    # print(" *** Please enter one of the following commands *** ")
    # print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    # print("> create_caregiver <username> <password>")
    # print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    # print("> login_caregiver <username> <password>")
    # print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    # print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    # print("> upload_availability <date>")
    # print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    # print("> add_doses <vaccine> <number>")
    # print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    # print("> logout")  # // TODO: implement logout (Part 2)
    # print("> Quit")
    # print()
    print_start()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
            return
        else:
            print("Invalid operation name!")
        print_start()


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
