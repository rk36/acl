import click
import keyring
import getpass
from source.scrapper import attempt
from tabulate import tabulate
from missedClassScrapper import MissedClassDates

@click.command()
@click.option('-r', '--roll', prompt='Roll Number', help='Enter the Roll Number for ERP Login.')
def attendance(roll):
    """
    Get the credentials first
    """
    password = keyring.get_password('ERP', roll)
    saved_password = True

    if password != None:
        response = attempt(roll, password)

        if not response:
            click.echo(click.style('Password modified, Enter new password.', fg='green', bold=True))
            keyring.delete_password('ERP',roll)
            password = None

    if password == None:
        password = getpass.getpass("Password : ")
        response,password = ResponseAttempt(roll,password)
        saved_password = False

    # Fetch attendance from ERP and Pretty Print it on Terminal.
    attendance_table = make_table(response)
    show_table(attendance_table)

    # Fetch missed classes from ERP and Pretty Print it on Terminal.
    ans = input("Do you want to see the missed class(es) date-wise ? (y/N) ")
    if ans=='y':
        print("please wait, it may take a while to fetch the information... \n")
        missed_class_response = MissedClassDates(roll,password)
        missed_class_table = make_missed_class_table(missed_class_response)
        show_table(missed_class_table)

        
    # Store password locally if not saved already
    if not saved_password:
        ans = input("Do you want to store your password locally? (y/N) ")
        if ans=='y':
            keyring.set_password('ERP', roll, password)


def make_table(response):
    result = list()
    for (code, data) in response.items():
        row = list()
        row.append(data['name'])
        row.append(data['attended'] + '/' + data['total'])
        row.append(data['percentage'])
        result.append(row)

    return result

def make_missed_class_table(response):
    result = list()
    for (Date, data) in response.items():
        row = list()
        row.append(data['Date'])
        row.append(data['subjectName'])
        row.append(data['attended'] + '/' + data['total'])
        result.append(row)

    return result

def ResponseAttempt(roll, password):

    response = attempt(roll, password)

    if not response:
        click.secho('Invalid Credentials, Sorry, try again', fg='red', bold=True)
        password = getpass.getpass("Password : ")
        response = attempt(roll, password)

    if not response:
        click.secho('Invalid Credentials, Sorry, try one more time.', fg='red', bold=True)
        password = getpass.getpass("Password : ")
        response = attempt(roll, password)

    if not response:
        click.secho('Invalid Credentials, 3 incorrect attempts', fg='red', bold=True)
        exit(0)

    return response,password


def show_table(table):
    print(tabulate(table, headers=["Date","Subject Name", "Attended"],tablefmt="fancy_grid"))




