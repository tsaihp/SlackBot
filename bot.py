#-*- coding: utf-8 -*-

import requests
import json
import websocket
import time

# init
url="https://slack.com/api/rtm.start"
payload={"token": "1111-11111111111-111111111111111111111111"}
user_list=[]

def get_username_by_id(id):
  for index, item in enumerate(rv['users']):
    if item['id'] == id:
      return item['name']
  return "No user match"

def on_message(ws, message):
  # print(message)
  r_msg=json.loads(message)
  current_time=time.asctime(time.localtime(time.time()))

  if "type" in r_msg:
    r_type=r_msg["type"]
  else:
    print(message)
    return

  if r_type == "presence_change":
    username=get_username_by_id(r_msg["user"])
    print("%s %s %s"%(current_time, username, r_msg["presence"]))
  elif r_type == "message":
    username=get_username_by_id(r_msg["user"])
    print("%s: %s"%(username, r_msg["text"]))

    # reply format
    reply={"id":r_msg["user"], "type":"message", "text":"吃飽未?", "channel":r_msg["channel"]}
    input_msg=r_msg["text"].lower();

    if input_msg == "hello" or input_msg == "hi":
      reply["text"] = username + ", 您好"
      ws.send(json.dumps(reply))
    else:
      reply["text"] = "我是個測試用的機器人, 請勿拍打餵食"
      ws.send(json.dumps(reply))

def on_error(ws, error):
  print(error)

def on_close(ws):
  print("### closed ###")

def on_open(ws):
  print("WS on_open!!")
  def run(*args):
    for i in range(3):
      time.sleep(1)
      ws.send("Hello %d" % i)
      time.sleep(1)
      ws.close()
      print("thread terminating...")
  # thread.start_new_thread(run, ())

def connect_to(ws, ws_url):
  ws.close()


if __name__ == "__main__":
  # Read token from file
  f=open("setup.json", "r")
  payload["token"] = json.loads(f.read())["token"]

  # connect to rtm
  r=requests.get(url,params=payload)
  rv=json.loads(r.text)
  print("Connect to slack RTM service: %s"%(rv['ok']))

  user_list = rv['users']

  wss_url=rv["url"]
  ws = websocket.WebSocketApp(wss_url,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
  ws.on_open = on_open
  ws.run_forever()
