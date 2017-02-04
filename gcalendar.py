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
DNI_BOT = 'fbt1r7ekung1spfcfacnva7990@group.calendar.google.com'


class gcalendar:

    def __init__(self):
        def get_credentials():
            """Gets valid user credentials from storage.

            If nothing has been stored, or if the stored credentials are
             invalid, the OAuth2 flow is completed to obtain the new
             credentials.

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
                flow = client.flow_from_clientsecrets(
                    CLIENT_SECRET_FILE, SCOPES)
                flow.user_agent = APPLICATION_NAME
                if flags:
                    credentials = tools.run_flow(flow, store, flags)
                else:  # Needed only for compatibility with Python 2.6
                    credentials = tools.run(flow, store)
                print('Storing credentials to ' + credential_path)
            return credentials

        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=http)

    def addTakeOffEvents(self, user, date_list):

        for x in date_list:
            start_datetime = datetime.combine(x['date'], time(9, 0))
            end_datetime = datetime.combine(x['date'], time(17, 30))
            summary = user

            if x['time'] == 'morning':
                end_datetime = datetime.combine(x['date'], time(12, 0))
                summary += '早上'
            elif x['time'] == 'afternoon':
                start_datetime = datetime.combine(x['date'], time(13, 0))
                summary += '下午'

            summary += '請假'
            self.addEventstoGCalendar(summary, start_datetime, end_datetime)

    def getEventsFromGCalendar(self, start_datetime, end_datetime):
        timeMin = start_datetime.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
        timeMax = end_datetime.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
        return self.service.events().list(
            calendarId=DNI_BOT, pageToken=None,
            timeMin=timeMin, timeMax=timeMax).execute()

    def addEventstoGCalendar(self, summary, start_datetime, end_datetime):
        start_time = start_datetime.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
        end_time = end_datetime.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'

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

        event = self.service.events().insert(
            calendarId=DNI_BOT, body=event).execute()
        print('GClalendar event created: %s (id:%s)' % (
            event.get('summary'), event.get('id')))

    def rmEventFromGCalendar(self, summary, start_datetime):
        events = self.getEventsFromGCalendar(
            start_datetime,
            datetime.combine(start_datetime.date(), time(17, 30)))

        for event in events['items']:
            if event.get('summary') == summary:
                self.service.events().delete(
                    calendarId=DNI_BOT, eventId=event['id']).execute()
                print('GClalendar event removed: %s (id:%s)' % (
                    event.get('summary'), event.get('id')))

    def queryEventsFromGCalendar(self, start_datetime, end_datetime):
        summarys = []
        events = self.getEventsFromGCalendar(start_datetime, end_datetime)

        for event in events['items']:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

            summarys.append(event['summary'])

        return summarys


if __name__ == '__main__':
    x = gcalendar()
    x.queryEventsFromGCalendar(
        datetime.combine(
            date.today(), time(9, 0)),
        datetime.combine(
            date.today(), time(17, 30)))

    # insert event today
    x.addTakeOffEvents(
        'ethan',
        [{'date': date.today(), 'time': 'afternoon'}])
    # x.addEventstoGCalendar('ethan下午請假', date.today(), 'afternoon')
    x.rmEventFromGCalendar(
        'ethan下午請假',
        datetime.combine(date.today(), time(9, 0)))
