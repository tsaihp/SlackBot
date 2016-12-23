#-*- coding: utf-8 -*-

import requests
import json
import websocket
import time
import datetime
import sys
import csv

import gcalendar
import parsing_takeoff

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
        config_date = x['date'] + datetime.timedelta(4 - x['date'].weekday())
        config_content = "Take off in %s/%s/%s by SlackBot"%(x['date'].year,x['date'].month, x['date'].day)
        work_time = 20
        if x['time'] != 'wholeday':
            work_time = 10

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
                                                                   w_t=work_time,
                                                                   o_t=0,
                                                                   update_day=current_date,
                                                                   update_time=current_time
                                                                   )
        r = s.post('http://172.16.83.193/weekly/sql/db_insert_task.php', data=params)


# Define actions when taking off
def take_off_procedure(user_id, input_string):

    date_list = parsing_takeoff.parsing_takeoff_req(input_string)

    if len(date_list) > 0 and len(date_list) <= 5:
        # weekly report
        username = get_weeklyname_by_id(user_id)
        report_to_weeklyreport_system(username, date_list, False)

        # calendar
        username = get_username_by_id(user_id)
        gcalendar.addEventstoGCalendar(username, date_list)

        return date_list[0]

    return None

def get_username_by_id(id):
    for item in user_list:
        if item['slack_id'] == id:
            return item['slack_name']
    return None

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

    current_time=time.asctime(time.localtime(time.time()))
    r_type=r_msg.get("type", "NO_TYPE")

    # if r_type == "presence_change":
    #   username=get_username_by_id(r_msg["user"])
    #   print("%s %s %s"%(current_time, username, r_msg["presence"]))
    # elif r_type == "message":
    if r_type == "message":
        username=get_username_by_id(r_msg["user"])

        if username == None:
            print(r_msg)
            return

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
        elif parsing_takeoff.isTakeoffReq(input_msg):
            firstDate = take_off_procedure(r_msg["user"], input_msg)
            if firstDate:
                reply_msg = "你將於%d/%d開始休假, 祝休假愉快!"%(firstDate['date'].month,firstDate['date'].day)
            else:
                reply_msg = "拍謝啦, 我不了解你的明白, 你是不是時間給錯啦?"
            on_reply(ws, reply, reply_msg)
        else:
            reply_msg = "我是個測試用的機器人, 不要把人家玩壞惹"
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

    user_list = []
    with open('users.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            user_list.append(row)

    # connect to rtm
    r=requests.get(url,params=payload)
    rv = r.json()

    for user in rv['users']:
        if get_username_by_id(user['id']) == None:
            print ('User %s(%s) is not in the database!'%(user['name'],user['id']))

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
