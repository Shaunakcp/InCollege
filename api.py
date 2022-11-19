# try:
#     with open("newJobs.txt", 'r') as f:
#         lines = f.readlines()
#         data = []
#         i = 0
#         for line in lines:
#             if line == '=====\n':
#                 print(data)
#                 i = 0
#                 data = []
#                 continue
#             if i != 1:
#                 data.append(line.rstrip('\n'))
#                 i += 1
#             elif line != '&&&\n':
#                 if len(data) < 2:
#                     data.append(line.rstrip('\n'))
#                 else:
#                     data[1] += '\n' + line.rstrip('\n')
#             elif line == '&&&\n':
#                 i += 1
#         print(data)
# except FileNotFoundError:
#     print("newJobs.txt not found")
import os
try:
    with open("studentAccounts.txt", 'r') as f:
        lines = f.readlines()
        data = []
        for line in lines:
            if line == '=====\n':
                print(data)
                data = []
                continue
            line = line.strip('\n')
            data += line.split(' ')
        if data != []:
            print(data)
except FileNotFoundError:
    print("studentAccounts.txt not found")
os.remove("studentAccounts.txt")