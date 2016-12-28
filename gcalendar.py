from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from datetime import datetime, date, time

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'abcde'
DNI_BOT  = 'fbt1r7ekung1spfcfacnva7990@group.calendar.google.com'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

class gcalendar:

    def __init__(self):
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=http)

    def addEventstoGCalendar(self, user, date_list):
        summary = ("%s" % (user))

        for x in date_list:
            start_time = ''
            end_time = ''
            if x['time'] == 'wholeday':
                start_time = ("%sT09:00:00+08:00"%str(x['date']))
                end_time = ("%sT17:30:00+08:00"%str(x['date']))
            elif x['time'] == 'morning':
                start_time = ("%sT09:00:00+08:00"%str(x['date']))
                end_time = ("%sT12:00:00+08:00"%str(x['date']))
                summary = summary + '早上'
            elif x['time'] == 'afternoon':
                start_time = ("%sT13:00:00+08:00"%str(x['date']))
                end_time = ("%sT17:30:00+08:00"%str(x['date']))
                summary = summary + '下午'

            summary = summary + '請假'

            # define event
            event = {
              'summary': summary,
              'location': '',
              'description': 'Created by SlackBot',
              'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Taipei',
              },
              'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Taipei',
              },
            }

            event = self.service.events().insert(calendarId=DNI_BOT, body=event).execute()
            print('Event created: %s' % (event.get('summary')))

    def queryEventsFromGCalendar(self, aDate):
        summarys = []
        timeMin = datetime.combine(aDate, time(9,0)).isoformat()+'+08:00'
        timeMax = datetime.combine(aDate, time(17,30)).isoformat()+'+08:00'

        events = self.service.events().list(calendarId=DNI_BOT, pageToken=None, timeMin=timeMin, timeMax=timeMax).execute()
        for event in events['items']:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

            summarys.append(event['summary']);

        return summarys

if __name__ == '__main__':
    x = gcalendar()
    x.queryEventsFromGCalendar(date.today())

    # insert event today
    x.addEventstoGCalendar('ethan',[{'date':date.today(), 'time':'afternoon'}])
