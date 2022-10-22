from genericpath import sameopenfile
import profile
import sqlite3               # database used to store account & job information
import string
from tokenize import String

class JobPosting:            # class for creating job listings
    def __init__(self, dbName):
        self._db = sqlite3.connect(f"./{dbName}.db")
        self._cur = self._db.cursor()
        # Creating a table in SQL file to store account info
        self._cur.execute("CREATE TABLE IF NOT EXISTS jobs ('title' TEXT NOT NULL, 'description' TEXT NOT NULL, 'employer' TEXT NOT NULL, 'location' TEXT NOT NULL, 'salary' FLOAT NOT NULL, 'poster' TEXT NOT NULL)")
        
    def checkLimit(self): # Checking whether the number of jobs has reached the limit of 5
        rows = self._cur.execute("SELECT COUNT(*) FROM jobs")
        for row in rows:
            if row[0] >= 5:
                return False
        return True
    
    def addJob(self, title, description, employer, location, salary, poster):        # Add job to SQL file
        query = "INSERT INTO jobs ('title', 'description', 'employer', 'location', 'salary', 'poster') VALUES (?, ?, ?, ?, ?, ?)"
        self._cur.execute(query, (title, description, employer, location, salary, poster))
        self.commit()

    def createAJob(self):        # Function to create job posting
        if not self.checkLimit():
            return "ERROR: All permitted jobs have been created, please come back later"
        print("\nPost your job")
        title = input("Title: ")
        description = input("Description: ")
        employer = input("Employer: ")
        location = input("Location: ")
        salary = float(input("Salary: $"))
        self.addJob(title, description, employer, location, salary, accounts.currentUser)
        return "\n--Job has been posted--"

    def displayAllJobs(self):
        rows = self._cur.execute("SELECT * FROM jobs")
        jobCounter = 1
        for row in rows:
            print(f"\nJob {jobCounter}:")
            print(f"Title: {row[0]}")
            print(f"Description: {row[1]}")
            print(f"Employer: {row[2]}")
            print(f"Location: {row[3]}")
            print(f"Salary: ${row[4]:,.2f}")
            jobCounter+= 1
            
    def commit(self):
        self._db.commit()

    def close(self):
        self._cur.close()
        self._db.close()
            
class AccountCreation:        # class for creating accounts
    def __init__(self, dbName):
        self._db = sqlite3.connect(f"./{dbName}.db")
        self._cur = self._db.cursor()
        # Creating a table in SQL file to store account info
        self._cur.execute("CREATE TABLE IF NOT EXISTS accounts ('username' TEXT NOT NULL UNIQUE, 'password' TEXT NOT NULL, 'firstname' TEXT NOT NULL, 'lastname' TEXT NOT NULL, 'university' TEXT NOT NULL, 'major' TEXT NOT NULL, 'emailnoti' TEXT NOT NULL, 'sms' TEXT NOT NULL, 'adfeatures' TEXT NOT NULL, 'languagepreference' TEXT NOT NULL)")
        self.currentUser = None
        self.language = "English"

    # CRUD 
    def commit(self):
        self._db.commit()

    def close(self):
        self._cur.close()
        self._db.close()

    def addAccount(self, userName, passWord, firstName, lastName, university, major): # Create new record in the Database after the input is verified
        query = "INSERT INTO accounts ('username', 'password', 'firstname', 'lastname', 'university', 'major', 'emailnoti', 'sms', 'adfeatures', 'languagepreference') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        self._cur.execute(query, (userName, passWord, firstName, lastName, university, major, "On", "On", "On", "English"))
        self.commit()

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

    def getLanguage(self):
        if self.currentUser == None:
            return self.language
        rows = self._cur.execute("SELECT languagepreference FROM accounts WHERE username = ?", (self.currentUser,))
        res = rows.fetchall()
        return res[0][0]

    def updateGuestControls(self, email, sms, adfeatures):
        self._cur.execute("UPDATE accounts SET emailnoti = ?, sms = ?, adfeatures = ? WHERE username = ?", (email, sms, adfeatures, self.currentUser))
        self.commit()

    def updateLanguage(self, lang):
        self.language = lang
        self._cur.execute("UPDATE accounts SET languagepreference = ? WHERE username = ?", (lang, self.currentUser))
        self.commit()

class Profiles:
    def __init__(self, dbName):
        self.db = sqlite3.connect(f"./{dbName}.db")
        self._cur = self.db.cursor()
        #creates a table in sql for profiles info
        self._cur.execute("Create IF NOT EXISTS profiles ('profile_user' TEXT NOT NULL,'title' TEXT NOT NULL, 'major' TEXT NOT NULL, 'university' TEXT NOT NULL, 'info' TEXT NOT NULL, 'experience' TEXT NOT NULL, 'education' TEXT NOT NULL)") 
    
    def addProfileUser(self, profile_user):
        query = "INSERT INTO profiles ('profile_user) VALUES (?)"
        self._cur.execute(query, (profile_user))
        self.commit()

    def addTitle(self,title):
        query = "INSERT INTO profiles ('title') VALUES (?)"
        self._cur.execute(query, (title))
        self.commit()
    
    def addMajor(self,major):
        query = "INSERT INTO profiles ('major') VALUES (?)"
        self.commit()
    
    def addUni(self, university):
        query = "INSERT INTO profiles ('university') VALUES (?)"
        self._cur.execute(query, (university))
        self.commit()
    
    def addInfo(self, info):
        query = "INSERT INTO profiles ('info') VALUES (?)"
        self._cur.execute(query, (info))
        self.commit()
    
    def addExp(self, experience):
        query = "INSERT INTO profiles ('experience') VALUES (?)"
        self._cur.execute(query, experience ())
        self.commit()
    
    def addEdu(self, education):
        query = "INSERT INTO profiles ('experience') VALUES (?)"
        self._cur.execute(query, education ())
        self.commit()
    
    
    def experienceInput(self):
        experience = str(input("Enter job title: "))
        experience = experience + "\n"  + input("Enter employer: ")
        experience = experience + "\n"  + input("Enter Start Date: ") + input("Enter end date")
        experience = experience + "\n"  + input("Enter location: ")
        experience = experience + "\n"  + input("Enter job description: ")
        return experience

    def educationInput(self):
        education = str(input("Enter School Name: "))
        education = education + input("Enter degree: ")
        education = education + input("Years attended: ")
        return education
    

        
    def createProfile(self):          #  martin - USF - - -   // Insert [Current user and Major == Null ]
                                      #  aaron - - - - - - 
                                      #  shaunak - - -  - //Insert[]

                                      #  
        userinput = 1
        while(userinput != 0):                   
            print("\n Update your profile")
            userinput = input("Would you like to continue: 1(y) 0(n)")
            self.addProfileUser(accounts.currentUser())
            
            userinput = input("Would you like to continue: 1(y) 0(n)")
            title = input("Title: ")
            self.addTitle(title)
            
            userinput = input("Would you like to continue: 1(y) 0(n)")
            major = string.capwords(input("Major: "))
            self.addMajor(major)
            
            userinput = input("Would you like to continue: 1(y) 0(n)")
            university = string.capwords(input("University: "))
            self.addUni(university)
            
            userinput = input("Would you like to continue: 1(y) 0(n)")
            info = input("Info: ")
            self.addInfo(info)
            
            userinput = input("Would you like to continue: 1(y) 0(n)")
            experience = Profiles.experienceInput()
            self.addExp(experience)
            
            userinput = input("Would you like to continue: 1(y) 0(n)")
            education = Profiles.educationInput()
            self.addEdu(education)


    
    
    def commit(self):
        self._db.commit()

    def close(self):
        self._cur.close()
        self._db.close()


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

    def checkIfConnected(self, current_user, friendsName):
        rows = self._cur.execute("SELECT COUNT(*) FROM friends WHERE logged_in_user = ? AND friend = ? AND friend_status = 'accepted'", (current_user, friendsName))
        row = rows.fetchone()
        if row[0] == 0: return False
        return True

    def checkIfPending(self, current_user, friendsName):
        rows = self._cur.execute("SELECT COUNT(*) FROM friends WHERE logged_in_user = ? AND friend = ? AND friend_status = 'pending'", (current_user, friendsName))
        row = rows.fetchone()
        if row[0] == 0: return False
        return True

    def commit(self):
        self._db.commit()

    def close(self):
        self._cur.close()
        self._db.close()

def friendRequests():
    list_of_friends = friends.listOfPendingFriends(accounts.currentUser)
    if list_of_friends == []:
        return
    for friend in list_of_friends:
        account = accounts.searchAccount(friend[0])
        print(f"{account[2]} {account[3]} wants to connect with you\nEnter 'y' to connect\nEnter 'n' to deny")
        accept = input("-> ")
        if accept == "y":
            friends.acceptFriend(accounts.currentUser, friend[0])

def friendRequestsList():
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

def showMyNetwork():
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
            print(f"{i}: {account[2]} {account[3]}")
            i += 1
        if input("Do you want to disconnect with anyone? (y/n)") == 'n':
            break
        friendidx = int(input("Please enter the friend number you would like to disconnect: "))
        friends.deleteAFriend(accounts.currentUser, list_of_friends[friendidx][0])
        flag = False if input("Do you want to continue viewing your connections? (y/n)") == 'n' else True
        
def searchForFriends():
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
        friendidx = int(input("Please enter the friend number you would like to connect: "))
        if not (friends.checkIfConnected(accounts.currentUser, list_of_friends[friendidx][0]) or friends.checkIfPending(accounts.currentUser, list_of_friends[friendidx][0])):
            friendsUsername = list_of_friends[friendidx][0]
            friends.addFriend(accounts.currentUser, friendsUsername)
        flag = False if input("Do you want to stop searching for friends? (y/n)") == 'y' else True

def networking():
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
            signIn()
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
    actionsMenu()

def actionsMenu():        # Menu after logging in. Sub to initialScreen()
    selection = int(input("\nPlease select a menu option:\n1. Find or Post a job\n2. Find a friend\n3. Learn a new skill\n4. Useful Links\n5. InCollege Important Links\n6. Sign Out\n-> "))
    while True:
        if selection == 1:
            createOrFindJobMenu()
        elif selection == 2:
            networking()
        elif selection == 3:
            skillsMenu()
        elif selection == 4:
            usefulLinks()
        elif selection == 5:
            incollegeImportantLinks()
        elif selection == 6:
            print("\nSigning you out...\n")
            accounts.currentUser = None
            return
        selection = int(input("\nPlease select a menu option:\n1. Find or Post a job\n2. Find a friend\n3. Learn a new skill\n4. Useful Links\n5. InCollege Important Links\n6. Sign Out\n-> "))
        

def usefulLinks():
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

def createOrFindJobMenu():        # Menu to search job listings or create a new job. sub to actionsMenu()
    option = int(input("\nPlease make a job related selection:\n1. Search posted jobs\n2. Create a job listing\n3. Back\n-> "))
    if option == 1:
        print("\nDisplaying all job:")
        jobs.displayAllJobs()
        createOrFindJobMenu()
    elif option == 2:
        print(jobs.createAJob())
        createOrFindJobMenu()
    else:
        actionsMenu()
    
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
    print("Please select one of those skill:\n1. Python\n2. C++\n3. HTML\n4. JavaScript\n5. CSS\n6. Back")
    selection = int(input("-> "))
    if selection == 6:
        actionsMenu()
    else:
        print("\n--Under Construction--")
        skillsMenu()

def guestControls():
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

def updateLanguage():
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


def main():
    global friends
    global accounts
    global jobs
    jobs = JobPosting("incollege")
    accounts = AccountCreation("incollege")
    friends = Friends("incollege")
    openingTestimonial()
    friends.close()
    jobs.close()
    accounts.close()

if __name__ =="__main__":
    main()
