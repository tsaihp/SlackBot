# coding:utf-8

#
# User object
# Athor: Ethan Tsai
# Date: 2017/1/3
#

import csv


class slackuser(object):

    def __init__(self, slack_id, slack_name, weekly_name, lvl):
        self.id = slack_id
        self.name = slack_name
        self.weekly_name = weekly_name
        self.lvl = lvl

    def __eq__(self, that):
        if not isinstance(that, slackuser):
            return False
        return self.id == that.id and self.name == that.name

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return self.name

    def isMaster(self):
        if self.lvl == 'master':
            return True
        else:
            return False

    def isManager(self):
        if self.lvl == 'manager':
            return True
        else:
            return False


class slackuserdict(object):

    def __init__(self, csvfile_name):
        self.user_list = {}

        with open(csvfile_name) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.user_list[row['slack_id']] = slackuser(
                    row['slack_id'],
                    row['slack_name'],
                    row['weekly_name'],
                    row['lvl'])

    def get_username_by_id(self, slack_id):
        if slack_id in self.user_list:
            return self.user_list[slack_id].name

    def get_weeklyname_by_id(self, slack_id):
        if slack_id in self.user_list:
            return self.user_list[slack_id].weekly_name

    def get_user(self, slack_id):
        if slack_id in self.user_list:
            return self.user_list[slack_id]
        else:
            return None


if __name__ == "__main__":
    list = slackuserdict('users.csv')
    for user in list.user_list:
        print(
            user,
            list.get_username_by_id(user),
            list.get_weeklyname_by_id(user)
        )
