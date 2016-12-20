from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

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

def addEventstoGCalendar(user, date_list):
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    summary = ("%s請假" % (user))

    for x in date_list:
        start_time = ''
        end_time = ''
        if x['time'] == 'wholeday':
            start_time = ("%sT09:00:00+08:00"%str(x['date']))
            end_time = ("%sT17:30:00+08:00"%str(x['date']))
        elif x['time'] == 'morning':
            start_time = ("%sT09:00:00+08:00"%str(x['date']))
            end_time = ("%sT12:00:00+08:00"%str(x['date']))
        elif x['time'] == 'afternoon':
            start_time = ("%sT13:00:00+08:00"%str(x['date']))
            end_time = ("%sT17:30:00+08:00"%str(x['date']))

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

        event = service.events().insert(calendarId=DNI_BOT, body=event).execute()
        print('Event created: %s' % (event.get('summary')))
