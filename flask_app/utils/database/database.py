import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow
from datetime import datetime, timedelta
from flask import current_app as app


class database:

    def __init__(self, purge=False):

        # Grab information from the configuration file
        self.database = 'db'
        self.host = '127.0.0.1'
        self.user = 'master'
        self.port = 3306
        self.password = 'master'
        self.tables = ['institutions', 'positions',
                       'experiences', 'skills', 'feedback', 'users']

        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption = {'oneway': {'salt': b'averysaltysailortookalongwalkoffashortbridge',
                                      'n': int(pow(2, 5)),
                                      'r': 9,
                                      'p': 1
                                      },
                           'reversible': {'key': '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                           }
        # -----------------------------------------------------------------------------

    def query(self, query="SELECT * FROM users", parameters=None):

        cnx = mysql.connector.connect(host=self.host,
                                      user=self.user,
                                      password=self.password,
                                      port=self.port,
                                      database=self.database,
                                      charset='latin1'
                                      )

        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path='flask_app/database/'):
        # connect to the database
        cnx = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port,
            database=self.database,
            charset='latin1')
        cursor = cnx.cursor()

        if purge:
            # drop the exisiting tables (clear the current database)
            cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            for table in tables:
                table_name = table[0]
                cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
            cnx.commit()

        # go through each sql lite file to create the tables
        sql_files = ['flask_app/database/create_tables/users.sql', 'flask_app/database/create_tables/events.sql',
                     'flask_app/database/create_tables/invited_emails.sql', 'flask_app/database/create_tables/event_availability.sql']
        # go through each file
        for file in sql_files:
            # open the file
            with open(file, 'r') as opened_file:
                script = opened_file.read()
                try:
                    # try to the command (create table) in the file
                    cursor.execute(script)
                except mysql.connector.Error as err:
                    # print out the error that occured in creating the table
                    print(f"Error executing {file}: {err}")

        cnx.commit()
        cursor.close()
        cnx.close()

    def insertRows(self, table='table', columns=['x', 'y'], parameters=[['v11', 'v12'], ['v21', 'v22']]):

        # create connection to the database
        cnx = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port,
            database=self.database,
            charset='latin1')
        cursor = cnx.cursor()

        try:
            # write out the query
            temp = ', '.join(['%s'] * len(columns))
            query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({temp})"
            # actually do the query
            cursor.executemany(query, parameters)
            cnx.commit()
        except mysql.connector.Error as err:
            print(f"Error inserting data into {table}: {err}")

        # close connection to the database
        cursor.close()
        cnx.close()


#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################


    def createUser(self, email='me@email.com', password='password', role='user'):
        try:
            # connect to the database
            cnx = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database=self.database,
                charset='latin1')
            cursor = cnx.cursor()

            # check if the email already exists in the database
            cursor.execute(
                "SELECT COUNT(*) AS count FROM users WHERE email = %s;", (email,))
            user_exists = cursor.fetchall()[0][0]

            if user_exists != 0:
                print("User already exists in database")
                # disconnect from db
                cursor.close()
                cnx.close()
                return {'status': 2}

            # encrypt the password
            encrypt_pass = self.onewayEncrypt(password)

            # insert the user into the database
            cursor.execute(
                "INSERT INTO users (role, email, password) VALUES (%s, %s, %s);", (role, email, encrypt_pass,))

            # disconnect from the database
            cnx.commit()
            cursor.close()
            cnx.close()
        except Exception as e:
            cursor.close()
            cnx.close()
            print("Failure to create user: ", e)
            return {'status': 2}
        return {'success': 1}

    def authenticate(self, email='me@email.com', password='password'):
        try:
            # connect to the database
            cnx = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database=self.database,
                charset='latin1')
            cursor = cnx.cursor()

            # encrypt the password
            encrypt_pass = self.onewayEncrypt(password)

            # check if the email is in the users table already
            cursor.execute(
                "SELECT COUNT(*) FROM users WHERE email = %s;", (email,))
            exists = cursor.fetchall()

            # check if email and password exist in database
            cursor.execute(
                "SELECT COUNT(*) FROM users WHERE email = %s AND password = %s;", (email, encrypt_pass,))
            exists = cursor.fetchall()

            if exists[0][0] == 0:
                # old code below
                print("User does not exists in database. Cannot authenticate.")
                cursor.close()
                cnx.close()
                return {'status': 2}

            # disconnect from the database
            cursor.close()
            cnx.close()
        except Exception as e:
            # disconnect from the database
            cursor.close()
            cnx.close()
            print("Failure with authenticat: ", e)
            return {'status': 2}

        return {'success': 1}

    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt=self.encryption['oneway']['salt'],
                                          n=self.encryption['oneway']['n'],
                                          r=self.encryption['oneway']['r'],
                                          p=self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string

    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])

        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message

    # gets the role of the user
    def getUserRole(self, email):
        try:
            # connect to the database
            cnx = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database=self.database,
                charset='latin1')
            cursor = cnx.cursor()

            cursor.execute(
                "SELECT role FROM users WHERE email = %s;", (email,))
            role = cursor.fetchone()[0]

            # disconnect from the database
            cursor.close()
            cnx.close()
            return role
        except Exception as e:
            # disconnect from the database
            cursor.close()
            cnx.close()
            print("Failure with to get user role: ", e)
            return "Fail"


#######################################################################################
# Event Related
#######################################################################################

    def addEvent(self, name='event_name', start_date='2025-04-19', end_date='2025-04-19', start_time='10:17', end_time='11:00', people=['person1'], event_creator='me'):
        try:
            # connect to the database
            cnx = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database=self.database,
                charset='latin1')
            cursor = cnx.cursor()

            # put event into events table
            cursor.execute(
                "INSERT INTO events (event_name, start_date, end_date, start_time, end_time, event_creator) VALUES (%s, %s, %s, %s, %s, %s);",
                (name, start_date, end_date, start_time, end_time, event_creator)
            )
            cnx.commit()

            # get the event id of the event just added
            event_id = cursor.lastrowid

            # add each person invited to the meeting to the database correlated with the event id
            for person in people:
                cursor.execute(
                    "INSERT INTO invitees (event_id, email) VALUES(%s, %s);", (event_id, person,))
                cnx.commit()

            # for testing purposes
            cursor.execute("SELECT * FROM events;")
            temp = cursor.fetchall()
            print(temp)

            # disconnect from the database
            cursor.close()
            cnx.close()
        except Exception as e:
            # disconnect from the database
            cursor.close()
            cnx.close()
            print("Failure in adding event to db: ", e)
            return {'status': 2, 'id': 'NULL'}
        # event was added properly
        return json.dumps({'status': 1, 'id': event_id})

    # get the events a user is invited to

    def getEventsForUser(self, person):
        try:
            # connect to the database
            cnx = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database=self.database,
                charset='latin1')
            cursor = cnx.cursor()

            # get all the events that a user is invited to
            cursor.execute("SELECT events.event_id, events.event_name, events.start_date, events.end_date, events.event_creator FROM events JOIN invitees ON events.event_id = invitees.event_id WHERE invitees.email = %s;", (person,))
            temp = cursor.fetchall()

            print("ALL EVENTS", temp)

            # disconnect from the database
            cursor.close()
            cnx.close()

            all_events = [{'event_id': row[0], 'event_name': row[1], 'start_date': row[2].strftime(
                '%B %d, %Y'), 'end_date': row[3].strftime('%B %d, %Y'), 'creator': row[4]} for row in temp]
            return all_events
        except Exception as e:
            cursor.close()
            cnx.close()
            print("Failure to get events: ", e)
            return {}

    # get the event name and date range
    def getNameDateTime(self, id):
        try:
            # connect to the database
            cnx = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database=self.database,
                charset='latin1')
            cursor = cnx.cursor()

            # get all the events that a user is invited to
            cursor.execute("SELECT * FROM events WHERE event_id = %s;", (id,))
            temp = cursor.fetchone()
            # output = []
            # for i in all_events:
            #     output.append(i[0])
            print("EVENT DETAILS", temp)

            if not temp:
                print("Failure in getting event details")
                return {}

            # format the dates to something more readable
            start_date = temp[2].strftime('%B %d, %Y')
            end_date = temp[3].strftime('%B %d, %Y')

            start_time = (datetime.min + temp[4]).time()
            end_time = (datetime.min + temp[5]).time()

            event = {'event_name': temp[1], 'start_date': start_date,
                     'end_date': end_date, 'start_time': start_time, 'end_time': end_time}

            # disconnect from the database
            cursor.close()
            cnx.close()

            return event
        except Exception as e:
            cursor.close()
            cnx.close()
            print("Failure to get events: ", e)
            return {}


# add a user's availability for an event to the database

    def addEventAvailability(self, user_id, event_id, date, time, available):
        print("USER ID", user_id)
        try:
            # connect to the database
            cnx = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database=self.database,
                charset='latin1')
            cursor = cnx.cursor()

            time = datetime.strptime(time, '%I:%M %p').strftime('%H:%M:%S')

            # check if this user already had information logged for that time
            cursor.execute("SELECT COUNT(*) FROM event_availability WHERE user_id=%s AND event_id=%s AND date=%s AND time_slot=%s;",
                           (user_id, event_id, date, time,))
            need_update = cursor.fetchone()

            if need_update[0] != 1:
                # print("IN INSERT")
                # add the availability to the database
                cursor.execute("INSERT INTO event_availability(user_id, event_id, date, time_slot, availabile) VALUES (%s, %s, %s, %s, %s);", (
                    user_id, event_id, date, time, available,))
                cnx.commit()
            else:
                # print("IN UPDATE")
                # update the availability
                cursor.execute("UPDATE event_availability SET availabile=%s WHERE user_id=%s AND event_id=%s AND date=%s AND time_slot=%s;", (
                    available, user_id, event_id, date, time,))
                cnx.commit()

            # for testing
            # cursor.execute("SELECT * FROM event_availability;")
            # print(cursor.fetchall())

            # disconnect from the database
            cursor.close()
            cnx.close()
        except Exception as e:
            # disconnect from the database
            cursor.close()
            cnx.close()
            print("Failure in adding availability to db: ", e)
            return {'status': 2, 'id': 'NULL'}
        # event was added properly
        return json.dumps({'status': 1, 'id': event_id})

    # get the event availability for a user

    def getEventAvailability(self, user_id, event_id):
        output = []
        try:
            # connect to the database
            cnx = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database=self.database,
                charset='latin1')
            cursor = cnx.cursor()

            cursor.execute("SELECT * FROM event_availability;")
            print(cursor.fetchall())

            print("USER AND EVENT", user_id, event_id)

            # check that the user has something documented for the event
            cursor.execute(
                "SELECT COUNT(*) FROM event_availability WHERE user_id=%s AND event_id=%s;", (user_id, event_id,))
            test = cursor.fetchone()
            if test[0] < 1:
                # disconnect from the database
                cursor.close()
                cnx.close()
                return {'status': 2, 'data': 'NULL'}

            cursor.execute(
                "SELECT date, time_slot, availabile FROM event_availability WHERE user_id=%s AND event_id=%s;", (user_id, event_id,))
            temp = cursor.fetchall()
            for i in temp:
                row = {}
                row['date'] = i[0].strftime('%Y-%m-%d')
                total_seconds = int(i[1].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                formatted_time = datetime.strptime(
                    f"{hours:02d}:{minutes:02d}", "%H:%M").strftime("%I:%M %p")
                row['time'] = formatted_time
                row['available'] = i[2]
                output.append(row)

            # disconnect from the database
            cursor.close()
            cnx.close()
        except Exception as e:
            # disconnect from the database
            cursor.close()
            cnx.close()
            print("Failure in getting event availability: ", e)
            return {'status': 3, 'id': 'NULL'}
        # event was added properly
        return {'status': 1, 'data': output}

    # evaluate everyone' availability for the heatmap

    def getHeatMapInfo(self, event_id):
        output = {}
        try:
            # connect to the database
            cnx = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database=self.database,
                charset='latin1')
            cursor = cnx.cursor()

            # get all the availabilities for the event
            cursor.execute(
                "SELECT date, time_slot, availabile FROM event_availability WHERE event_id=%s;", (event_id,))
            data = cursor.fetchall()
            # print(data)

            for row in data:
                # go through each row to get the date, time, and availability
                date = row[0].strftime('%Y-%m-%d')
                total_seconds = int(row[1].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                time = datetime.strptime(
                    f"{hours:02d}:{minutes:02d}", "%H:%M").strftime("%I:%M %p")
                available = row[2]

                if (date, time) not in output:
                    # don't already have the date/time accounted for so add it
                    output[(date, time)] = {
                        'available': 0, 'maybe': 0, 'unavailable': 0}
                # count how many times a person is a type of available for each date time combination
                output[(date, time)][available] += 1

            # disconnect from the database
            cursor.close()
            cnx.close()
        except Exception as e:
            # disconnect from the database
            cursor.close()
            cnx.close()
            print("Failure in getting heat map info from the database: ", e)
            return {'status': 2, 'data': 'NULL'}
        # restructure the output so the return is in the right format
        temp = []
        for (date, time), c in output.items():
            temp.append({
                'date': date,
                'time': time,
                'available': c['available'],
                'maybe': c['maybe'],
                'unavailable': c['unavailable']
            })
        # event was added properly
        return {'status': 1, 'data': temp}

    def getBestTime(self, event_id):
        cnx = None
        cursor1 = None
        cursor2 = None
        try:
            cnx = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database=self.database,
                charset='latin1'
            )

            cursor1 = cnx.cursor()
            cursor1.execute("""
                SELECT date, time_slot,
                SUM(CASE WHEN availabile='available' THEN 1 ELSE 0 END) AS good,
                SUM(CASE WHEN availabile='unavailable' THEN 1 ELSE 0 END) AS bad
                FROM event_availability
                WHERE event_id=%s
                GROUP BY date, time_slot
                ORDER BY good DESC, bad ASC, date ASC, time_slot ASC;
            """, (event_id,))
            best = cursor1.fetchall()

            # no data available
            if not best:
                return {'status': 2, 'data': 'NULL'}

            first_time = int(best[0][2])
            if first_time == 0:
                # close the first cursor before the second query
                cursor1.close()
                cursor1 = None

                cursor2 = cnx.cursor()
                cursor2.execute("""
                    SELECT date, time_slot
                    FROM event_availability
                    WHERE event_id=%s
                    ORDER BY date ASC, time_slot ASC;
                """, (event_id,))
                earliest_time = cursor2.fetchall()
                # print("EARILEST TIME", earliest_time)
                return {'status': 3, 'data': (earliest_time[0][0], earliest_time[0][1])}

            # print("BEST TIME IN DB ", best[0])
            return {'status': 1, 'data': (best[0][0], best[0][1])}

        except Exception as e:
            print("Failure in getting best time calculation from the database: ", e)
            return {'status': 4, 'data': 'NULL'}

        finally:
            if cursor1:
                cursor1.close()
            if cursor2:
                cursor2.close()
            if cnx:
                cnx.close()
