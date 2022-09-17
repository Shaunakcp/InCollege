# InCollege
User_list = []         # list to store class objects of UserAccount
def makeNewAccount():
      newName = userName()
      newPass = newPassword()
      User = UserAccount(newName, newPass)
      User_list.append(User)
      print("\nNewly added user is: ",User.userName)
def newPassword():
  passAcceptable = False           # variable for determining whether the password is acceptable.
  while(passAcceptable != True):    # while loop to check password acceptability.
    nPass = str(input("Enter a unique password.\n minimum of 8 characters,\n maximum of 12 characters,\n at least one capital letter,\n one digit,\n one special character\n> "))  # enter password.
    r1, r2, r3 = False, False, False      # variables to hold if there is a capital letter (r1), a digit (r2), a special character (r3).
    if len(nPass) < 8:      # Checking minimum pass length.
      print("ERROR: Password must be atleast 8 characters!")
      continue                  # restart loop if bad password.
    elif (len(nPass) > 12):     # Checking maximum pass length.
      print("ERROR: Password must be at maximum 12 characters!") 
      continue                  # restart loop if bad password.
    
    for i in nPass: 
      if i.isupper():            # there is a capital letter (r1)
        r1 = True
      if i.isdigit():             # there is a digit (r2)
        r2 = True
      if not((i.isalnum()) or (i==' ')):  # there is a special character and no spaces (r3)
        r3 = True
    if not (r1 and r2 and r3):
      print("ERROR: Password does not meet ALL requirements, try again.")
      continue
    passAcceptable = True
  return nPass

def userName():
  uName = str(input("Enter your user name: "))
  return uName
def loginUser():
  flag = 0
  while flag!=1:
    userName = input("\nEnter your username: ")
    userPassword = input("\nEnter your password: ")
    
    for line in open("UserDatabase.txt","r").readlines(): 
      userInfo = line.split() 
      if userName == userInfo[0] and userPassword == userInfo[1]:
        print("Login successful!")
        print("welcome ",userName)
        return True
      print("Your Username or Password is incorrect.")
      return False
    
    '''for users in User_list:
      if userName == users.userName and userPassword == users.userPassword:
        print("\nLogin Successful")
        print("\nWelcome ",userName)
        flag = 1
        break
      else:
        continue
    if flag == 0:
      print("\nUsername or Password Might be incorrect. Try again")   
      continue  '''
def storeUserData(User_list):   # Function to store user name and pass to .txt file
  with open('UserDatabase.txt', 'a+') as f:
    for i in User_list:
      f.write(i.getName())
      f.write(" ")
      f.write(i.getPass())
      f.write("\n")
    f.close()

def main (): 
  selection = 1
  while selection!=3:
    selection = int(input("Make a selection:\n 1. Create a new account (type 1)\n 2. Login to existing account (type 2)\n 3. Exit the code\n "))
    if selection==1:       # Making new account
      with open("UserDatabase.txt", 'r') as f:
        x = len(f.readlines())
        if x >= 5:
          print("All permitted accounts have been created, please come back later")
          f.close
          continue
      makeNewAccount()
      storeUserData(User_list)
      

    elif selection==2:     #logging in into existing account
      loginUser()
    
class UserAccount:       # class for storing username and password
  def __init__(self, userName, userPassword):
    self.userName = userName
    self.userPassword = userPassword

  def getName(self):
    return self.userName
  def getPass(self):
    return self.userPassword

main()    # call main
