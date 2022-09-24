import sqlite3

class AccountCreation:
    def __init__(self, dbName):
        self._db = sqlite3.connect(f"./{dbName}.db")
        self._cur = self._db.cursor()
        self._cur.execute("CREATE TABLE IF NOT EXISTS accounts "
                          "('username' TEXT NOT NULL UNIQUE, 'password' TEXT NOT NULL)")
        self.numAccounts = 0
    
    # CRUD
    def commit(self):
        self._db.commit()

    def close(self):
        self._cur.close()
        self._db.close()

    def addAccount(self, userName, passWord):
        self.numAccounts += 1
        query = "INSERT INTO accounts ('username', 'password') VALUES (?, ?)"
        self._cur.execute(query, (userName, passWord))
        self.commit()

    def displayAccount(self):
        self._cur.execute("SELECT * FROM accounts")
        rows = self._cur.fetchall()
        for row in rows:
            print(f"Account: {row[0]}\nPassword: {row[1]}")

    def deleteAccount(self):
        userName = input("Enter the userName you want to delete: ")
        query = "DELETE FROM accounts WHERE username == ?"
        self._cur.execute(query, (userName,))
        self.commit()

    # Verifying input
    def checkUsername(self, userName):
        rows = self._cur.execute("SELECT * FROM accounts")
        for row in rows:
            if userName == row[0]:
                return True
        return False

    def checkPassword(self, userName, password):
        rows = self._cur.execute("SELECT * FROM accounts WHERE username == ?", (userName,))
        for row in rows:
            if row[1] == password:
                return True
        return False

    def checkLimit(self):
        return False if self.numAccounts == 5 else True

    def createNewAccount(self):
        if not self.checkLimit():
            return "ERROR: All permitted accounts have been created, please come back later"
        userName = input("Please enter your username: ")
        while not self.checkExistingUsername(userName):
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
        self.addAccount(userName, passWord)
        return f"Account {userName} successfully created"

    def checkExistingUsername(self, userName):
        self._cur.execute("SELECT username FROM accounts")
        rows = self._cur.fetchall()
        for row in rows:
            if userName == row[0]:
                return False
        return True

    def checkPasswordConvention(self, password):
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

def initialScreen(table):
    print("Please choose between the options:\n1. Create new account\n2. Sign in to existing account\n3. Quit")
    option = int(input("-> "))
    while option != 3:
        if option == 1:
            print(table.createNewAccount())
            table.displayAccount()
        if option == 2:
            signIn(table)
        print("Please choose between the options:\n1. Create new account\n2. Sign in to existing account\n3. Quit")
        option = int(input("-> "))

def signIn(table):
    userName = input("Please type in your Username: ")
    while not table.checkUsername(userName):
        userName = input("Username cannot be found, please enter the correct username: ")
    password = input("Please type in your Password: ")
    while not table.checkPassword(userName, password):
        password = input(f"Incorrect password, please enter the correct password for {userName}: ")
    actionsMenu()

def actionsMenu():
    selection = int(input("\nPlease Select a menu option:\n1. Find a job\n2. Find a friend\n3. Learn a new skill\n>"))
    if selection == 1 or selection == 2:
        print("Under Construction")
        actionsMenu()
    elif selection == 3:
        skillsMenu()
        
def skillsMenu():
    print("Please select one of those skill:\n1. Python\n2. C++\n3. HTML\n4. JavaScript\n5. CSS")
    selection = int(input("-> "))
    print("Under Construction")
    actionsMenu()

def main():
    accounts = AccountCreation("incollege")
    initialScreen(accounts)
    accounts.close()

if __name__ =="__main__":
    main()

