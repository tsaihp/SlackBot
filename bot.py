#-*- coding: utf-8 -*-

import requests
import json
import websocket
import time
import datetime
import sys

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# init
url="https://slack.com/api/rtm.start"
users_profile_get="https://slack.com/api/users.profile.get"

payload={"token": "1111-11111111111-111111111111111111111111"}
user_list=[]

sample_content = (
    "A,-{year},-{mon},-{day},"
    "-{customer},-{project},"
    "-{content},-{w_t},-{o_t},-{update_day}<br>{update_time},"
    "-4,-{year}-{mon}-{day}|"
    )

# Report to weekly report system
def report_to_weeklyreport_system(user, date_list, halfday):

    print("[Weekly System]user:%s, take off:%s"%(user,date_list))

    # time config
    localtime = time.localtime(time.time())
    current_date = time.strftime("%Y/%m/%d", localtime)
    current_time = time.strftime("%H:%M:%S", localtime)

    # login to weeky report
    s = requests.Session()

    for x in date_list:
        # get next friday
        config_date = x + datetime.timedelta(4 - x.weekday())
        config_content = "Take off in %s/%s/%s by SlackBot"%(x.year,x.month, x.day)

        # post
        params = {}
        params['sqlUrl'] = '172.16.83.193'
        params['sendParam[0]'] = 'username:>{0}'.format(user)
        params['sendParam[1]'] = 'currentYear:>{0}'.format(config_date.year)
        params['sendParam[2]'] = 'currentMonth:>{0}'.format(config_date.month)
        params['sendParam[3]'] = 'currentDay:>{0}'.format(config_date.day)
        params['sendParam[4]'] = 'tasks:>' + sample_content.format(year=config_date.year,
                                                                   mon=config_date.month,
                                                                   day=config_date.day,
                                                                   customer='Other',
                                                                   project='Take off',
                                                                   content=config_content,
                                                                   w_t=20,
                                                                   o_t=0,
                                                                   update_day=current_date,
                                                                   update_time=current_time
                                                                   )
        r = s.post('http://172.16.83.193/weekly/sql/db_insert_task.php', data=params)

# Report to google spreadsheet
def report_to_googlespreadsheet(user, date_list, halfday):

    print("[GSpread System]user:%s, take off:%s"%(user,date_list))

    gc = gspread.authorize(credentials)
    sh = gc.open("dnisw_holiday_2016") 

    for x in date_list:
        # select sheet
        select_sheet = "{0}月".format(x.month)
        sht = sh.worksheet(select_sheet)

        # col: day
        day_list = sht.row_values(1)
        try:
          col_num = day_list.index(str(x.day))+1
        except ValueError:
          continue

        # row: user
        cell = sht.find(user)
        row_num = cell.row

        # update
        sht.update_cell(row_num, col_num, '1')


# Convert date sting to date object
def date_string_to_datetime(input_string):
    input_string = input_string.split("/")
    current_year = datetime.date.today().year

    try:
        tmp_datetime = datetime.date(current_year, int(input_string[0]), int(input_string[1]))
    except ValueError:
        print("Value Error: %d/%d/%d"%(current_year, int(input_string[0]), int(input_string[1])))
        return False

    # check if is futrue date
    if tmp_datetime < datetime.date.today():
        tmp_datetime = datetime.date(current_year+1, int(input_string[0]), int(input_string[1]))

    return tmp_datetime

# Parse the date string to list
# ex: input="1/1-2,1/5" output=['1/5','1/1','1/2']
def parsing_date_to_list(input_string):
    date_list = input_string.split(",")
    datetime_list = []

    for x in date_list:
        if x.find("-") != -1:
            tmp2 = x.split("/")
            tmp3 = tmp2[1].split("-")
            for y in range(int(tmp3[0]), int(tmp3[1])+1):
                tmp4 = "%s/%d"%(tmp2[0], y)

                if date_string_to_datetime(tmp4) != False:
                    datetime_list.append(date_string_to_datetime(tmp4))
        else:
            if date_string_to_datetime(x) != False:
                datetime_list.append(date_string_to_datetime(x))

    return datetime_list

# Define actions when taking off
def take_off_procedure(user_id, dates):
    # date list
    date_list = parsing_date_to_list(dates)

    # weekly report
    username = get_weeklyname_by_id(user_id)
    report_to_weeklyreport_system(username, date_list, False)

    # google spreadsheet
    username = get_googlename_by_id(user_id)
    report_to_googlespreadsheet(username, date_list, False)


def get_username_by_id(id):
    for item in user_list:
        if item['slack_id'] == id:
            return item['slack_name']
    return "No user match"

def get_weeklyname_by_id(id):
    for item in user_list:
        if item['slack_id'] == id:
            return item['weekly_name']
    return "No user match"

def get_googlename_by_id(id):
    for item in user_list:
        if item['slack_id'] == id:
            return item['google_name']
    return "No user match"

def on_reply(ws, reply, message):
    reply["text"] = message
    ws.send(json.dumps(reply))

def on_message(ws, message):
    r_msg=json.loads(message)

    if "type" not in r_msg:
        return

    current_time=time.asctime(time.localtime(time.time()))
    r_type=r_msg["type"]

    # if r_type == "presence_change":
    #   username=get_username_by_id(r_msg["user"])
    #   print("%s %s %s"%(current_time, username, r_msg["presence"]))
    # elif r_type == "message":
    if r_type == "message":
        username=get_username_by_id(r_msg["user"])
        # print(r_msg)

        # reply format
        reply={
            "id":r_msg["user"],
            "type":"message",
            "text":"吃飽未?",
            "channel":r_msg["channel"]
        }
        input_msg=r_msg["text"].lower();

        if username == "" or username == "No user match":
            # no user name
            return

        if r_msg["user"] == "U26SFGPP1":
            print("Bot: %s"%(r_msg["text"]))
            return

        if r_msg["channel"][0] == "C" and r_msg["text"].find("<@U26SFGPP1>") == -1:
            # Not for me
            return

        print("%s: %s"%(username, r_msg["text"]))

        if input_msg == "hello" or input_msg == "hi":
            reply["text"] = username + ", 您好, 吃飽未?"
            ws.send(json.dumps(reply))
        elif input_msg == "bot close":
            if username == "ethan":
                on_reply(ws, reply, "Bye~!")
                ws.close()
        elif input_msg.find("請假") != -1:
            va=input_msg.split()
            # print(va)
            if len(va) < 2:
                on_reply(ws, reply, "想請假嗎? 請依照以下格式\n \"請假 <日期> \", ex: 請假 9/9,9/11")
            else:
                take_off_procedure(r_msg["user"], va[1])
                reply_msg="你將於%s開始休假, 祝休假愉快!"%(va[1])
                on_reply(ws, reply, reply_msg)
        else:
            reply_msg = "我是個測試用的機器人, 請勿拍打餵食"
            on_reply(ws, reply, reply_msg)
    elif r_type == "error":
        print("Error (%d)! %s"%(r_msg['error']['code'], r_msg['error']['msg']))
        return

def on_error(ws, error):
    print(error)

def on_close(ws):
    # wait 5 seconds
    time.sleep(5)
    post_message_to_channel('test_channel', '拎北來睏惹!')
    print("### closed ###")

def on_open(ws):
    print("WS on_open!!")
    post_message_to_channel('test_channel', '拎北起床惹!')

def connect_to(ws, ws_url):
    ws.close()


def post_message(post_to, message):
    msg_payload = {
        'token': payload["token"],
        'channel': post_to,
        'as_user': True,
        'text': message
    }

    r = requests.get('https://slack.com/api/chat.postMessage', params=msg_payload)
    print(r.json())

def post_message_to_user(user, message):
    user = '@' + user
    post_message(user, message)

def post_message_to_channel(channel, message):
    channel = '#' + channel
    post_message(channel, message)


if __name__ == "__main__":

    # Read token from file
    f=open("setup.json", "r")
    payload["token"] = json.loads(f.read())["token"]
    f.close()

    # Read user's infomation
    f=open("users.json", "r")
    user_list = json.loads(f.read())["users"]
    f.close()

    # gspread.authorize
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('auth.json', scope)

    # connect to rtm
    r=requests.get(url,params=payload)
    rv = r.json()

    if rv['ok'] == True:
        print("Connect to slack RTM service: Success")
    else:
        print("Connect to slack RTM service: Fail!")
        print("Error: %s"%(rv['error']))
        sys.exit()

    wss_url=rv["url"]

    print("Bot %s is active now"%(rv["self"]['name']))

    ws = websocket.WebSocketApp(wss_url,
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
