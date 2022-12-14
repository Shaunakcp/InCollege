from turtle import title
import incollege
import os

# EPIC 1 TESTING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# This test_ case tests whether there's userTest1 in the username database
def test_RepeatedUsername_1():
    accounts = incollege.AccountCreation("test")
    assert accounts.checkExistingUsername("userTest1")


# This test_ case tests whether there's userTest1 in the username database
def test_RepeatedUsername_2():
    global accounts
    accounts = incollege.AccountCreation("test")
    accounts.addAccount("userTest1", "Password-123", "first", "last", "USF",
                        "CS")
    assert not accounts.checkExistingUsername("userTest1")


# This test_ case test_s whether there's userTest2 in the username database
def test_RepeatedUsername_3():
    accounts = incollege.AccountCreation("test")
    assert accounts.checkExistingUsername("userTest2")


# This password has less than 8 characters
def test_Password_1():
    accounts = incollege.AccountCreation("test")
    assert not accounts.checkPasswordConvention("pass")


# This password has more than 12 characters
def test_Password_2():
    accounts = incollege.AccountCreation("test")
    assert not accounts.checkPasswordConvention("Passssswooordd")


# This password doesn't have any Capital Letter
def test_Password_3():
    accounts = incollege.AccountCreation("test")
    assert not accounts.checkPasswordConvention("pass-1234")


# This password doesn't have any Digit
def test_Password_4():
    accounts = incollege.AccountCreation("test")
    assert not accounts.checkPasswordConvention("Password-")


# This password doesn't have any Special Letter
def test_Password_5():
    accounts = incollege.AccountCreation("test")
    assert not accounts.checkPasswordConvention("Pass4321")


# This password has a space
def test_Password_6():
    accounts = incollege.AccountCreation("test")
    assert not accounts.checkPasswordConvention("Pass- 412")


# TESTING ACCOUNT LIMIT IS 10 USERS


# Account limit 2/10
def test_AccountLimit_2():
    accounts = incollege.AccountCreation("test")
    accounts.addAccount("userTest2", "Password-123", "first2", "last2", "USF",
                        "CS")
    assert accounts.checkLimit()


# Account limit 3/10
def test_AccountLimit_3():
    accounts = incollege.AccountCreation("test")
    accounts.addAccount("userTest3", "Password-123", "first3", "last3", "USF",
                        "CS")
    assert accounts.checkLimit()


# Account limit 4/10
def test_AccountLimit_4():
    accounts = incollege.AccountCreation("test")
    accounts.addAccount("userTest4", "Password-123", "first4", "last4", "USF",
                        "CS")
    assert accounts.checkLimit()


# Account limit 5/10
def test_AccountLimit_5():
    accounts = incollege.AccountCreation("test")
    accounts.addAccount("userTest5", "Password-123", "first5", "last5", "USF",
                        "CS")
    assert accounts.checkLimit()


# Account limit 6/10
def test_AccountLimit_6():
    accounts = incollege.AccountCreation("test")
    accounts.addAccount("userTest6", "Password-123", "first6", "last6", "USF",
                        "CS")
    assert accounts.checkLimit()


# Account limit 7/10
def test_AccountLimit_7():
    accounts = incollege.AccountCreation("test")
    accounts.addAccount("userTest7", "Password-123", "first7", "last7", "USF",
                        "CS")
    assert accounts.checkLimit()


# Account limit 8/10
def test_AccountLimit_8():
    accounts = incollege.AccountCreation("test")
    accounts.addAccount("userTest8", "Password-123", "first8", "last8", "USF",
                        "CS")
    assert accounts.checkLimit()


# Account limit 9/10
def test_AccountLimit_9():
    accounts = incollege.AccountCreation("test")
    accounts.addAccount("userTest9", "Password-123", "first9", "last9", "USF",
                        "CS")
    assert accounts.checkLimit()


# They're too many accounts
def test_AccountLimit_10():
    accounts = incollege.AccountCreation("test")
    accounts.addAccount("userTest10", "Password-123", "first10", "last10",
                        "USF", "CS")
    assert not accounts.checkLimit()


# Signin using correct username and password
def test_SignIn_1():
    accounts = incollege.AccountCreation("test")
    assert accounts.checkUsername("userTest1") and accounts.checkPassword(
        "userTest1", "Password-123")


# Signin using incorrect username
def test_SignIn_2():
    accounts = incollege.AccountCreation("test")
    assert not (accounts.checkUsername("userTest?")
                and accounts.checkPassword("userTest?", "Password-123"))


# Signin using correct username and wrong password
def test_SignIn_3():
    accounts = incollege.AccountCreation("test")
    assert not (accounts.checkUsername("userTest1")
                and accounts.checkPassword("userTest1", "Password-321"))


# Test for number of jobs limit
def test_jobLimitTest_1():
    jobs = incollege.JobPosting("test")
    jobs.addJob("title1", "description1", "employer1", "location1", "salary1",
                "testUser1")
    assert jobs.checkLimit()


def test_jobLimitTest_2():
    jobs = incollege.JobPosting("test")
    jobs.addJob("title2", "description2", "employer2", "location2", "salary2",
                "testUser2")
    assert jobs.checkLimit()


def test_jobLimitTest_3():
    jobs = incollege.JobPosting("test")
    jobs.addJob("title3", "description3", "employer3", "location3", "salary3",
                "testUser3")
    assert jobs.checkLimit()


def test_jobLimitTest_4():
    jobs = incollege.JobPosting("test")
    jobs.addJob("title4", "description4", "employer4", "location4", "salary4",
                "testUser4")
    assert jobs.checkLimit()


def test_jobLimitTest_5():
    jobs = incollege.JobPosting("test")
    jobs.addJob("title5", "description5", "employer5", "location5", "salary5",
                "testUser5")
    assert jobs.checkLimit()


def test_jobLimitTest_6():
    jobs = incollege.JobPosting("test")
    jobs.addJob("title6", "description6", "employer6", "location6", "salary6",
                "testUser6")
    assert jobs.checkLimit()


# Increased Job limit to 10


def test_jobLimitTest_7():
    jobs = incollege.JobPosting("test")
    jobs.addJob("title7", "description7", "employer7", "location7", "salary7",
                "testUser7")
    assert jobs.checkLimit()


def test_jobLimitTest_8():
    jobs = incollege.JobPosting("test")
    jobs.addJob("title8", "description8", "employer8", "location8", "salary8",
                "testUser8")
    assert jobs.checkLimit()


def test_jobLimitTest_9():
    jobs = incollege.JobPosting("test")
    jobs.addJob("title9", "description9", "employer9", "location9", "salary9",
                "testUser9")
    assert jobs.checkLimit()


#Determine if At limit
def test_jobLimitTest_10():
    jobs = incollege.JobPosting("test")
    jobs.addJob("title10", "description10", "employer10", "location10",
                "salary10", "testUser10")
    assert not jobs.checkLimit()


#Determine if over limit
def test_jobLimitTest_11():
    jobs = incollege.JobPosting("test")
    jobs.addJob("title11", "description11", "employer11", "location11",
                "salary11", "testUser11")
    assert not jobs.checkLimit()


# Epic 3 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Test for email notification option
def test_emailnotificationTest_1():
    global accounts
    accounts = incollege.AccountCreation("test")
    accounts.currentUser = "userTest1"
    _, _, _, _, _, _, email, _, _, _, _ = accounts.searchAccount("userTest7")
    assert email == "On"


def test_emailnotificationTest_2():
    global accounts
    accounts = incollege.AccountCreation("test")
    accounts.currentUser = "userTest7"
    accounts.updateGuestControls("Off", "On", "On")
    _, _, _, _, _, _, email, _, _, _, _ = accounts.searchAccount("userTest7")
    assert email == "Off"


# Test for SMS notification option
def test_smsnotificationTest_1():
    global accounts
    accounts = incollege.AccountCreation("test")
    accounts.currentUser = "userTest7"
    _, _, _, _, _, _, _, sms, _, _, _ = accounts.searchAccount("userTest7")
    assert sms == "On"


def test_smsnotificationTest_2():
    global accounts
    accounts = incollege.AccountCreation("test")
    accounts.currentUser = "userTest7"
    accounts.updateGuestControls("On", "Off", "On")
    _, _, _, _, _, _, _, sms, _, _, _ = accounts.searchAccount("userTest7")
    assert sms == "Off"


# Test for Targeted Advertising Features option
def test_adFeaturesTest_1():
    global accounts
    accounts = incollege.AccountCreation("test")
    accounts.currentUser = "userTest7"
    _, _, _, _, _, _, _, _, adFeatures, _, _ = accounts.searchAccount("userTest7")
    assert adFeatures == "On"


def test_adFeaturesTest_2():
    global accounts
    accounts = incollege.AccountCreation("test")
    accounts.currentUser = "userTest7"
    accounts.updateGuestControls("On", "On", "Off")
    _, _, _, _, _, _, _, _, adFeatures, _, _ = accounts.searchAccount("userTest7")
    assert adFeatures == "Off"


# Test for Language Preference without signing in
def test_nonsigninLanguageTest_1():
    global accounts
    accounts = incollege.AccountCreation("test")
    accounts.currentUser = None
    assert accounts.language == "English"


def test_nonsigninLanguageTest_2():
    global accounts
    accounts = incollege.AccountCreation("test")
    accounts.currentUser = None
    accounts.language = "Spanish"
    assert accounts.language == "Spanish"


# Test for Language Preference with signing in
def test_signinLanguageTest_1():
    global accounts
    accounts = incollege.AccountCreation("test")
    accounts.currentUser = "userTest7"
    lang = accounts.getLanguage()
    assert lang == "English"


def test_signinLanguageTest_2():
    global accounts, language
    language = "Spanish"
    accounts = incollege.AccountCreation("test")
    accounts.currentUser = "userTest7"
    accounts.updateLanguage("Spanish")
    lang = accounts.getLanguage()
    assert lang == "Spanish"


# Epic 4  16 Oct 2022 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Test for 10 Account limit -- in previous userlimit test cases


# test friend list initialized to empty
def test_friendListInitEmpty():
    global accounts
    accounts = incollege.AccountCreation("test")
    accounts.currentUser = "userTest1"

    global friends
    friends = incollege.Friends("test")

    assert not friends.listOfFriends(accounts.currentUser)


# search for others' accounts by lastname, uni, or major
def test_searchForFriendsUni():
    global accounts
    accounts = incollege.AccountCreation("test")
    accounts.currentUser = "userTest1"

    global friends
    friends = incollege.Friends("test")

    assert friends.searchForFriends("N/A", "USF", "N/A")


def test_searchForFriendsLastName():
    global accounts
    accounts = incollege.AccountCreation("test")
    accounts.currentUser = "userTest1"

    global friends
    friends = incollege.Friends("test")

    assert friends.searchForFriends("last10", "N/A", "N/A")


def test_searchForFriendsMajor():
    global accounts
    accounts = incollege.AccountCreation("test")
    accounts.currentUser = "userTest1"

    global friends
    friends = incollege.Friends("test")

    assert friends.searchForFriends("N/A", "N/A", "CS")


# pending friend requests
def test_pendingFriendRequests():
    global accounts
    accounts = incollege.AccountCreation("test")
    accounts.currentUser = "userTest1"
    global friends
    friends = incollege.Friends("test")

    assert not friends.checkIfPending(accounts.currentUser, "Test11")

# Epic 5  22 Oct 2022 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Newly created user does not have a profile
def test_emptyProfile():
    global accounts
    global profiles
    accounts = incollege.AccountCreation("test")
    profiles = incollege.ProfilesCreation("test")
    accounts.currentUser = "userTest1"
    assert profiles.checkExistingUsername('userTest1')


# Check for Title in Profile
def test_ProfileTitle():
    global accounts
    global profiles
    accounts = incollege.AccountCreation("test")
    profiles = incollege.ProfilesCreation("test")
    accounts.currentUser = "userTest1"
    profiles.addProfileUser("userTest1")
    profiles.addTitle(accounts.currentUser, "SWE")
    rows = profiles._cur.execute(
        "SELECT title FROM profiles WHERE profile_user = ?",
        (accounts.currentUser, ))
    assert rows.fetchall()[0][0] == "SWE"


# Check for Major name convention
def test_ProfileMajor():
    global accounts
    global profiles
    accounts = incollege.AccountCreation("test")
    profiles = incollege.ProfilesCreation("test")
    accounts.currentUser = "userTest1"
    profiles.addProfileUser("userTest1")
    profiles.addMajor(accounts.currentUser, "cOmPuTer ScIence")
    rows = profiles._cur.execute(
        "SELECT major FROM profiles WHERE profile_user = ?",
        (accounts.currentUser, ))
    assert rows.fetchall()[0][0] == "Computer Science"


# Check for University name convention
def test_ProfileUni():
    global accounts
    global profiles
    accounts = incollege.AccountCreation("test")
    profiles = incollege.ProfilesCreation("test")
    accounts.currentUser = "userTest1"
    profiles.addProfileUser("userTest1")
    profiles.addUni(accounts.currentUser, "uNiVerSity oF fLoridA")
    rows = profiles._cur.execute(
        "SELECT university FROM profiles WHERE profile_user = ?",
        (accounts.currentUser, ))
    assert rows.fetchall()[0][0] == "University Of Florida"


# Check for Info
def test_ProfileInfo():
    global accounts
    global profiles
    accounts = incollege.AccountCreation("test")
    profiles = incollege.ProfilesCreation("test")
    accounts.currentUser = "userTest1"
    profiles.addProfileUser("userTest1")
    profiles.addInfo(accounts.currentUser, "I'm a Sophomore")
    rows = profiles._cur.execute(
        "SELECT info FROM profiles WHERE profile_user = ?",
        (accounts.currentUser, ))
    assert rows.fetchall()[0][0] == "I'm a Sophomore"


# Check for Experience
def test_ProfileExp():
    global accounts
    global profiles
    accounts = incollege.AccountCreation("test")
    profiles = incollege.ProfilesCreation("test")
    accounts.currentUser = "userTest1"
    profiles.addProfileUser("userTest1")
    profiles.addExp(accounts.currentUser, "I worked at USF for 10 years")
    rows = profiles._cur.execute(
        "SELECT experience FROM profiles WHERE profile_user = ?",
        (accounts.currentUser, ))
    assert rows.fetchall()[0][0] == "I worked at USF for 10 years"


# Check for Education
def test_ProfileEdu():
    global accounts
    global profiles
    accounts = incollege.AccountCreation("test")
    profiles = incollege.ProfilesCreation("test")
    accounts.currentUser = "userTest1"
    profiles.addProfileUser("userTest1")
    profiles.addEdu(accounts.currentUser, "USF from 2020 to 2024")
    rows = profiles._cur.execute(
        "SELECT education FROM profiles WHERE profile_user = ?",
        (accounts.currentUser, ))
    assert rows.fetchall()[0][0] == "USF from 2020 to 2024"


# Check for modifications
def test_ProfileModification():
    global accounts
    global profiles
    accounts = incollege.AccountCreation("test")
    profiles = incollege.ProfilesCreation("test")
    accounts.currentUser = "userTest1"
    profiles.addProfileUser("userTest1")
    profiles.addTitle(accounts.currentUser, "IT Support")
    profiles.addMajor(accounts.currentUser, "iNforMatIon tEchNolOgy")
    profiles.addUni(accounts.currentUser, "uNiVerSity oF sOuth fLoridA")
    profiles.addInfo(accounts.currentUser, "I'm a Senior")
    profiles.addExp(accounts.currentUser, "I worked at USF for 2 years")
    profiles.addEdu(accounts.currentUser, "USF from 2020 to 2023")
    rows = profiles._cur.execute(
        "SELECT * FROM profiles WHERE profile_user = ?",
        (accounts.currentUser, ))
    assert rows.fetchall()[0] == (accounts.currentUser, "IT Support",
                                  "Information Technology",
                                  "University Of South Florida",
                                  "I'm a Senior",
                                  "I worked at USF for 2 years",
                                  "USF from 2020 to 2023")


# Epic 6 10/30/2022 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#user cannot apply to job made by self


def test_check_SelfApplicationUser():
    global accounts
    global jobs
    global jobapps
    jobs = incollege.JobPosting("test")
    accounts = incollege.AccountCreation("test")
    jobapps = incollege.JobApplication("test")
    accounts.currentUser = "userTest1"
    assert not jobs.selfApplyCheck('userTest1', 'title1')


def test_checkIfapplied():
    global accounts
    global jobs
    global jobapps
    jobs = incollege.JobPosting("test")
    accounts = incollege.AccountCreation("test")
    jobapps = incollege.JobApplication("test")
    accounts.currentUser = "userTest2"
    jobapps.createApplication('userTest2', 1)
    assert not jobapps.checkIfApplied('userTest1', 1)


# user cannot save job more than once
def test_check_savedjob():
    global accounts
    global jobs
    global jobapps
    jobs = incollege.JobPosting("test")
    accounts = incollege.AccountCreation("test")
    jobapps = incollege.JobApplication("test")
    accounts.currentUser = "userTest1"
    jobapps.saveAJob('userTest1', 1)
    assert jobapps.checkIfSaved('userTest1', 1)


def test_unsavignJob():
    global accounts
    global jobs
    global jobapps
    jobs = incollege.JobPosting("test")
    accounts = incollege.AccountCreation("test")
    jobapps = incollege.JobApplication("test")
    accounts.currentUser = "userTest1"
    jobapps.unsaveAJob('userTest1', 'title1')
    assert not jobapps.checkIfSaved('userTest1', 'title1')


# Epic 7 Due: 11/06/2022 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# checks if A users tier should be standard
def test_checkStandard_Tier():
    global accounts
    global membership
    membership = incollege.AccountCreation("test")
    accounts = incollege.AccountCreation("test")
    assert not membership.checkTier('userTest1')


# checks if A users changes tier from standard and becomes plus
def test_Plus_Tier():
    global accounts
    global membership
    membership = incollege.AccountCreation("test")
    accounts = incollege.AccountCreation("test")
    membership.changeTier('userTest1')
    assert membership.checkTier


# checks if A users message to a friend is working
def test_newMessage():
    global accounts
    global membership
    global messages
    membership = incollege.AccountCreation("test")
    accounts = incollege.AccountCreation("test")
    messages = incollege.Message("test")
    messages.addMessage('Hello friend!', 'userTest1', 'userTest10')
    assert messages.haveNewMessages('userTest10') == 1


# checks if A users message is unread by default
def test_unreadMessages():
    global accounts
    global membership
    global messages
    membership = incollege.AccountCreation("test")
    accounts = incollege.AccountCreation("test")
    messages = incollege.Message("test")
    assert messages.haveUnreadMessages('userTest1', 'userTest10') == 1


# checks if A users message is highlighted as read when read by recipent.
def test_readMessages():
    global accounts
    global membership
    global messages
    membership = incollege.AccountCreation("test")
    accounts = incollege.AccountCreation("test")
    messages = incollege.Message("test")
    messages.markAsRead(1)
    assert not messages.haveUnreadMessages('userTest1', 'userTest10') == 1


# checks if A users message is deleted when deleteing
def test_deleteMessages():
    global accounts
    global membership
    global messages
    membership = incollege.AccountCreation("test")
    accounts = incollege.AccountCreation("test")
    messages = incollege.Message("test")
    messages.deleteMessage(1)
    assert not messages.haveNewMessages('userTest10') == 1


# Epic 8 Notifications, Due: 11/14/2022 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# testing that a new user has not applied to a job and therefore will receive a notification
def test_userNotAppliedToJob7Days():
    global accounts
    global jobs
    global jobapps
    assert jobapps.haveNotApplied("userTest10")


# test that user will see number of jobs they applied for when they go to jobs section
def test_numOfJobsApplied0():
    global accounts
    global jobs
    global jobapps
    assert not jobapps.countJobApps("userTest10")


# test if a user has applied to atleast one job
def test_numOfJobsApplied1():
    global accounts
    global jobs
    global jobapps
    jobs = incollege.JobPosting("test")
    accounts = incollege.AccountCreation("test")
    jobapps = incollege.JobApplication("test")
    accounts.currentUser = "userTest3"
    jobapps.createApplication('userTest3', 1)
    assert not jobapps.haveNotApplied("userTest3")


# test that a user will have a message notification if they have unread messages
def test_userHasMessagesNotification():
    global accounts
    global membership
    global messages
    membership = incollege.AccountCreation("test")
    accounts = incollege.AccountCreation("test")
    messages = incollege.Message("test")
    messages.addMessage('Hello friend!', 'userTest1', 'userTest10')
    assert messages.haveNewMessages('userTest10')

