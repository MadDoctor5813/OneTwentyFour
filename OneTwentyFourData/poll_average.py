import csv
import datetime
import math

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
    
#various constants for the weighted average

#the number of polls we take into account for the weighted average
MAX_POLLS = 6

def weight(poll, poll_idx):
    if poll_idx <= MAX_POLLS:
        return 1
    else:
        return 0

def weighted_average(polls):
    weights = dict()
    weight_sum = 0
    results = dict()
    for idx, poll in enumerate(polls):
        poll_weight = weight(poll, idx)
        weight_sum += poll_weight
        weights[poll] = poll_weight
    for poll in polls:
        for party, result in poll.results.items():
            if party not in results:
                results[party] = 0
            results[party] += result * weights[poll]
    for party, result in results.items():
        results[party] /= weight_sum
    return results


polls_2011 = load_polls('data/2011/op_polls/op_polls.csv')
polls_2014 = load_polls('data/2014/op_polls/op_polls.csv')

predicted_2011 = weighted_average(polls_2011)
predicted_2014 = weighted_average(polls_2014)

print(predicted_2011)
print(predicted_2014)

errors = list()

for party, result in predicted_2011.items():
    errors.append(result - FINAL_2011[party])

for party, result in predicted_2014.items():
    errors.append(result - FINAL_2014[party])

avg_error = sum(errors) / len(errors)

avg_diff = 0
for error in errors:
    avg_diff += (error - avg_error) ** 2
  
std_dev = math.sqrt(avg_diff / len(errors))
print(avg_error)
print(std_dev)