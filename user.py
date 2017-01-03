# coding:utf-8

#
# User object
# Athor: Ethan Tsai
# Date: 2017/1/3
#


class slackuser(object):

    def __init__(self, slack_id, slack_name):
        self.id = slack_id
        self.name = slack_name

    def __eq__(self, that):
        if not isinstance(that, slackuser):
            return False
        return self.id == that.id and self.name == that.name

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return self.name

    def get_username(self):
        return self.name


class slackuserlist(object):

    pass
