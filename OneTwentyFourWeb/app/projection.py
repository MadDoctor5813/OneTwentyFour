class Projection:

    def __init__(self):
        self.seats = dict()
        self.result = None
        self.riding_projections = dict()

def find_party_max(party_dict):
    return max(party_dict.items(), key=lambda x: x[1])[0]

def project(all_ridings, poll_average):
    projection = Projection()
    projection.seats['LIB'] = 0
    projection.seats['PC'] = 0
    projection.seats['NDP'] = 0
    projection.seats['OTH'] = 0
    for riding in all_ridings:
        riding_results = dict()
        for party, swing in riding.swings.items():
            riding_results[party] = swing + poll_average.current[party]
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