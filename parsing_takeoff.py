#coding:utf-8

# 
# Parsing a string of taking off to datetime object
# Athor: Ethan Tsai
# Date: 2016/12/14
# 

import re
import datetime

month_day_pat = r'\d+/\d+'
month_day_range_pat = r'\d+/\d+-\d+/\d+'

date_pat = ['明天','後天',r'\w*禮拜.',r'\w*星期.',r'\w*週.',month_day_range_pat,month_day_pat]
time_pat = ['早上','上午','下午']
takeoff_pat = r'請\w*假'

test_items = [
                '明天請假',
                '明天請半天假',
                '明天上午請假',
                '明天上午請假半天',
                '明天早上請假',
                '明天下午請假',
                '後天請假',
                '下週一請假',
                '下禮拜一請假',
                '下禮拜一早上請假',
                '星期五請假',
                '下星期五請假',
                '12/30請假',
                '12/31早上請假',
                '11/11-11/15請假',
                '11/31請假'
            ]

weekday_prefix = ['禮拜','星期','週']

weekday_map = {
                '一': 0,
                '二': 1,
                '三': 2,
                '四': 3,
                '五': 4,
                '六': 5,
                '日': 6
            }

def match_pattern(pattern_list, input_string):
    for pattern in pattern_list:
        # print("pattern:%s input:%s"%(pattern, input_string))
        match = re.search(pattern, input_string)
        if match:
            return match.group()
    return None

def parsing_weekday(input_weekday):
    for prefix in weekday_prefix:
        if input_weekday.find(prefix) != -1:
            weekday = weekday_map[(input_weekday.split(prefix)[-1])]
            aDate = datetime.date.today()

            if input_weekday[0] == '下':
                aDate = aDate + datetime.timedelta(days=(7 - aDate.weekday()))

            # get next weekday
            while aDate.weekday() != weekday:
                aDate = aDate + datetime.timedelta(days=1)
                pass
            return aDate
    return None

def get_date(input_string):
    input_string = input_string.split('/')
    try:
        aDate = datetime.date(datetime.date.today().year, int(input_string[0]), int(input_string[1]))
        if aDate < datetime.date.today():
            aDate = datetime.date(datetime.date.today().year+1, int(input_string[0]), int(input_string[1]))
        return aDate
    except:
        return None

def parsing_date(input_string):
    date_string = match_pattern(date_pat, input_string)
    date_list = []
    if date_string:
        setting_date = datetime.date.today()

        match = re.search(month_day_pat, date_string)
        if match:
            match = re.search(month_day_range_pat, date_string)
            if match:
                split_string = match.group().split('-')
                start_date = get_date(split_string[0])
                end_date = get_date(split_string[1])

                if start_date and end_date:
                    while start_date <= end_date:
                        if start_date.weekday() <= 4:
                            date_list.append(start_date)
                        start_date = start_date + datetime.timedelta(days=1)
                        pass
            else:
                setting_date = get_date(date_string)
                if setting_date and setting_date.weekday() <= 4:
                    date_list.append(setting_date)
        else:
            # descripted date
            if date_string == '明天':
                setting_date = setting_date + datetime.timedelta(days=1)
            elif date_string == '後天':
                setting_date = setting_date + datetime.timedelta(days=2)
            else:
                setting_date = parsing_weekday(date_string)

            if setting_date and setting_date.weekday() <= 4:
                date_list.append(setting_date)

    return date_list


def isTakeoffReq(input_string):
    return match_pattern([takeoff_pat], input_string)

def parsing_takeoff_string(input_string):
    if isTakeoffReq(input_string):
        return parsing_date(input_string)
    return None

if __name__ == "__main__":
    for item in test_items:
        print("{0} => {1}".format(item, parsing_takeoff_string(item)))