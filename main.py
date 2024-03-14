import csv
import json
import smtplib
from datetime import datetime
from json import JSONDecodeError

user_dict = {}


def prepare_json_data(name, birth_date, email):
    # Prepare JSON as dictionary
    global user_dict
    if len(user_dict) == 0:  # Check if dictionary is empty
        user_dict = {birth_date: []}  # Create Key Value pair with value as an empty list
        user_dict[birth_date].append({"name": name, "email": email})  # Add items to the list
    else:
        try:
            if user_dict[birth_date]:  # To Handle more than one person having bdays on the same day.
                user_dict[birth_date].append({"name": name, "email": email})  # Add items to the existing list
        except KeyError:  # Create new entry
            user_dict = {birth_date: []}
            user_dict[birth_date].append({"name": name, "email": email})

    # add dictionary as JSON to JSON file
    try:
        with open("bday_list.json", "r") as json_file: # Update existing JSON file
            bday_info = json.load(json_file)
    except FileNotFoundError:
        with open("bday_list.json", "w") as json_file:  # Create new JSON
            json.dump(user_dict, json_file, indent=4)
    except JSONDecodeError:  # In situations where JSON file is present but empty without values
        with open("bday_list.json", "w") as json_file:
            json.dump(user_dict, json_file, indent=4)
    else:
        bday_info.update(user_dict)
        with open("bday_list.json", "w") as json_file:
            json.dump(bday_info, json_file, indent=4)


def prepare_data_from_csv():  # Converting CSV to JSON
    with open("bday_list.csv", "r") as csv_input_file:
        for i in csv.reader(csv_input_file):
            name = i[0]
            birth_date = i[1]
            birth_date = birth_date[:5]
            email = i[2]
            prepare_json_data(name, birth_date, email)


def send_email(user_info, mail_template, subject):
    my_email = "test@gmail.com"
    password = "PASSWORD"  # Dummy Values

    connection = smtplib.SMTP("smtp.gmail.com")  # smtp information || smtplib port number 587 -- config
    connection.starttls()

    connection.login(user=my_email, password=password)

    with open(mail_template, "r") as email_template:  # txt file converted to string
        email_string = email_template.read()

    for i in range(len(user_info)):  # Loop is used when multiple emails have to be sent

        recipient_email = user_info[i]["email"]
        temp = email_string.replace("<recipient>", user_info[i]["name"])  # email_string is immutable hence temp is used to capture the modified string.
        temp = temp.replace("<admin>", user_info[i]["name"])  # Depending on the type of user recipient/ admin the replacement action takes place.
        modified_string = temp.replace("<timestamp>", str(datetime.now()))

        connection.sendmail(from_addr=my_email, to_addrs=recipient_email,
                            msg=f"Subject: {subject}\n\n{modified_string}")

    connection.close()


def check_date():  # Function checks date and triggers appropriate functions
    prepare_data_from_csv()

    date = datetime.now()
    new_date = date.strftime("%d")
    new_month = date.strftime("%m")
    today_date = new_month + "-" + new_date

    with open("bday_list.json", "r") as json_file:
        bday_dict = json.load(json_file)
        try:
            user_info = bday_dict[today_date]
        except KeyError:
            admin_info = [{"name": "Shraveen", "email": "test@gmail.com"}]
            send_email(admin_info, "no_bday.txt", "No B'day mails for today!")
            print(f"No birthday(s) today. Timestamp: {datetime.now()}")
        else:
            admin_info = [{"name": "Shraveen", "email": "test@gmail.com"}]
            send_email(user_info, "bday_email_template.txt", "Happy Birthday!")
            send_email(admin_info, "mail_to_admin.txt", "B'day Emails have been sent!")
            print(f"Email(s) sent to respective user(s) at {datetime.now()}")

check_date()
