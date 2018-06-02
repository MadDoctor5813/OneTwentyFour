import random
import json
from collections import Counter

class Projection:

    def __init__(self):
        self.seats = dict()
        self.result = None
        self.riding_projections = dict()

def find_party_max(party_dict):
    return max(party_dict.items(), key=lambda x: x[1])[0]

#taken from poll_avg.py
ERROR_AVG = -0.35071428571428775
STD_DEV = 1.2474828397112945

NUM_SIMULATIONS = 500

def project_random_outcomes(all_ridings, poll_average):
    seat_outcomes = dict()
    minorities = Counter()
    majorities = Counter()
    for i in range(NUM_SIMULATIONS):
        outcome = project_with_error(all_ridings, poll_average)
        for party, seats in outcome.seats.items():
            if seat_outcomes.get(party) is None:
                seat_outcomes[party] = Counter()
            seat_outcomes[party][seats] += 1
        if outcome.result[0] == 'minority':
            minorities[outcome.result[1]] += 1
        elif outcome.result[0] == 'majority':
            majorities[outcome.result[1]] += 1
    #convert the seat_outcomes back into a dict for serialization
    for party, counter in seat_outcomes.items():
        seat_outcomes[party] = dict(seat_outcomes[party])
    #convert minorities and majorities into percentages
    maj_sum = sum(majorities.values())
    maj_percent = dict()
    for party, count in majorities.items():
        maj_percent[party] = (count / maj_sum) * 100
    min_sum = sum(minorities.values())
    min_percent = dict()
    for party, count in minorities.items():
        min_percent[party] = (count / min_sum) * 100
    return (seat_outcomes, maj_percent, min_percent)

def project_with_error(all_ridings, poll_average):
    adjusted = dict()
    for party, average in poll_average.items():
        adjusted[party] = average + random.gauss(ERROR_AVG, STD_DEV)
    return project(all_ridings, adjusted)

def project(all_ridings, poll_average):
    projection = Projection()
    projection.seats['LIB'] = 0
    projection.seats['PC'] = 0
    projection.seats['NDP'] = 0
    projection.seats['OTH'] = 0
    for riding in all_ridings:
        riding_results = dict()
        for party, swing in riding.swings.items():
            riding_results[party] = swing + poll_average[party]
        min_result = min(riding_results.values())
        if min_result < 0:
            #we have a negative result, do some adjustment
            adjusted_sum = 0
            for party, result in riding_results.items():
                riding_results[party] = riding_results[party] + (-min_result)
                adjusted_sum += riding_results[party]
            for party, result in riding_results.items():
                riding_results[party] *= (100 / adjusted_sum)
        projection.riding_projections[riding.riding_id] = riding_results
        winner = find_party_max(riding_results)
        projection.seats[winner] += 1
    winning_party = find_party_max(projection.seats)
    if projection.seats[winning_party] >= 63:
        projection.result = ('majority', winner, projection.seats[winner])
    else:
        projection.result = ('minority', winner, projection.seats[winner])
    return projection