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

class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = ['institutions', 'positions', 'experiences', 'skills','feedback', 'users']
        
        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
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

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        ''' FILL ME IN WITH CODE THAT CREATES YOUR DATABASE TABLES.'''

        #should be in order or creation - this matters if you are using forign keys.
         
        # if purge:
        #     for table in self.tables[::-1]:
        #         self.query(f"""DROP TABLE IF EXISTS {table}""")
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
            
        # Execute all SQL queries in the /database/create_tables directory.
        # for table in self.tables:
            
        #     #Create each table using the .sql file in /database/create_tables directory.
        #     with open(data_path + f"create_tables/{table}.sql") as read_file:
        #         create_statement = read_file.read()
        #     self.query(create_statement)

        #     # Import the initial data
        #     try:
        #         params = []
        #         with open(data_path + f"initial_data/{table}.csv") as read_file:
        #             scsv = read_file.read()            
        #         for row in csv.reader(StringIO(scsv), delimiter=','):
        #             params.append(row)
            
        #         # Insert the data
        #         cols = params[0]; params = params[1:] 
        #         self.insertRows(table = table,  columns = cols, parameters = params)
        #     except:
        #         print('no initial data')

        # connect to the database 
        # cnx = mysql.connector.connect(
        #     host=self.host,
        #     user=self.user,
        #     password=self.password,
        #     port=self.port,
        #     database=self.database,
        #     charset='latin1')
        # cursor = cnx.cursor()

        # if purge:
        #     # drop the exisiting tables (clear the current database)
        #     cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        #     cursor.execute("SHOW TABLES;")
        #     tables = cursor.fetchall()
        #     for table in tables:
        #         table_name = table[0]
        #         cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        #     cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
        #     cnx.commit()


        # go through each sql lite file to create the tables 
        sql_files = ['flask_app/database/create_tables/feedback.sql', 'flask_app/database/create_tables/institutions.sql', 'flask_app/database/create_tables/positions.sql', 'flask_app/database/create_tables/experiences.sql', 'flask_app/database/create_tables/skills.sql', 'flask_app/database/create_tables/users.sql']
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

        # insert initial values 
        csv_files = ['flask_app/database/initial_data/institutions.csv', 'flask_app/database/initial_data/positions.csv', 'flask_app/database/initial_data/experiences.csv','flask_app/database/initial_data/skills.csv']
        
        # go through all the csv files 
        for file in csv_files: 
            # get the table name 
            table = file.split('/')[-1].replace('.csv', '')
            # open the file 
            try: 
                with open(file, 'r') as opened_file: 
                    reader = csv.reader(opened_file)
                    columns = next(reader)
                    for row in reader:
                        row = [None if val == 'NULL' else val for val in row]
                        values_placeholder = ', '.join(['%s'] * len(columns))
                        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({values_placeholder})"

                        try:
                            cursor.execute(query, row)
                        except mysql.connector.Error as err:
                            print(f"Error inserting data into {table}: {err}")
            except Exception as e: 
                print("Error occured with csv file inserting: ", e)

        cnx.commit()
        cursor.close()
        cnx.close()

    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        
        # # Check if there are multiple rows present in the parameters
        # has_multiple_rows = any(isinstance(el, list) for el in parameters)
        # keys, values      = ','.join(columns), ','.join(['%s' for x in columns])
        
        # # Construct the query we will execute to insert the row(s)
        # query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
        # if has_multiple_rows:
        #     for p in parameters:
        #         query += f"""({values}),"""
        #     query     = query[:-1] 
        #     parameters = list(itertools.chain(*parameters))
        # else:
        #     query += f"""({values}) """                      
        
        # insert_id = self.query(query,parameters)[0]['LAST_INSERT_ID()']         
        # return insert_id

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

    def getResumeData(self):
        # connect to the database
        cnx = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port,
            database=self.database,
            charset='latin1')
        cursor = cnx.cursor(dictionary = True)

        resume = {}

        # get institution data 
        cursor.execute("SELECT * FROM institutions")
        institutions = cursor.fetchall()
        for place in institutions: 
            inst_id = place['inst_id']
            resume[inst_id] = {
                'name': place['name'],
                'type': place['type'],
                'department': place.get('department'),
                'address': place.get('address'),
                'city': place.get('city'),
                'state': place.get('state'),
                'zip': place.get('zip'),
                'positions': {}
            }

            # go through positions 
            cursor.execute("SELECT * FROM positions WHERE inst_id = %s", (inst_id,))
            positions = cursor.fetchall()
            for position in positions: 
                pos_id = position['position_id']
                resume[inst_id]['positions'][pos_id] = {
                    'title': position['title'],
                    'start_date': position['start_date'],
                    'end_date': position['end_date'],
                    'responsibilities': position['responsibilities'],
                    'experiences': {}
                }
            
                # go through experience table 
                cursor.execute("SELECT * FROM experiences WHERE position_id = %s", (pos_id,))
                experiences = cursor.fetchall()
                for experience in experiences: 
                    experience_id = experience['experience_id']
                    resume[inst_id]['positions'][pos_id]['experiences'][experience_id] = {
                        'name': experience['name'],
                        'description': experience['description'],
                        'start_date': experience['start_date'],
                        'end_date': experience['end_date'],
                        'hyperlink': experience.get('hyperlink'),
                        'skills': {}
                    }

                    # go through skills table
                    cursor.execute("SELECT * FROM skills WHERE experience_id = %s", (experience_id,))
                    skills = cursor.fetchall()
                    for skill in skills: 
                        skill_id = skill['skill_id']
                        resume[inst_id]['positions'][pos_id]['experiences'][experience_id]['skills'][skill_id] = {
                            'name': skill['name'],
                            'skill_level': skill['skill_level']
                        }

        # close connection with database 
        cursor.close()
        cnx.close()
        # format resume before returning for easier reading 
        #resume = json.dumps(resume, indent=4, default=str)
        return (resume)


    def getFeedbackRows(self): 
     # connect to the database
        cnx = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port,
            database=self.database,
            charset='latin1')
        cursor = cnx.cursor(dictionary = True)

        query = f"SELECT * FROM feedback"
    
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error retrieving data from feedback: {err}")
            rows = []

        cursor.close()
        cnx.close()
        return(rows)

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
            cursor.execute("SELECT COUNT(*) AS count FROM users WHERE email = %s;", (email,))
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
            cursor.execute("INSERT INTO users (role, email, password) VALUES (%s, %s, %s);", (role, email, encrypt_pass,))
            
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

        
            # check if email and password exist in database 
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s AND password = %s;", (email, encrypt_pass,))
            exists = cursor.fetchall()

            if exists[0][0] == 0: 
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
            print("Failure with authenticate: ", e)
            return {'status': 2}

        return {'success': 1}

    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
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

            cursor.execute("SELECT role FROM users WHERE email = %s;", (email,))
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

