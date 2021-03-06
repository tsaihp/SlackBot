# coding:utf-8

#
# Parsing a string of taking off to datetime object
# Athor: Ethan Tsai
# Date: 2016/12/14
#

import re
import datetime

month_day_pat = r'\d+/\d+'
month_day_range_pat = r'\d+/\d+-\d+/\d+'

afterday_pattern = r'(?P<afterday>[明後]天)'
weekday_pattern = r'(?P<next>下*)(?P<week>禮拜|星期|週)(?P<weekday>一|二|三|四|五)'
month_day_pattern = r'(?P<monthday>\d+/\d+)'

date_pattern_spec = [
    ('AFTERDAY', r'[明後]天'),
    ('WEEKDAY', r'(下*)(禮拜|星期|週)(一|二|三|四|五)'),
    ('MONTHDAY', r'\d+/\d+'),
    ('TIME', r'(早上|[上下]午)'),
    ('FROMTO', r'-'),
    ('AND', r'(,|和)'),
    ('END', r'NOTHING'),
]

date_pat = [
    '明天',
    '後天',
    r'\w*禮拜.',
    r'\w*星期.',
    r'\w*週.',
    month_day_range_pat,
    month_day_pat
]

time_pat = ['早上', '[上下]午']
takeoff_pat = r'請\w*假'

test_items = [
    '我明天請假',
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
    '11/31請假',
    '我今天想請假',
    '今天誰請假',
    '明天早上請假, 下禮拜一下午請假',
    '下禮拜一和禮拜三請假',
    '下禮拜一早上和禮拜三下午請假'
]

weekday_prefix = ['禮拜', '星期', '週']

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


def parsing_time(input_time):
    time_string = match_pattern(time_pat, input_time)
    if time_string == '早上' or time_string == '上午':
        return 'morning'
    elif time_string == '下午':
        return 'afternoon'
    else:
        return 'wholeday'


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
        aDate = datetime.date(
            datetime.date.today().year,
            int(input_string[0]),
            int(input_string[1])
        )
        if aDate < datetime.date.today():
            aDate = datetime.date(
                datetime.date.today().year + 1,
                int(input_string[0]),
                int(input_string[1])
            )
        return aDate
    except:
        return None


def parsing_monthday(input_string):
    return get_date(input_string)


def parsing_afterday(input_string):
    setting_date = datetime.date.today()

    if input_string == '明天':
        setting_date = setting_date + datetime.timedelta(days=1)
    elif input_string == '後天':
        setting_date = setting_date + datetime.timedelta(days=2)
    else:
        setting_date = None

    return setting_date


def parsing_takeoff_req(input_string):
    date_time_pattern = '|'.join('(?P<%s>%s)' %
                                 pair for pair in date_pattern_spec)
    takeoff_date = None
    takeoff_time = ''

    range_start = None
    range_exist = False

    date_list = []

    # 1st layer
    for mo in re.finditer(date_time_pattern, input_string):
        kind = mo.lastgroup
        value = mo.group(kind)
        # print('%s => %s' % (kind, value))

        if kind == 'AFTERDAY':
            takeoff_date = parsing_afterday(value)
        elif kind == 'WEEKDAY':
            takeoff_date = parsing_weekday(value)
        elif kind == 'MONTHDAY':
            takeoff_date = parsing_monthday(value)
        elif kind == 'TIME':
            takeoff_time = parsing_time(value)
        elif kind == 'FROMTO':
            # print ('%s => %s' % (kind, value))
            if takeoff_date:
                range_start = takeoff_date
                range_exist = True
            else:
                return []
        elif kind == 'AND':
            # print ('%s => %s' % (kind, value))
            date_list.append({'date': takeoff_date, 'time': takeoff_time})

    if takeoff_time == '':
        takeoff_time = 'wholeday'

    if range_exist and range_start:
        while range_start <= takeoff_date:
            if range_start.weekday() <= 4:
                date_list.append({'date': range_start, 'time': takeoff_time})
            range_start = range_start + datetime.timedelta(days=1)
            pass
        range_exist = False
        range_start = None
    elif takeoff_date and takeoff_date.weekday() <= 4:
        date_list.append({'date': takeoff_date, 'time': takeoff_time})

    return date_list


def isTakeoffQuery(input_string):
    if match_pattern(["誰" + takeoff_pat], input_string):
        return True
    return False


def isTakeoffReq(input_string):
    pattern = '\w*'
    pattern += '|'.join('(?P<%s>%s)' % pair for pair in date_pattern_spec)
    pattern += takeoff_pat
    match = re.match(pattern, input_string)
    if match:
        return True
    return False


def parsing_takeoff_string(input_string):
    if isTakeoffQuery(input_string):
        return 'query'

    if isTakeoffReq(input_string):
        return parsing_takeoff_req(input_string)
    return None


if __name__ == "__main__":
    for item in test_items:
        print("{0} => {1}".format(item, parsing_takeoff_string(item)))
