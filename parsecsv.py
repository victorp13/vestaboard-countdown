import csv, urllib.request, os
from datetime import date, datetime
from vestaboard.formatter import Formatter
import config

URL = config.googlesheets_url

# This function calculates the number of days until a future date
def days_until(futuredate):
    futuredate = datetime.date(datetime.strptime(futuredate, "%Y-%m-%d"))
    return abs((futuredate - date.today()).days)

# This function updates the Vestaboard with the latest data from the Google Sheet
def update_vestaboard():
    response = urllib.request.urlopen(URL)
    lines = [l.decode('utf-8') for l in response.readlines()]
    cr = csv.reader(lines)

    lineNum = 0
    state = 'START'
    showEvents = False
    showMessage = False
    events = []
    message = ''

    # Go through each row in the CSV file and create a list of events with the number of days until the event. Also create a message to display on the Vestaboard.
    for row in cr:
        lineNum += 1
        match row[0]:
            case "DAYS UNTIL":
                state = 'DAYS UNTIL'
                if (row[1] == 'ON'):
                    showEvents = True
            case "MESSAGE":
                state = 'MESSAGE'
                if (row[1] == 'ON'):
                    showMessage = True
            case default:
                match state:
                    case 'DAYS UNTIL':
                        if (showEvents and row[0] != '' and row[1] != ''):
                            events.append([row[0], str(days_until(row[1]))])
                    case 'MESSAGE':
                        if (showMessage and row[0] != ''):
                            message += row[0]

    lines = []

    # Create the list of event lines to send to the Vestaboard
    if showEvents:
        lines.append(Formatter().convertLine('DAYS TILL:', justify='left'))
        for event in events:
            lines.append(Formatter().convertLine('  ' + event[0].ljust(15) + event[1].rjust(3), justify='left'))
    # Create the message line and add it to the lines to send to the Vestaboard
    if showMessage:
        for i in range (5 - len(lines)):
            lines.append(Formatter().convertLine(''))
        lines.append(Formatter().convertLine(message, justify='center'))

    # Add blank lines to the end of the lines to send to the Vestaboard if there are less than 6 lines
    if len(lines) < 6:
        for i in range(6 - len(lines)):
            lines.append(Formatter().convertLine(''))

    # Print the lines to send to the Vestaboard (for debugging)
    print(lines)

    # Send the lines to the Vestaboard
    # Only send the lines when showEvents or showMessage is True
    if showEvents or showMessage:
        send_lines(lines)

def send_lines(lines):
    req = urllib.request.Request('http://' + config.vestaboard_ip + ':7000/local-api/message', method="POST")
    req.add_header('X-Vestaboard-Local-Api-Key', config.vestaboard_key)
    data = str(lines)
    data = data.encode()
    r = urllib.request.urlopen(req, data=data)


# This if statement guarantees that update_vestaboard function runs when this file is called directly. It allows me to both call the main function from the Flask server as well as run this script from the command line or cron job.
if __name__ == '__main__':
    update_vestaboard()