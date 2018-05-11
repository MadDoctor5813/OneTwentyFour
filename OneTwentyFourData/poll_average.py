import csv
import datetime

FINAL_2014 = {
    'LIB' : 38.65,
    'PC' : 31.25,
    'NDP': 23.75,
    'OTH' : 6.35
}

DATE_2014 = datetime.date(2014, 6, 12)

FINAL_2011 = {
    'LIB' : 37.65,
    'PC' : 35.45,
    'NDP' : 22.74
}

DATE_2011 = datetime.date(2011, 10, 6)

class Poll:

    def __init__(self):
        self.pollster = ''
        self.date = None
        self.type = ''
        self.results = dict()
        self.margin_of_error = 0
        self.sample_size = 0

def load_polls(file):
    polls = list()
    with open(file, 'r') as poll_file:
        for row in csv.reader(poll_file):
            row_poll = Poll()
            row_poll.pollster = row[0]
            row_poll.date = datetime.datetime.strptime(row[1], '%Y-%m-%d')
            row_poll.results['LIB'] = float(row[2])
            row_poll.results['PC'] = float(row[3])
            row_poll.results['NDP'] = float(row[4])
            row_poll.type = row[6]
            row_poll.margin_of_error = float(row[7])
            polls.append(row_poll)
    return polls
            

polls_2011 = load_polls('data/2011/op_polls/op_polls.csv')
polls_2014 = load_polls('data/2014/op_polls/op_polls.csv')
print(polls_2011)
