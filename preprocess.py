import os
import sys
import csv
import imghdr
import requests
from shutil import move
from datetime import datetime
from dateutil.relativedelta import relativedelta


def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=view"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

line_number = 0

if len(sys.argv) != 2 and len(sys.argv) != 3:
    print('ERROR: Run as "python ' + sys.argv[0] + ' CSV_FILE [OUT_FILE]"')
    sys.exit(1)

if len(sys.argv) == 3:
    csv_output = open(sys.argv[2], "w")
else:
    csv_output = open("students.csv", "w")

total_lines = 0

with open(sys.argv[1], "r") as f:
    for line in f:
        total_lines += 1

with open(sys.argv[1], "r") as f:
    csv_reader = csv.reader(f, delimiter=',')
    dirName = 'pictures'
    try:
        # Create target Directory
        os.mkdir(dirName)
        print("Directory " + dirName +  " Created ") 
    except:
        print("Directory " + dirName +  " already exists")
    for line in csv_reader:
        if line_number == 0:
            csv_output.write("name,country,D0,D1,M0,M1,Y0,Y1,")
            csv_output.write("TD0,TD1,TM0,TM1,TY0,TY1\n")
        else:
            print(str(line_number) + "/" + str(total_lines - 1))
            name = line[1]
            if len(name) > 30:
                print('WARNING: Name "' + name + '" longer than 30 characters!')
                names = name.split()
                i = 0
                for n in names:
                    print("[" + str(i) + "] " + n)
                    i += 1
                print("Which names should I use? (use numbers separated by ',')")
                text = raw_input("Names: ")
                names_to_use = text.split(",")
                name = ""
                for ntu in names_to_use:
                    name += " " + names[int(ntu)]
                name = name[1:]
            country = line[2]
            date_str = line[3]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            today_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            age = relativedelta(datetime.now(), date_obj).years
            if age < 18:
                print("ERROR: " + name + " younger than 18! (" + str(age) + ")")
            D0 = date_str[8]
            D1 = date_str[9]
            M0 = date_str[5]
            M1 = date_str[6]
            Y0 = date_str[2]
            Y1 = date_str[3]
            TD0 = today_str[8]
            TD1 = today_str[9]
            TM0 = today_str[5]
            TM1 = today_str[6]
            TY0 = today_str[2]
            TY1 = today_str[3]
            csv_output.write(name + "," + country + "," + D0 + "," + D1 + "," + M0 + "," + M1 + "," + Y0 + "," + Y1 + ",")
            csv_output.write(TD0 + "," + TD1 + "," + TM0 + "," + TM1 + "," + TY0 + "," + TY1 + "\n")
            file_id = line[4][line[4].find("id=") + 3:]
            download_file_from_google_drive(file_id, name)
            fileType = imghdr.what(name)
            if fileType == None:
                print("Couldn't find out the picture type, please add it manually to the end of the filename for " + name)
            else:
                move(name, os.path.join('pictures', name + '.' + fileType))
        line_number += 1

csv_output.close()