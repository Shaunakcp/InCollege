import sqlite3           # database used to store account & job information
import datetime
import os


class Message:
    def __init__(self, dbName):
        self._db = sqlite3.connect(f"./{dbName}.db")
        self._cur = self._db.cursor()
        self._cur.execute("CREATE TABLE IF NOT EXISTS messages ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'message' TEXT, 'sender' TEXT, 'receiver' TEXT, 'datetime' TEXT, 'read' TEXT)")
        self._db.commit()
    
    def addMessage(self, message, sender, receiver):
        currentDateTime = datetime.datetime.now()
        self._cur.execute("INSERT INTO messages (message, sender, receiver, datetime, read) VALUES (?, ?, ?, ?, ?)", (message, sender, receiver, currentDateTime, "no"))
        self.commit()

    def getMessages(self, receiver):
        rows = self._cur.execute("SELECT * FROM messages WHERE receiver = ?", (receiver,))
        return rows.fetchall()

    def getUnreadMessages(self, receiver):
        rows = self._cur.execute("SELECT * FROM messages WHERE receiver = ? AND read = ?", (receiver, "no"))
        return rows.fetchall()

    def viewMessages(self, sender, receiver):
        rows = self._cur.execute("SELECT * FROM messages WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)", (sender, receiver, receiver, sender))
        return rows.fetchall()

    def haveUnreadMessages(self, sender, receiver):
        rows = self._cur.execute("SELECT * FROM messages WHERE sender = ? AND receiver = ? AND read = ?", (sender, receiver, "no"))
        return len(rows.fetchall()) > 0

    def haveNewMessages(self, receiver):
        rows = self._cur.execute("SELECT * FROM messages WHERE receiver = ? AND read = ?", (receiver, "no"))
        return len(rows.fetchall()) > 0

    def listOfSenders(self, receiver):
        rows = self._cur.execute("SELECT DISTINCT messages.sender, accounts.firstname, accounts.lastname FROM messages, accounts WHERE messages.sender = accounts.username AND messages.receiver = ?", (receiver,))
        return rows.fetchall()

    def markAsRead(self, id):
        self._cur.execute("UPDATE messages SET read = ? WHERE id = ?", ("yes", id))
        self.commit()

    def deleteMessage(self, id):
        self._cur.execute("DELETE FROM messages WHERE id = ?", (id,))
        self.commit()

    def haveCommunication(self, sender, receiver):
        rows = self._cur.execute("SELECT * FROM messages WHERE sender = ? AND receiver = ?", (sender, receiver))
        return len(rows.fetchall()) > 0

    def commit(self):
        self._db.commit()

    def close(self):
        self._cur.close()
        self._db.close()


class JobApplication:
    def __init__(self, dbName): # create 2 tables for job applications and application information
        self._db = sqlite3.connect(f"./{dbName}.db")
        self._cur = self._db.cursor()
        self._cur.execute("CREATE TABLE IF NOT EXISTS jobapps ('appID' INTEGER PRIMARY KEY AUTOINCREMENT, 'applicantID' TEXT NOT NULL, 'jobID' INTEGER NOT NULL, 'title' TEXT NOT NULL, 'status' TEXT NOT NULL, 'timeapp' TEXT NOT NULL)")
        self._cur.execute("CREATE TABLE IF NOT EXISTS appinfos ('appID' INTEGER NOT NULL, 'monGrad' INTEGER, 'dayGrad' INTEGER, 'yearGrad' INTEGER, 'monStart' INTEGER, 'dayStart' INTEGER, 'yearStart' INTEGER, 'details' TEXT NOT NULL, FOREIGN KEY (appID) REFERENCES jobapps (appID) ON DELETE CASCADE)")
        self._db.commit()
        self.APIoutputHandling_appliedJobs()
        self.APIoutputHandling_savedJobs()

    def checkIfApplied(self, applicant_ID, job_ID): # check whether the user already applied for the job
        rows = self._cur.execute("SELECT COUNT(*) FROM jobapps WHERE applicantID = ? AND jobID = ? AND status = ?", (applicant_ID, job_ID, 'applied'))
        for row in rows:
            if row[0] != 0:
                return True
        return False
    
    def checkIfSaved(self, applicant_ID, job_ID): # check whether the user already saved the job
        rows = self._cur.execute("SELECT COUNT(*) FROM jobapps WHERE applicantID = ? AND jobID = ? AND status = ?", (applicant_ID, job_ID, 'saved'))
        for row in rows:
            if row[0] != 0:
                return True
        return False

    def createApplication(self, applicant_ID, job_ID): # create an application with status "applied" in jobapps table
        rows = self._cur.execute("SELECT title FROM jobs WHERE jobID = ?", (job_ID,))
        for row in rows:
            title = row[0]
        self._cur.execute("INSERT INTO jobapps ('appID', 'applicantID', 'jobID', 'title', 'status', 'timeapp') VALUES (NULL, ?, ?, ?, ?, ?)", (applicant_ID, job_ID, title, 'applied', datetime.datetime.now().strftime("%Y-%m-%d")))
        self.APIoutputHandling_appliedJobs()
        self.commit()

    def saveAJob(self, applicant_ID, job_ID): # create an application with status "saved" in jobapps table
        rows = self._cur.execute("SELECT title FROM jobs WHERE jobID = ?", (job_ID,))
        for row in rows:
            title = row[0]
        self._cur.execute("INSERT INTO jobapps ('appID', 'applicantID', 'jobID', 'title', 'status', 'timeapp') VALUES (NULL, ?, ?, ?, ?, ?)", (applicant_ID, job_ID, title, 'saved', datetime.datetime.now().strftime("%Y-%m-%d")))
        self.APIoutputHandling_savedJobs()
        self.commit()

    def changeSavedToApplied(self, applicant_ID, job_ID): # change status from saved to applied
        self._cur.execute("UPDATE jobapps SET 'status' = ?, 'timeapp' = ? WHERE applicantID = ? AND jobID = ?", ("applied", datetime.datetime.now().strftime("%Y-%m-%d"), applicant_ID, job_ID))
        self.APIoutputHandling_savedJobs()
        self.commit()
    
    def unsaveAJob(self, applicant_ID, job_ID): # delete the application that is marked save from jobapps table
        self._cur.execute("DELETE FROM jobapps WHERE applicantID = ? AND jobID = ?", (applicant_ID, job_ID))
        self.APIoutputHandling_savedJobs()
        self.commit()

    def updateApplicationInfo(self, applicant_ID, job_ID, mon_grad, day_grad, year_grad, mon_start, day_start, year_start, details): # insert information about application to appinfo table after the application has been triggered
        rows = self._cur.execute("SELECT appID FROM jobapps WHERE applicantID = ? and jobID = ?", (applicant_ID, job_ID))
        appID = rows.fetchone()[0]
        self._cur.execute("INSERT INTO appinfos (appID, monGrad, dayGrad, yearGrad, monStart, dayStart, yearStart, details) VALUES (?,?,?,?,?,?,?,?)", (appID, mon_grad, day_grad, year_grad, mon_start, day_start, year_start, details))
        self.APIoutputHandling_appliedJobs()
        self.commit()

    def deletedJobNoti(self, applicant_ID): # check if there's any jobs being deleted by the employer and then refresh the jobapps table and appinfo table by deleting those expired records
        rows = self._cur.execute("SELECT title FROM jobapps WHERE applicantID = ? AND status = ?", (applicant_ID, 'deleted'))
        list = []
        for row in rows:
            list.append(row[0])
        self._cur.execute("DELETE FROM jobapps WHERE applicantID = ? AND status = ?", (applicant_ID, 'deleted'))
        self.APIoutputHandling_appliedJobs()
        self.commit()
        return list

    def haveNotApplied(self, applicant_ID):
        rows = self._cur.execute("SELECT timeapp FROM jobapps WHERE applicantID = ? AND status = ? ORDER BY appID DESC LIMIT 1", (applicant_ID, 'applied'))
        for row in rows:
            date = row[0].split('-')
            if datetime.datetime.now() - datetime.datetime(int(date[0]), int(date[1]), int(date[2])) < datetime.timedelta(7):
                return False
        return True

    def countJobApps(self, applicant_ID):
        rows = self._cur.execute("SELECT COUNT(*) FROM jobapps WHERE applicantID = ? AND status = ?", (applicant_ID, 'applied'))
        for row in rows:
            return row[0]

    def commit(self):
        self._db.commit()

    def close(self):
        self._cur.close()
        self._db.close()

    def APIoutputHandling_appliedJobs(self):
        try:
            with open("MyCollege_appliedJobs.txt", "w") as f:
                rows = self._cur.execute("SELECT title, applicantID, details FROM jobapps JOIN appinfos WHERE status = ?", ('applied',))
                for row in rows:
                    f.write(row[0] + '\n' + row[1] + '\n' + row[2] + '\n&&&\n' + '=====\n')
        except:
            print("Unable to write to MyCollege_appliedJobs.txt")

    def APIoutputHandling_savedJobs(self):
        try:
            with open("MyCollege_savedJobs.txt", "w") as f:
                rows = self._cur.execute("SELECT title, applicantID FROM jobapps WHERE status = ?", ('saved',))
                for row in rows:
                    f.write(row[0] + '\n' + row[1] + '\n=====\n')
        except:
            print("Unable to write to MyCollege_savedJobs.txt")


class JobPosting:            # class for creating job listings
    def __init__(self, dbName):
        self._db = sqlite3.connect(f"./{dbName}.db")
        self._cur = self._db.cursor()
        # Creating a table in SQL file to store account info
        self._cur.execute("CREATE TABLE IF NOT EXISTS jobs ('jobID' INTEGER PRIMARY KEY AUTOINCREMENT, 'title' TEXT NOT NULL, 'description' TEXT NOT NULL, 'employer' TEXT NOT NULL, 'location' TEXT NOT NULL, 'salary' TEXT NOT NULL, 'poster' TEXT NOT NULL, 'timepost' TEXT NOT NULL)")
        self._db.commit()
        #self.APIoutputHandling()
        self.APIinputHandling()

        
    def checkLimit(self): # Checking whether the number of jobs has reached the limit of 5
        rows = self._cur.execute("SELECT COUNT(*) FROM jobs")
        for row in rows:
            if row[0] >= 10:
                return False
        return True
    
    def addJob(self, title, description, employer, location, salary, poster):        # Add job to SQL file
        query = "INSERT INTO jobs ('jobID', 'title', 'description', 'employer', 'location', 'salary', 'poster', 'timepost') VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)"
        self._cur.execute(query, (title, description, employer, location, salary, poster, datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")))
        self.commit()
        self.APIoutputHandling()

    def createAJob(self, current_user):        # Function to create job posting
        if not self.checkLimit():
            print("ERROR: All permitted jobs have been created, please come back later")
            return
        print("\nPost your job")
        title = input("Title: ")
        description = input("Description: ")
        employer = input("Employer: ")
        location = input("Location: ")
        salary = float(input("Salary: $"))
        self.addJob(title, description, employer, location, salary, current_user)
        print("\n--Job has been posted--")

    def selfApplyCheck(self, current_user, job_ID): # func checks if curr_user is applying to own job
        rows = self._cur.execute("SELECT COUNT(*) FROM jobs WHERE poster = ? AND jobID = ?", (current_user, job_ID))
        for row in rows:
            if row[0] != 0:
                return True
        return False    

    def myJobPostings(self, current_user):       # func returns all of curr_user's posted jobs
        rows = self._cur.execute("SELECT * FROM jobs WHERE poster = ?", (current_user,))
        return rows.fetchall()

    def displayAllJobs(self):    # func returns all posted jobs
        rows = self._cur.execute("SELECT * FROM jobs")
        return rows.fetchall()

    def displayAppliedJobs(self, applicant_ID):    # func returns all jobs that curr_user applied to
        rows = self._cur.execute("SELECT jobs.* FROM jobs, jobapps WHERE jobapps.jobID = jobs.jobID AND jobapps.applicantID = ? AND jobapps.status = ?", (applicant_ID, 'applied'))
        return rows.fetchall()

    def displaySavedJobs(self, applicant_ID):    # func returns all jobs that curr_user saved
        rows = self._cur.execute("SELECT jobs.* FROM jobs, jobapps WHERE jobapps.jobID = jobs.jobID AND jobapps.applicantID = ? AND jobapps.status = ?", (applicant_ID, 'saved'))
        return rows.fetchall()
    
    def displayAJob(self, job_ID):            # func displays details about a job listing
        rows = self._cur.execute("SELECT * FROM jobs WHERE jobID = ?", (job_ID,))
        row = rows.fetchone()
        print(f"Title: {row[1]}")
        print(f"Description: {row[2]}")
        print(f"Employer: {row[3]}")
        print(f"Location: {row[4]}")
        print(f"Salary: ${float(row[5]):,.2f}")

    def deleteAJob(self, job_ID):        # func deletes job
        self._cur.execute("DELETE FROM jobs WHERE jobID = ?", (job_ID,))
        self.commit()
        self._cur.execute("UPDATE jobapps SET 'status' = ? WHERE jobID = ?", ('deleted', job_ID)) # updates job status in jobapps table to 'deleted'
        self.commit()
        self.APIoutputHandling()

    def newJobPostings(self, current_user): # func returns all new job postings
        rows = self._cur.execute("SELECT title, timepost FROM jobs WHERE poster != ?", (current_user,))
        return rows.fetchall()
            
    def commit(self):
        self._db.commit()

    def close(self):
        self._cur.close()
        self._db.close()

    def checkUniqueTitle(self, title): # func checks if job title is unique
        rows = self._cur.execute("SELECT COUNT(*) FROM jobs WHERE title = ?", (title,))
        for row in rows:
            if row[0] != 0:
                return False
        return True

    def APIinputHandling(self): # func handles input from API
        try:
            with open("newJobs.txt", 'r') as f:
                lines = f.readlines()
                data = []
                i = 0
                for line in lines:
                    if line == '=====\n':
                        if self.checkLimit() and self.checkUniqueTitle(data[0]):
                            self.addJob(data[0], data[1], data[3], data[4], float(data[5]), data[2])
                        i = 0
                        data = []
                        continue
                    if i != 1:
                        data.append(line.rstrip('\n'))
                        i += 1
                    elif line != '&&&\n':
                        if len(data) < 2:
                            data.append(line.rstrip('\n'))
                        else:
                            data[1] += '\n' + line.rstrip('\n')
                    elif line == '&&&\n':
                        i += 1
                if self.checkLimit() and data != []:
                    self.addJob(data[0], data[1], data[3], data[4], float(data[5]), data[2])
            os.remove("newJobs.txt")
        except FileNotFoundError:
            print("newJobs.txt not found")
        

    def APIoutputHandling(self): # func handles output to API
        try:
            with open("MyCollege_jobs.txt", 'w') as f:
                rows = self._cur.execute("SELECT title, description, poster, employer, location, salary FROM jobs")
                for row in rows:
                    f.write(row[0] + '\n')
                    f.write(row[1] + '\n&&&\n')
                    f.write(row[2] + '\n')
                    f.write(row[3] + '\n')
                    f.write(row[4] + '\n')
                    f.write(row[5] + '\n')
                    f.write('=====\n')
                self.commit()
        except:
            print("Unable to write to MyCollege_jobs.txt")

class SignInHistory:
    def __init__(self, dbname):
        self._db = sqlite3.connect(f"./{dbname}.db")
        self._cur = self._db.cursor()
        self._cur.execute("CREATE TABLE IF NOT EXISTS signinhistory ('username' TEXT NOT NULL, 'timesign' TEXT NOT NULL)")
        self._db.commit()
    
    def addSignIn(self, username): # func adds a new sign in to the signinhistory table
        self._cur.execute("INSERT INTO signinhistory ('username', 'timesign') VALUES (?, ?)", (username, datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")))
        self.commit()

    def lastSignIn(self, username): # func returns the last sign in of a user
        rows = self._cur.execute("SELECT timesign FROM signinhistory WHERE username = ? ORDER BY timesign DESC LIMIT 1", (username,))
        row = rows.fetchall()
        if row == []:
            return False
        date = row[0][0].split("-")
        return datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(date[3]), int(date[4]), int(date[5]))

    def commit(self): # func commits changes to the database
        self._db.commit()

    def close(self): # func closes the database
        self._cur.close()
        self._db.close()

class AccountCreation:        # class for creating accounts
    def __init__(self, dbName):
        self._db = sqlite3.connect(f"./{dbName}.db")
        self._cur = self._db.cursor()
        # Creating a table in SQL file to store account info
        self._cur.execute("CREATE TABLE IF NOT EXISTS accounts ('username' TEXT NOT NULL PRIMARY KEY, 'password' TEXT NOT NULL, 'firstname' TEXT NOT NULL, 'lastname' TEXT NOT NULL, 'university' TEXT NOT NULL, 'major' TEXT NOT NULL, 'emailnoti' TEXT NOT NULL, 'sms' TEXT NOT NULL, 'adfeatures' TEXT NOT NULL, 'languagepreference' TEXT NOT NULL, 'timecreated' TEXT NOT NULL)")
        self._cur.execute("CREATE TABLE IF NOT EXISTS membership ('username' TEXT NOT NULL, 'tier' TEXT NOT NULL, FOREIGN KEY (username) REFERENCES accounts(username) ON DELETE CASCADE) ")
        self.currentUser = None
        self.language = "English"
        self._db.commit()
        self.APIoutputHandling()
        self.APIinputHandling()
        

    def listOfUsers(self, username):        # func returns list of all usernames
        rows = self._cur.execute("SELECT username, firstname, lastname FROM accounts WHERE username != ?", (username,))
        return rows.fetchall()

    # CRUD 
    def commit(self):
        self._db.commit()

    def close(self):
        self._cur.close()
        self._db.close()

    def addAccount(self, userName, passWord, firstName, lastName, university, major): # Create new record in the Database after the input is verified
        query = "INSERT INTO accounts ('username', 'password', 'firstname', 'lastname', 'university', 'major', 'emailnoti', 'sms', 'adfeatures', 'languagepreference', 'timecreated') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        self._cur.execute(query, (userName, passWord, firstName, lastName, university, major, "On", "On", "On", "English", datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")))
        self.commit()
        self.APIoutputHandling()

    def addTier(self, userName, tier):
        self._cur.execute("INSERT INTO membership ('username', 'tier') VALUES (?, ?)", (userName, tier))
        self.commit()
        self.APIoutputHandling()

    def checkTier(self, userName): #return True if user is a Plus, False if user is a Standard
        rows = self._cur.execute("SELECT tier FROM membership WHERE username = ?", (userName,))
        for row in rows:
            if row[0] == "plus":
                return True
            else:
                return False

    def displayAccount(self):            # print all account and password
        rows = self._cur.execute("SELECT * FROM accounts")
        for row in rows:
            print(f"Account: {row[0]}\nPassword: {row[1]}")
    
    def searchAccount(self, userName):
        query = "SELECT * FROM accounts WHERE username = ?"
        rows = self._cur.execute(query, (userName,))
        res = rows.fetchall()
        return res[0]

    def deleteAccount(self):              # Delete inputed account with name
        userName = input("Enter the userName you want to delete: ")
        query = "DELETE FROM accounts WHERE username = ?"
        self._cur.execute(query, (userName,))
        self.commit()

    def searchForName(self, firstName, lastName):    # Searching SQL file by first and last name
        rows = self._cur.execute("SELECT * FROM accounts")
        for row in rows:
            if firstName == row[2] and lastName == row[3]:
                return True
        return False
        
    def checkUsername(self, userName):     # Verifying input username is in system when the user signs in
        rows = self._cur.execute("SELECT * FROM accounts")
        for row in rows:
            if userName == row[0]:
                return True
        return False
    
    def checkPassword(self, userName, password): # Checking whether the input password assocciated with the userName is correct 
        rows = self._cur.execute("SELECT * FROM accounts WHERE username = ?", (userName,))
        for row in rows:
            if row[1] == password:
                return True
        return False
    
    def checkLimit(self): # Checking whether the number of accounts has reached the limit of 5
        rows = self._cur.execute("SELECT COUNT(*) FROM accounts")
        for row in rows:
            if row[0] >= 10:
                return False
        return True

    def changeTier(self, userName):
        if self.checkTier(userName):
            self._cur.execute("UPDATE membership SET 'tier' = ? WHERE username = ?", ('standard', userName))
        else:
            self._cur.execute("UPDATE membership SET 'tier' = ? WHERE username = ?", ('plus', userName))
        self.commit()

    def createNewAccount(self):        # Creating new account with username and password
        if not self.checkLimit():
            return "ERROR: All permitted accounts have been created, please come back later"
        userName = input("Please enter your username: ")
        while not self.checkExistingUsername(userName):    # Checking if username already exists
            userName = input("This username is already registered, please enter a different username: ")
        print("Please enter a password that has:")
        print("\t- 8-12 characters")
        print("\t- At least 1 capital letter")
        print("\t- At least 1 digit")
        print("\t- At least a special character")
        print("\t- No space")
        passWord = input("-> ")
        while not self.checkPasswordConvention(passWord):
            print("Please enter a password that has:")
            print("\t- 8-12 characters")
            print("\t- At least 1 capital letter")
            print("\t- At least 1 digit")
            print("\t- At least a special character")
            print("\t- No space")
            passWord = input("-> ")
        firstName = input("Please enter your first name: ")
        lastName = input("Please enter your last name: ")
        university = input("Please enter institution that you're attending: ")
        major = input("Please enter you major: ")
        print("Plus users have access to more features, including:\nBeing able to send messages to everyone in the system")
        print("Your subscription is $10/month and will be automatically renewed at the end of each month")
        tier = input("Do you want to be a Standard user or a Plus user? (standard/plus): ")
        while tier != "standard" and tier != "plus":
            tier = input("Please enter either 'standard' or 'plus': ")
        self.addTier(userName, tier)
        self.addAccount(userName, passWord, firstName, lastName, university, major)    # Calling addAccount func with 4 arguments
        return f"Account {userName} successfully created"
    
    def checkExistingUsername(self, userName):               # Checking Dup when the user creates a new account
        self._cur.execute("SELECT username FROM accounts")
        rows = self._cur.fetchall()
        for row in rows:
            if userName == row[0]:
                return False
        return True

    def checkPasswordConvention(self, password): # Checking whether a password passes the convention
        r1, r2, r3, r4 = False, False, False, True      
        # variables to hold if there is a capital letter (r1), 
        # a digit (r2), a special character (r3), no space (r4).
        if len(password) < 8:      # Checking minimum pass length.
            print("ERROR: Password must be atleast 8 characters!")       
            return False       
        elif len(password) > 12:     # Checking maximum pass length.
            print("ERROR: Password must be at maximum 12 characters!")  
            return False               
        for i in password: 
            if i.isupper():             # there is a capital letter (r1)
                r1 = True            
            if i.isdigit():             # there is a digit (r2)
                r2 = True
            if not((i.isalnum()) or (i==' ')):  # there is a special character and no spaces (r3)
                r3 = True
            if i == ' ': # No space allowed
                r4 = False
        if not (r1 and r2 and r3 and r4):
            print("ERROR: Password does not meet ALL requirements, try again.")
            return False
        return True

    def getLanguage(self):        # returns the language preprences of curr_user
        if self.currentUser == None:
            return self.language
        rows = self._cur.execute("SELECT languagepreference FROM accounts WHERE username = ?", (self.currentUser,))
        res = rows.fetchall()
        return res[0][0]

    def updateGuestControls(self, email, sms, adfeatures):        # updates guest controls for curr user
        self._cur.execute("UPDATE accounts SET emailnoti = ?, sms = ?, adfeatures = ? WHERE username = ?", (email, sms, adfeatures, self.currentUser))
        self.commit()

    def newUsersCreated(self, current_user):        # returns new users created
        rows = self._cur.execute("SELECT firstname, lastname, timecreated FROM accounts WHERE username != ?", (current_user,))
        return rows.fetchall()

    def updateLanguage(self, lang):        # update lang pref of curr_user
        self.language = lang
        self._cur.execute("UPDATE accounts SET languagepreference = ? WHERE username = ?", (lang, self.currentUser))
        self.commit()

    def APIinputHandling(self):
        try:
            with open("studentAccounts.txt", 'r') as f:
                lines = f.readlines()
                data = []
                for line in lines:
                    if line == '=====\n':
                        if self.checkLimit() and self.checkExistingUsername(data[0]):
                            self.addAccount(data[0], data[3], data[1], data[2], 'N/A', 'N/A')
                            self.addTier(data[0], 'standard')
                        data = []
                        continue
                    line = line.strip('\n')
                    data += line.split(' ')
                if self.checkLimit() and data != []:
                    self.addAccount(data[0], data[3], data[1], data[2], 'N/A', 'N/A')
                    self.addTier(data[0], 'standard')
            os.remove('studentAccounts.txt')
        except FileNotFoundError:
            print("studentAccounts.txt not found")


    def APIoutputHandling(self):
        try:
            with open("MyCollege_users.txt", 'w') as f:
                rows = self._cur.execute("SELECT * FROM membership")
                for row in rows:
                    f.write(row[0] + ' ' + row[1] + '\n')
        except:
            print("Unable to write to MyCollege_users.txt")

class ProfilesCreation:
    def __init__(self, dbName):
        self._db = sqlite3.connect(f"./{dbName}.db")
        self._cur = self._db.cursor()
        #creates a table in sql for profiles info
        self._cur.execute("CREATE TABLE IF NOT EXISTS profiles ('profile_user' TEXT NOT NULL,'title' TEXT NOT NULL, 'major' TEXT NOT NULL, 'university' TEXT NOT NULL, 'info' TEXT NOT NULL, 'experience' TEXT NOT NULL, 'education' TEXT NOT NULL)")
        self._db.commit()
        self.APIoutputHandling()
    
    def addProfileUser(self, profile_user):    # Add a new user profile. default to null
        query = "INSERT INTO profiles ('profile_user', 'title','major','university','info','experience','education') VALUES (?,?,?,?,?,?,?)"
        self._cur.execute(query, (profile_user, "NULL", "NULL","NULL", "NULL", "NULL", "NULL"))
        self.commit()

    def addTitle(self, currentUser, title):    # add profile info: title
        self._cur.execute("UPDATE profiles SET title = ? WHERE profile_user = ?", (title, currentUser))
        self.commit()

    def addMajor(self, currentUser, major):     # add profile info: major
        self._cur.execute("UPDATE profiles SET major = ? WHERE profile_user = ?", (major.title(), currentUser))
        self.commit()
    
    def addUni(self, currentUser, university):     # add profile info: University
        self._cur.execute("UPDATE profiles SET university = ? WHERE profile_user = ?", (university.title(), currentUser))
        self.commit()
    
    def addInfo(self, currentUser, info):     # add profile info: information
        self._cur.execute("UPDATE profiles SET info = ? WHERE profile_user = ?", (info, currentUser))
        self.commit()
    
    def addExp(self, currentUser, experience):     # add profile info: experience
        self._cur.execute("UPDATE profiles SET experience = ? WHERE profile_user = ?", (experience, currentUser))
        self.commit()
    
    def addEdu(self, currentUser, education):     # add profile info: education
        self._cur.execute("UPDATE profiles SET education = ? WHERE profile_user = ?", (education, currentUser))
        self.commit()
    
    def experienceInput(self):    # input profile info: experience
        experience = (input("Enter job title: "))
        experience = experience + "\n"  + input("Enter employer: ")
        experience = experience + "\n"  + input("Enter Start Date: ") + input("Enter End Date: ")
        experience = experience + "\n"  + input("Enter location: ")
        experience = experience + "\n"  + input("Enter job description: ")
        return experience

    def educationInput(self):    # input profile info: education
        education = (input("Enter School Name: "))
        education = education + input("Enter degree: ")
        education = education + input("Years attended: ")
        return education
    
    def editProfile(self):    # edit curr_user profile information
        self.viewProfile(accounts.currentUser)
        selection = int(input("\nPlease select a profile edit option:\n1. Edit or enter Title\n2. Edit or enter Major\n3. Edit or enter University\n4. Edit or enter Info\n5. Edit or enter Experience \n6. Edit or enter Education\n7. Save and Exit\n-> "))
        while selection != 7:
            if(selection == 1):
                title = input("Title: ")
                self.addTitle(accounts.currentUser, title)
            
            elif(selection == 2):    
                major = (input("Major: "))
                self.addMajor(accounts.currentUser, major)
                
            elif(selection == 3):    
                university = input("University: ")
                self.addUni(accounts.currentUser, university)
                
            elif(selection == 4):     
                info = input("Info: ")
                self.addInfo(accounts.currentUser, info)
                
            elif(selection == 5):     
                experience = self.experienceInput()
                self.addExp(accounts.currentUser, experience)
            
            elif(selection == 6):     
                education = self.educationInput()
                self.addEdu(accounts.currentUser, education)
            elif(selection == 7): 
                print("Changes have been saved")
            self.APIoutputHandling()
            selection = int(input("\nPlease select a profile edit option:\n1. Edit or enter Title\n2. Edit or enter Major\n3. Edit or enter University\n4. Edit or enter Info\n5. Edit or enter Experience \n6. Edit or enter Education\n7. Save and Exit\n-> "))
            
    
    def checkExistingUsername(self, profile_name):               # Checking Dup when the user creates a new account
        rows = self._cur.execute("SELECT profile_user FROM profiles WHERE profile_user = ?", (profile_name,))
        res = rows.fetchall()
        if res == []:
            return True
        return False
        
    def createProfile(self):        # create a new user profile for curr_user
        if (not profiles.checkExistingUsername(accounts.currentUser)):    # check if curr_user already has a profile
            print("You may only have one profile")
        else:    
            curUser = accounts.currentUser
            self.addProfileUser(curUser) #user creates profile
            self.editProfile()
            print("\n Your profile has been created!")
            self.APIoutputHandling()

    def viewProfile(self, user_name):        # view profile of a user
        rows = self._cur.execute("SELECT * FROM profiles WHERE profile_user = ?", (user_name,))
        for row in rows:
            account = accounts.searchAccount(row[0])
            print(f"User: {account[2]} {account[3]}")
            print(f"Title: {row[1]}")
            print(f"Major: {row[2]}")
            print(f"University: {row[3]}")
            print(f"Info: {row[4]}")
            print(f"Experience: {row[5]}")
            print(f"Education: {row[6]}")
        
    def commit(self):
        self._db.commit()

    def close(self):
        self._cur.close()
        self._db.close()

    def APIoutputHandling(self):
        try:
            with open("MyCollege_profiles.txt", "w") as f:
                rows = self._cur.execute("SELECT title, major, university, info, experience, education FROM profiles")
                for row in rows:
                    f.write(row[0] + "\n")
                    f.write(row[1] + "\n")
                    f.write(row[2] + "\n")
                    f.write(row[3] + "\n")
                    f.write(row[4] + "\n")
                    f.write(row[5] + "\n")
                    f.write("=====\n")
        except:
            print("Error: Unable to write to MyCollege_profiles.txt")

class Friends:
    def __init__(self, dbName):
        self._db = sqlite3.connect(f"./{dbName}.db")
        self._cur = self._db.cursor()
        # Creating a table in SQL file to store account info
        self._cur.execute("CREATE TABLE IF NOT EXISTS friends ('logged_in_user' TEXT NOT NULL, 'friend' TEXT NOT NULL, 'friend_status' TEXT NOT NULL)")
    
    def listOfFriends(self, current_user): # return a list of your connected friends
        rows = self._cur.execute("SELECT friend FROM friends WHERE logged_in_user = ? AND friend_status = 'accepted'", (current_user,))
        return rows.fetchall()

    def listOfPendingFriends(self, current_user): # return a list of people who have sent you the friend request
        rows = self._cur.execute("SELECT logged_in_user FROM friends WHERE friend = ? AND friend_status = 'pending'", (current_user,))
        return rows.fetchall()

    def addFriend(self, current_user, friendsName): # send a friend request
        self._cur.execute("INSERT INTO friends (logged_in_user, friend, friend_status) VALUES (?,?,?)", (current_user, friendsName, "pending"))
        self.commit()

    def acceptFriend(self, current_user, friendsName): # accept a request
        self._cur.execute("UPDATE friends SET friend_status = 'accepted' WHERE logged_in_user = ? AND friend = ?", (friendsName, current_user))
        self._cur.execute("INSERT INTO friends (logged_in_user, friend, friend_status) VALUES (?,?,?)", (current_user, friendsName, "accepted"))
        self.commit()

    def deleteAFriend(self, current_user, friendsName): # delete a friend from your list
        self._cur.execute("DELETE FROM friends WHERE logged_in_user = ? AND friend = ?", (current_user, friendsName))
        self._cur.execute("DELETE FROM friends WHERE logged_in_user = ? AND friend = ?", (friendsName, current_user))
        self.commit()

    def searchForFriends(self, lastName, university, major): # return a list of people that match the search
        rows = self._cur.execute("SELECT * FROM accounts WHERE lastname = ? OR university = ? OR major = ?", (lastName, university, major))
        return rows.fetchall()

    def checkIfConnected(self, current_user, friendsName):        # check if curr_user is friends with another user
        rows = self._cur.execute("SELECT COUNT(*) FROM friends WHERE logged_in_user = ? AND friend = ? AND friend_status = 'accepted'", (current_user, friendsName))
        row = rows.fetchone()
        if row[0] == 0: return False
        return True

    def checkIfPending(self, current_user, friendsName):        # check if friend request from curr_user to another user is pending
        rows = self._cur.execute("SELECT COUNT(*) FROM friends WHERE logged_in_user = ? AND friend = ? AND friend_status = 'pending'", (current_user, friendsName))
        row = rows.fetchone()
        if row[0] == 0: return False
        return True
    
    def commit(self):
        self._db.commit()

    def close(self):
        self._cur.close()
        self._db.close()

def friendRequests():        # print list of friend requests. Allow user to accept or decline requests.
    list_of_friends = friends.listOfPendingFriends(accounts.currentUser)
    if list_of_friends == []:
        return
    for friend in list_of_friends:
        account = accounts.searchAccount(friend[0])
        print(f"{account[2]} {account[3]} wants to connect with you\nEnter 'y' to connect\nEnter 'n' to deny")
        accept = input("-> ")
        if accept == "y":
            friends.acceptFriend(accounts.currentUser, friend[0])
        elif accept == "n":
            friends.deleteAFriend(accounts.currentUser, friend[0])
        # TODO: implement removal from friend reqs. if 'n'??

def friendRequestsList():    #  print list of friend requests. Allow user to accept or decline requests
    list_of_friends = friends.listOfPendingFriends(accounts.currentUser)
    if list_of_friends == []:
        print("You don't have any request")
        return
    flag = True
    while flag:
        list_of_friends = friends.listOfPendingFriends(accounts.currentUser)
        if list_of_friends == []:
            print("You don't have any request")
            break
        i = 0
        for friend in list_of_friends:
            account = accounts.searchAccount(friend[0])
            print(f"{i}: {account[2]} {account[3]}")
            i += 1
        friendidx = int(input("Please enter the friend number you would like to connect: "))
        friends.acceptFriend(accounts.currentUser, list_of_friends[friendidx][0])
        flag = False if input("Do you want to accept more requests? (y/n)") == 'n' else True

def showMyNetwork(): # print current users friend connections
    list_of_friends = friends.listOfFriends(accounts.currentUser)
    if list_of_friends == []:
        return
    flag = True
    while flag:
        list_of_friends == friends.listOfFriends(accounts.currentUser)
        if list_of_friends == []:
            print("You don't have any connection")
            break
        i = 0
        for friend in list_of_friends:
            account = accounts.searchAccount(friend[0])
            if not profiles.checkExistingUsername(friend[0]):
                print(f"{i}: {account[2]} {account[3]} -- User Has Profile")
            else:
                print(f"{i}: {account[2]} {account[3]}")
        
            i += 1
        profileInput = input("Would you like to view a friend's profile? Enter (y) or (n): ")
    
        while(profileInput != 'n'):
            profileFriendUser = int(input("Please input the friend index you'd like to view their profile -> "))
            user = list_of_friends[profileFriendUser][0]
            if(profiles.checkExistingUsername(user)):
                print("User does not have a profile")
                profileInput = input("Would you like to continue to try and view a friend's profile? Enter (y) or (n)")
                if(profileInput == 'y'):
                    continue
                else:
                    profileInput = 'n'    
            else:
                profiles.viewProfile(user)
                profileInput = 'n'
            

        
        if input("Do you want to disconnect with anyone? (y/n)") == 'n':
            break
        friendidx = int(input("Please enter the friend number you would like to disconnect: "))
        friends.deleteAFriend(accounts.currentUser, list_of_friends[friendidx][0])
        flag = False if input("Do you want to continue viewing your connections? (y/n)") == 'n' else True
        
def searchForFriends():    # allows curr user to search for a friend by name, major, and uni
    lastName = input("Please enter your friends' last name: ")
    university = input("Please enter their institution name (USF, UCF, FSU, UF): ")
    major = input("Please enter their major in acronym format (CS, CYS, IT, CPE): ")
    list_of_friends = friends.searchForFriends(lastName, university, major)
    if accounts.currentUser == None:
        for friend in list_of_friends:
            print(f"{friend[2]} {friend[3]}")
        return
    flag = True
    while flag:
        i = 0
        for friend in list_of_friends:
            if friend[0] == accounts.currentUser:
                i += 1
                continue
            if friends.checkIfConnected(accounts.currentUser, friend[0]):
                print(f"{i}: {friend[2]} {friend[3]} -- Friends")
            elif friends.checkIfPending(accounts.currentUser, friend[0]):
                print(f"{i}: {friend[2]} {friend[3]} -- Request Sent")
            else:
                print(f"{i}: {friend[2]} {friend[3]} -- Send a request?")
            i += 1
        friendidx = int(input("Please enter the friend number you would like to connect (-1 to skip): "))
        if friendidx == -1: break
        if not (friends.checkIfConnected(accounts.currentUser, list_of_friends[friendidx][0]) or friends.checkIfPending(accounts.currentUser, list_of_friends[friendidx][0])):
            friendsUsername = list_of_friends[friendidx][0]
            friends.addFriend(accounts.currentUser, friendsUsername)
        flag = False if input("Do you want to stop searching for friends? (y/n)") == 'y' else True

def networking():    # Networking menu
    option = int(input("1. Search for Friends\n2. View Friend Requests\n3. Show my Network\n4. Back\n-> "))
    while True:
        if option == 1:
            searchForFriends()
        elif option == 2:
            friendRequestsList()
        elif option == 3:
            showMyNetwork()
        elif option == 4:
            return
        option = int(input("1. Search for Friends\n2. View Friend Requests\n3. Show my Network\n4. Back\n-> "))

def initialScreen():        # Home screen for InCollege. Leads to all others
    print("\nPlease choose between the options:\n1. Create new account\n2. Sign in to existing account\n3. Useful Links\n4. InCollege Important Links\n5. Quit")
    option = int(input("-> "))
    while option != 5:
        if option == 1:
            print(accounts.createNewAccount())
            # accounts.displayAccount()         # Will display all accounts in system.
        elif option == 2:
            actionsMenu()
        elif option == 3:
            usefulLinks()
        elif option == 4:
            incollegeImportantLinks()
        print("Please choose between the options:\n1. Create new account\n2. Sign in to existing account\n3. Useful Links\n4. InCollege Important Links\n5. Back")
        option = int(input("-> "))
    print("\nNow exiting, have a good day.")

def openingTestimonial():    # prints success story and directs user to advertisement video
    print("Hi College Student!\nIm Rowena, and when I was a college sophmore, InCollege got me a job at Google, now only 4 months later, I'm the CEO!\nWithout InCollege, I could have never done it!\n")
    option = int(input("1. Check out how YOU will become a FANG CEO with InCollege!\n2. Login or SignUp Screen\n3. Search for friends\n4. Useful Links\n5. InCollege Important Links\n6. Quit\n-> "))
    while True:
        if option == 1:
            print("\n--video is now playing--\n")
        elif option == 2:
            initialScreen()
        elif option == 3:
            searchForFriends()
        elif option == 4:
            usefulLinks()
        elif option == 5:
            incollegeImportantLinks()
        elif option == 6:
            quit("\n--Leaving InCollege--\n")
        print("Hi College Student!\nIm Rowena, and when I was a college sophmore, InCollege got me a job at Google, now only 4 months later, I'm the CEO!\nWithout InCollege, I could have never done it!\n")
        option = int(input("1. Check out how YOU will become a FANG CEO with InCollege!\n2. Login or SignUp Screen\n3. Search for friends\n4. Useful Links\n5. InCollege Important Links\n6. Quit\n-> "))

def signIn():            # function to sign in user.
    userName = input("\nPlease type in your Username: ")
    while not accounts.checkUsername(userName):
        userName = input("Username cannot be found, please enter the correct username: ")
    password = input("Please type in your Password: ")
    while not accounts.checkPassword(userName, password):
        password = input(f"\nERROR: Incorrect password\nEnter the correct password for {userName}: ")
    accounts.currentUser = userName
    friendRequests()
    if messages.haveNewMessages(accounts.currentUser):
        print("You have messages waiting for you!")
        option = input("View your messages (y/n): ")
        if option == 'y':
            messageMenu()
    if jobapps.haveNotApplied(accounts.currentUser):
        print("You haven't applied to any jobs in 7 days!")
        print("Remember - you're going to want to have a job when you graduate. Make sure that you start to apply for jobs today!")
    if profiles.checkExistingUsername(accounts.currentUser):
        print("You haven't created a profile yet! Please create one now.")
    newJobPostings()
    newUsersJoining()
    deletedJobNoti(accounts.currentUser)
    signInHistory.addSignIn(accounts.currentUser)

def newJobPostings():
    newJobs = jobs.newJobPostings(accounts.currentUser)
    for newJob in newJobs:
        date = newJob[1].split('-')
        postdate = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(date[3]), int(date[4]), int(date[5]))
        lastSignIn = signInHistory.lastSignIn(accounts.currentUser)
        if datetime.datetime.now() > postdate and (not lastSignIn or postdate > lastSignIn):
            print(f"A new job {newJob[0]} has been posted!")

def newUsersJoining():
    newUsers = accounts.newUsersCreated(accounts.currentUser)
    for newUser in newUsers:
        date = newUser[2].split('-')
        joindate = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(date[3]), int(date[4]), int(date[5]))
        lastSignIn = signInHistory.lastSignIn(accounts.currentUser)
        if datetime.datetime.now() > joindate and lastSignIn and joindate > lastSignIn:
            print(f"A new user {newUser[0]} {newUser[1]} has joined InCollege!")

def actionsMenu():        # Menu after logging in. Sub to initialScreen()
    signIn()
    selection = int(input("\nPlease select a menu option:\n1. Jobs\n2. Find a friend\n3. Message Menu\n4. Learn a new skill\n5. Useful Links\n6. InCollege Important Links\n7. Profile Management\n8. Sign Out\n-> "))
    while True:
        if selection == 1:
            createOrFindJobMenu()
        elif selection == 2:
            networking()
        elif selection == 3:
            messageMenu()
        elif selection == 4:
            skillsMenu()
        elif selection == 5:
            usefulLinks()
        elif selection == 6:
            incollegeImportantLinks()
        elif selection == 7:
            createOrViewProfileMenu()
        elif selection == 8:
            print("\nSigning you out...\n")
            accounts.currentUser = None
            return
        selection = int(input("\nPlease select a menu option:\n1. Jobs\n2. Find a friend\n3. Message Menu\n4. Learn a new skill\n5. Useful Links\n6. InCollege Important Links\n7. Profile Management\n8. Sign Out\n-> "))
        
def usefulLinks():    # Menu for incollege
    print("\nPlease choose between the options:\n1. General\n2. Browse InCollege\n3. Business Solutions\n4. Directories\n5. Back")
    option = int(input("-> "))
    while True:
        if option == 1: 
            generalMenu()
        elif option == 2: 
            print("\nUnder construction")
        elif option == 3: 
            print("\nUnder construction")
        elif option == 4: 
            print("\nUnder construction")
        elif option == 5:
            return 
        print("\nPlease choose between the options:\n1. General\n2. Browse InCollege\n3. Business Solutions\n4. Directories\n5. Back")
        option = int(input("-> "))

def generalMenu():          # Menu to display General Menu's available options/selections 
    selection = int(input("\nPlease select a menu option:\n1. Sign Up\n2. Help Center\n3. About\n4. Press\n5. Blog\n6. Careers\n7. Developers\n8. Back\n-> "))
    while True:
        if selection == 1:      # Sign Up
            global accounts
            if accounts.currentUser != None:
                print("You're already signed in, please sign out to create a new account!")
            else:
                accounts.createNewAccount()
        elif selection == 2:      # Help Center 
            print("\nWe're here to help!")
        elif selection == 3:      # About
            print("\nIn College: Welcome to In College, the world's largest college student network with many users in many countries and territories worldwide")
        elif selection == 4:      # Press
            print("\nIn College Pressroom: Stay on top of the latest news, updates, and reports")
        elif selection == 5:      # Blog
            print("\nUnder construction")
        elif selection == 6:      # Careers
            print("\nUnder construction")
        elif selection == 7:      # Developers 
            print("\nUnder construction")
        elif selection == 8:
            return
        selection = int(input("\nPlease select a menu option:\n1. Sign Up\n2. Help Center\n3. About\n4. Press\n5. Blog\n6. Careers\n7. Developers\n8. Back\n-> "))
        
def incollegeImportantLinks():          # Menu to display InCollege Important Links
    link = int(input("\nPlease select a menu option:\n1. Copyright Notice\n2. About\n3. Accessibility\n4. User Agreement\n5. Privacy Policy\n6. Cookie Policy\n7. Copyright Policy\n8. Brand Policy\n9. Languages\n10. Back\n-> "))
    while True:
        if link == 1:       # Copyright Notice 
            print("\n©2022 InCollege app, All right reserved")
        elif link == 2:       # About
            print("\nInCollege is an app focused on building stronger student connections. Our vision is to grow the college students experience")
        elif link == 3:       # Accessibility
            print("\nInCollege is designed to be accessible to students across a broad spectrum of physical and mental capability. Please contact our support staff if you encounter a non-incluse accessibility obstacle on InCollege.")
        elif link == 4:       # User Agreement
            print("\nBy utilizing InCollege you are agreeing that any and all data you create is owned by InCollege. You may request your data be removed from the InCollege database.")
        elif link == 5:       # Privacy Policy
            print("Privacy Policy:")
            guestcontrols = int(input("Enter 1 to access Guest Controls, 2 to ignore\n->"))
            if guestcontrols == 1:
                guestControls()
        elif link == 6:       # Cookie Policy
            print("\nWe use cookies to get to know you better. With cookies we can deliver a more personalized experience on InCollege.")
        elif link == 7:       # Copyright Policy
            print("\nInCollege is not responsible for the content of posts generated by InCollege users. All InCollege branding is property of InCollege.")
        elif link == 8:       # Brand Policy 
            print("\nInCollege is here to serve college students in their paths to bright futures. We strive to ensure every action fits that goal.")
        elif link == 9:       # Languages 
            updateLanguage()
        elif link == 10:
            return
        link = int(input("\nPlease select a menu option:\n1. Copyright Notice\n2. About\n3. Accessibility\n4. User Agreement\n5. Privachy Policy\n6. Cookie Policy\n7. Copyright Policy\n8. Brand Policy\n9. Languages\n10. Back\n-> "))

# def makeProfile(self):
#     Profiles.createProfile(self)
def createOrViewProfileMenu():
    option = int(input("\nPlease make a profile related selection:\n1. View Profiles\n2. Create a Profile\n3. Edit profile \n4. Back\n-> "))
    while option != 4:
        if option == 1:
            profiles.viewProfile(accounts.currentUser)
            createOrViewProfileMenu()  
        elif option == 2:
            profiles.createProfile()
            createOrViewProfileMenu()
        elif option == 3:
            profiles.editProfile()
            createOrViewProfileMenu()
        option = int(input("\nPlease make a profile related selection:\n1. View Profiles\n2. Create a Profile\n3. Edit profile \n4. Back\n-> "))

def createOrFindJobMenu():        # Menu to search job listings or create a new job. sub to actionsMenu()
    while True:
        if jobapps.countJobApps(accounts.currentUser) == 0:
            print("\nYou have not applied to any jobs yet!")
        elif jobapps.countJobApps(accounts.currentUser) == 1:
            print("\nYou have applied for 1 job!")
        else:
            print(f"You have applied for {jobapps.countJobApps(accounts.currentUser)} jobs!")
        deletedJobNoti(accounts.currentUser)
        option = int(input("\nPlease make a job related selection:\n1. Search posted jobs\n2. Jobs Management\n3. Back\n-> "))
        if option == 1:
            while True:
                preference = int(input("1. View all jobs\n2. View applied jobs\n3. View not applied jobs\n4. View saved jobs\n5. Back\n-> "))
                if preference == 1:
                    viewAllJobs(accounts.currentUser)
                elif preference == 2:
                    viewAppliedJobs(accounts.currentUser)
                elif preference == 3:
                    viewNotAppliedJobs(accounts.currentUser)
                elif preference == 4:
                    viewSavedJobs(accounts.currentUser)
                else: break
        elif option == 2:
            while True:
                preference = int(input("1. View/Delete my job postings\n2. Create a job listing\n3. Back\n-> "))
                if preference == 1:
                    myJobPostings(accounts.currentUser)
                elif preference == 2:
                    jobs.createAJob(accounts.currentUser)
                else: break
        elif option == 3:
            break

def myJobPostings(current_user):    # check curr_users job postings
    while True:
        jobCounter = 1
        jobPostings = jobs.myJobPostings(current_user)
        print("Job Lists")
        for row in jobPostings:
            print(f"{jobCounter}. {row[1]}")
            jobCounter+= 1
        print("Options: ")
        option = int(input("1. View Details\n2. Delete Jobs\n3. Back\n-> "))
        if option == 1:
            job = int(input("Please choose the job number you would like to view\n-> "))
            jobs.displayAJob(jobPostings[job-1][0])
        elif option == 2:
            job = int(input("Please choose the job number you would like to delete\n-> "))
            jobs.deleteAJob(jobPostings[job-1][0])
        elif option == 3:
            break

def deletedJobNoti(current_user):       # shows notification that a job that curr_user applied to has been deleted
    deletedjobs = jobapps.deletedJobNoti(current_user)
    for job in deletedjobs:
        print(f"Job {job} has been deleted")

def viewJobDetails(current_user, job_ID):    # shows more information on job and allows application to job
    jobs.displayAJob(job_ID)
    while True:
        option = int(input("1. Apply for Job\n2. Save Job for later\n3. Back\n-> "))
        if option == 1:
            if jobapps.checkIfApplied(current_user, job_ID):
                print("You have already applied for this job")
            elif jobs.selfApplyCheck(current_user, job_ID):
                print("You cannot apply for a job that you posted")
            else:
                jobapps.createApplication(current_user, job_ID)
                jobapps.changeSavedToApplied(current_user, job_ID)
                monGrad = int(input("What month did you graduate or expected to graduate? (numerical format ex: 01 - 12)\n-> "))
                dayGrad = int(input("What day did you graduate or expected to graduate? (numerical format ex: 01 - 31)\n-> "))
                yearGrad = int(input("What year did you graduate or expected to graduate?\n-> "))
                monStart = int(input("What month can you start working with us? (numerical format ex: 01 - 12)\n-> "))
                dayStart = int(input("What day can you start working with us? (numerical format ex: 01 - 31)\n-> "))
                yearStart = int(input("What year can you start working with us? \n-> "))
                details = input("Please tell us why you think you would be a good fit for this job?\n-> ")
                jobapps.updateApplicationInfo(current_user, job_ID, monGrad, dayGrad, yearGrad, monStart, dayStart, yearStart, details)
            break
        elif option == 2:
            if jobapps.checkIfSaved(current_user, job_ID):
                print("You have already saved this job")
            elif jobs.selfApplyCheck(current_user, job_ID):
                print("You cannot save a job that you posted")
            else:
                jobapps.saveAJob(current_user, job_ID)
                print("Job saved")
            break
        elif option == 3:
            break

def viewAllJobs(current_user):    # Displays all jobs, and wheter curr_user applied or saved them
    while True:
        jobCounter = 1
        jobPostings = jobs.displayAllJobs()
        for row in jobPostings:
            if jobapps.checkIfApplied(current_user, row[0]):
                print(f"{jobCounter}. {row[1]} --- Applied")
            elif jobapps.checkIfSaved(current_user, row[0]):
                print(f"{jobCounter}. {row[1]} --- Saved")
            else:
                print(f"{jobCounter}. {row[1]}")
            jobCounter+= 1
        view = int(input("Please choose the job number you would like to view more details about\nPlease choose 0 to go back\n-> "))
        if view == 0: break
        viewJobDetails(current_user, jobPostings[view-1][0])
        

def viewAppliedJobs(current_user):    # shows applied jobs 
    while True:
        jobCounter = 1
        jobPostings = jobs.displayAppliedJobs(current_user)
        for row in jobPostings:
            print(f"{jobCounter}. {row[1]}")
            jobCounter+= 1
        view = int(input("Please choose the job number you would like to view more details about\nPlease choose 0 to go back\n-> "))
        if view == 0: break
        jobs.displayAJob(jobPostings[view-1][0])

def viewNotAppliedJobs(current_user):    # shows jobs not applied for
    while True:
        jobCounter = 1
        jobPostings = jobs.displayAllJobs()
        for row in jobPostings:
            if not jobapps.checkIfApplied(current_user, row[0]):
                print(f"{jobCounter}. {row[1]}")
            jobCounter+= 1
        view = int(input("Please choose the job number you would like to view more details about\nPlease choose 0 to go back\n-> "))
        if view == 0: break
        viewJobDetails(current_user, jobPostings[view-1][0])

def viewSavedJobs(current_user):    # shows saved jobs
    while True:
        jobCounter = 1
        jobPostings = jobs.displaySavedJobs(current_user)
        for row in jobPostings:
            print(f"{jobCounter}. {row[1]}")
            jobCounter+= 1
        print("\nOptions: ")
        option = int(input("1. View job details\n2. Unsave jobs\n3. Back\n-> "))
        if option == 1:
            view = int(input("Please choose the job number you would like to view more details about\nPlease choose 0 to go back\n-> "))
            viewJobDetails(current_user, jobPostings[view-1][0])
        elif option == 2:
            unsave = int(input("Please choose the job number you want to unsave\nChoose 0 if you don't want to unsave any job\n-> "))
            jobapps.unsaveAJob(current_user, jobPostings[unsave-1][0])
        else:
            break

def findAFriend():       # Finding a friend on InCollege via first and lastname search
    print("\nFind your friends on InCollege!")
    firstName = input("First Name: ")
    lastName = input("Last Name: ")
    print(f"Searching for {firstName} {lastName}")
    if accounts.searchForName(firstName, lastName):
        print("\nThey are a part of the InCollege system")
    else:
        print("\nThey are not yet a part of the InCollege system yet")
        findAFriend()
    
def skillsMenu():        # Menu to display skills to learn. Sub actionsMenu()
    selection = int(input("Please select one of those skill:\n1. Python\n2. C++\n3. HTML\n4. JavaScript\n5. CSS\n6. Back\n->"))
    while selection != 6:
        print("\n--Under Construction--")
        selection = int(input("Please select one of those skill:\n1. Python\n2. C++\n3. HTML\n4. JavaScript\n5. CSS\n6. Back\n->"))

def guestControls():    # allows alteration of account controls 
    if accounts.currentUser is None:
        print("Please Sign in to your account to see the options")
        return
    _,_,_,_,_,_,email,sms,adfeatures,_ = accounts.searchAccount(accounts.currentUser)
    if email == "On":
        email_input = int(input("Your InCollege Email Notifications are allowed, please click 1 to turn it off, click 2 to ignore\n->"))
        if email_input == 1:
            email = "Off"
    elif email == "Off":
        email_input = int(input("Your InCollege Email Notifications are not allowed, please click 1 to turn it on, click 2 to ignore\n->"))
        if email_input == 1:
            email = "On"
    if sms == "On":
        sms_input = int(input("Your SMS Notifications are allowed, please click 1 to turn it off, click 2 to ignore\n->"))
        if sms_input == 1:
            sms = "Off"
    elif sms == "Off":
        sms_input = int(input("Your SMS Notifications are not allowed, please click 1 to turn it on, click 2 to ignore\n->"))
        if sms_input == 1:
            sms = "On"
    if adfeatures == "On":
        ad_input = int(input("Your Targeted Advertising Features are allowed, please click 1 to turn it off, click 2 to ignore\n->"))
        if ad_input == 1:
            adfeatures = "Off"
    elif adfeatures == "Off":
        ad_input = int(input("Your Targeted Advertising Features are not allowed, please click 1 to turn it on, click 2 to ignore\n->"))
        if ad_input == 1:
            adfeatures = "On"
    accounts.updateGuestControls(email, sms, adfeatures)

def updateLanguage():    # update the language in account
    if accounts.currentUser is None:
        language = accounts.language
        if language == "English":
            language_input = int(input("Your language is set to English, enter 1 to change to Spanish, enter 2 to ignore\n->"))
            if language_input == 1:
                print("Your language is set Spanish")
                language = "Spanish"
        elif language == "Spanish":
            language_input = int(input("Your language is set to Spanish, enter 1 to change to English, enter 2 to ignore\n->"))
            if language_input == 1:
                print("Your language is set English")
                language = "English"
        accounts.language = language
        return
    language = accounts.getLanguage()
    if language == "English":
        language_input = int(input("Your language is set to English, enter 1 to change to Spanish, enter 2 to ignore\n->"))
        if language_input == 1:
            print("Your language is set Spanish")
            language = "Spanish"
    elif language == "Spanish":
        language_input = int(input("Your language is set to Spanish, enter 1 to change to English, enter 2 to ignore\n->"))
        if language_input == 1:
            print("Your language is set English")
            language = "English"
    accounts.updateLanguage(language)
def searchAndMessage():
    list_of_users = accounts.listOfUsers(accounts.currentUser)
    if list_of_users == []:
        print("There is no other user in the system")
        return
    i = 0
    for user in list_of_users:
        print(f"{i}: {user[1]} {user[2]}")
        i += 1
    useridx = int(input("Please enter the user number you would like to message: "))
    if useridx >= len(list_of_users):
        print("Invalid user number")
        return
    receiver = list_of_users[useridx][0]
    if not accounts.checkTier(accounts.currentUser):
        if not friends.checkIfConnected(accounts.currentUser, receiver) and not messages.haveCommunication(accounts.currentUser, receiver):
            print("You cannot messages users that are not in your network if you are a Standard user")
            return
    flag = True
    while flag:
        print("Enter the message you would like to send")
        message = input("-> ")
        if message == "":
            print("Message cannot be empty")
            flag = False if input("Do you want to continue sending a message? (y/n)") == 'n' else True
        else:
            flag = False
    messages.addMessage(message, accounts.currentUser, receiver)
    print("Message sent")

def viewInbox():
    list_of_senders = messages.listOfSenders(accounts.currentUser)
    if list_of_senders == []:
        print("You don't have any message")
        return
    i = 0
    for sender in list_of_senders:
        if messages.haveUnreadMessages(sender[0], accounts.currentUser):
            print(f"{i}: {sender[1]} {sender[2]} has sent you a message")
        else:
            print(f"{i}: {sender[1]} {sender[2]}")
        i += 1
    senderidx = int(input("Please enter the sender number you would like to view: "))
    if senderidx >= len(list_of_senders):
        print("Invalid sender number")
        return
    sender = list_of_senders[senderidx][0]
    rows = messages.viewMessages(sender, accounts.currentUser)
    for row in rows:
        account = accounts.searchAccount(row[2])
        print(f"{account[2]} {account[3]}: {row[1]}")
        if row[3] == accounts.currentUser:
            messages.markAsRead(row[0])
    delete = input("Do you want to delete this conversation? (y/n)")
    if delete == 'y':
        for row in rows:
            messages.deleteMessage(row[0])
    while True:
        print("Enter the message you would like to send")
        message = input("-> ")
        if message == "":
            print("Message cannot be empty")
            if input("Do you want to continue sending a message? (y/n)") == 'n':
                return
        else:
            break
    messages.addMessage(message, accounts.currentUser, sender)
    print("Message sent")

def messageMenu():
    while True:
        print("1. Search and message")
        print("2. View inbox")
        print("3. Back")
        choice = input("-> ")
        if choice == "1":
            searchAndMessage()
        elif choice == "2":
            viewInbox()
        elif choice == "3":
            break
        else:
            print("Invalid choice")


def main():    # Main function, start of program
    global friends
    global accounts
    global jobs
    global profiles
    global jobapps
    global messages
    global signInHistory
    signInHistory = SignInHistory("incollege")
    messages = Message("incollege")
    profiles = ProfilesCreation("incollege")
    jobs = JobPosting("incollege")
    jobapps = JobApplication("incollege")
    accounts = AccountCreation("incollege")
    friends = Friends("incollege")
    openingTestimonial()
    friends.close()
    jobs.close()
    accounts.close()
    

if __name__ =="__main__":
    main()
