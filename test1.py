from turtle import title
import incollege
import os


# Epic 10 API, Due: 11/21/2022 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def test_profileAPIinputHandling(): # test that AccountCreation APIinputHangling is working 
    global accounts
    accounts = incollege.AccountCreation("testAPI")
    assert os.path.exists("MyCollege_users.txt")  # check that MyCollege_users.txt has the same contents as test_studentAccounts.txt
    assert os.path.exists("test_studentAccounts.txt")
    with open("MyCollege_users.txt", "r") as f:
        with open("test_studentAccounts.txt", "r") as g:
            assert f.read() == g.read()
    # close txt files
    f.close()
    g.close()


# test that JobPosting APIinputHangling is working
def test_jobsAPIinputHandling(): # test that JobPosting APIinputHangling is working
    global jobs
    jobs = incollege.JobPosting("testAPI")
    assert os.path.exists("MyCollege_jobs.txt")  # check that MyCollege_jobs.txt has the same contents as test_newJobs.txt
    assert os.path.exists("test_newJobs.txt")
    with open("MyCollege_jobs.txt", "r") as f:
        with open("test_newJobs.txt", "r") as g:
            assert f.read() == g.read()   
    f.close()
    g.close()
    
