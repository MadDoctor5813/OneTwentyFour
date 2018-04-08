import fiona
import shapely
from shapely.geometry import Polygon, shape
import rtree
import pprint
import timeit
import csv
import os
import re
import xlrd

"""Applies the 2014 electoral maps and results to the 2018 electoral map.

Methodology:
First, we determine which 2018 ridings each 2014 polling location intersects. If a polling location completely intersects
a riding, all its votes are assigned to the riding. If a location intersects more than one riding, its votes are divide based
on the proportion of the location that lies in each riding.

Advanced polling votes are divided with the same strategy, but based on riding instead of polling location because advanced 
poll votes are only available on a riding scale.
"""

class Poll:
    
    def __init__(self):
        self.riding_id = 0
        self.poll_id = 0

class Riding:

    def __init__(self):
        self.id = 0
        self.name = ''
        self.shape = Polygon()
        self.polls = list()
        self.ridings = list()
        self.results = dict()
        self.percents = dict()
        self.swings = dict()

"""Gets the ridings that intersect a given polling location's shape.
Returns a list of tuples containing the id of the riding, and the total area of their intersection.
"""
def get_intersecting_ridings(poll_shape, ridings_dict, ridings_index):
    intersections = list()
    possible = ridings_index.intersection(poll_shape.bounds)
    for id in possible:
        riding = ridings_dict[id]
        if poll_shape.intersects(riding.shape):
            intersect = poll_shape.intersection(riding.shape)
            intersections.append((id, intersect.area))
    return intersections

"""Assigns weights of 2014 polling locations to 2018 ridings.
"""
def assign_poll_weights(ridings_2018, ridings_index):
    with fiona.open('data/2014/polls/polls.shp') as polls_file_2014:
        for poll_record in polls_file_2014:
            poll = Poll()
            poll.riding_id = poll_record['properties']['ED_ID']
            poll.poll_id = poll_record['properties']['POLL_DIV_1']
            poll_shape = shape(poll_record['geometry'])
            intersecting = get_intersecting_ridings(poll_shape, ridings_2018, ridings_index)
            sum_area = 0
            for intersect in intersecting:
                sum_area += intersect[1]
            for intersect in intersecting:
                riding = ridings_2018[intersect[0]]
                weight = intersect[1] / sum_area
                riding.polls.append((poll, weight))

"""Assign weights of 2014 ridings to the 2018 ridings based on the area of overlap.  This is inaccurate and is used 
only for advanced polls, which have no geographic location and cannot be assigned more precisely.
"""
def assign_riding_weights(ridings_2018, ridings_index):
    with fiona.open('data/2014/districts/districts.shp') as ridings_file_2014:
        for riding_record in ridings_file_2014:
            riding_shape = shape(riding_record['geometry'])
            intersecting = get_intersecting_ridings(riding_shape, ridings_2018, ridings_index)
            sum_area = 0
            for intersect in intersecting:
                sum_area += intersect[1]
            for intersect in intersecting:
                riding = ridings_2018[intersect[0]]
                weight = intersect[1] / sum_area
                riding.ridings.append((riding_record['properties']['ED_ID'], intersect[1] / sum_area))

"""Loads riding data from a given year from the shapefiles.
"""
def load_riding_data(year):
    with fiona.open('data/' + str(year) + '/districts/districts.shp') as ridings_file_2018:
        ridings_2018 = dict()
        riding_index = rtree.index.Index()
        for riding_record in ridings_file_2018:
            riding = Riding()
            riding.name = riding_record['properties']['ENGLISH_NA']
            riding.id = riding_record['properties']['ED_ID']
            riding.shape = shape(riding_record['geometry'])
            ridings_2018[riding.id] = riding
            riding_index.add(riding.id, riding.shape.bounds)
        return ridings_2018, riding_index

"""Loads the list of candidates from the candidates file. Returns a dict of candidates by riding number.
"""
def load_candidate_list():
    with open('data/2014/results/candidates_fixed.csv') as candidate_file:
        candidates = dict()
        reader = csv.reader(candidate_file)
        for line in reader:
            riding_candidates = dict()
            riding_candidates[line[1].upper()] = 'LIB'
            riding_candidates[line[2].upper()] = 'PC'
            riding_candidates[line[3].upper()] = 'NDP'
            candidates[line[0].upper()] = riding_candidates
        return candidates

"""Determines the party assignment of results in a column based on the file header and the list of candidates by riding
and party.
"""
def assign_party_cols(candidates_dict, results_sheet):
    #assign result columns to party
    party_cols = dict()
    #names start at the third column
    col = 3
    while results_sheet.cell_value(1, col) is not '':
        candidate_name = results_sheet.cell_value(1, col)
        if candidate_name in candidates_dict:
            party_cols[col] = candidates_dict[candidate_name]
        else:
            party_cols[col] = 'OTH'
        col += 1
    return party_cols

"""Gets the poll number from a poll name. Returns ADV if the poll is an advanced poll, or None if there was no number found
"""
def get_poll_number(name):
    if name.startswith('ADV'):
        return 'ADV'
    digit_matches = re.findall(r'^\d+', name)
    if len(digit_matches) > 0:
        return int(digit_matches[0])
    else:
        return None

"""Assigns poll results from one row. Usually returns None, but if the row being processed combines its results with another
poll, it will return the name of that poll instead.
"""
def assign_row_results(row, results_sheet, party_cols, riding_results):
    poll_name = results_sheet.cell_value(row, 0)
    poll_number = get_poll_number(poll_name)
    if poll_number is None:
        return
    poll_info_text = results_sheet.cell_value(row, 2)
    #also check the first column because it shows up there sometimes too
    if poll_info_text is '':
        poll_info_text = results_sheet.cell_value(row, 1)
    if poll_info_text is not '':
        if 'COMBINED WITH POLL' in poll_info_text:
            return int(re.findall(r'\d+', poll_info_text)[0])
        if 'NO POLL TAKEN' in poll_info_text:
            return
    row_results = dict()
    for col, party in party_cols.items():
        if row_results.get(party) is None:
            row_results[party] = 0
        row_results[party] += int(results_sheet.cell_value(row, col))
    if riding_results.get(poll_number) is None:
        riding_results[poll_number] = row_results
    else:
        for key in row_results.keys():
            riding_results[poll_number][key] += row_results[key]

"""Loads poll-by-poll results and returns a dict. The dict is keyed by riding id, and the values are also dicts containing
results by poll number, keyed by party descriptor. Some polls are combined with other polling locations. The votes are split
across all combined polls evenly after the fact. Other polls have taken no votes, they are not recorded. Advanced polls do
not appear in the poll shapefiles and are listed under one heading, 'ADV'.
"""
def load_poll_results(ridings_2014, candidates):
    results = dict()
    for result_file_name in os.listdir('data/2014/results/poll_results/'):
        results_sheet = xlrd.open_workbook('data/2014/results/poll_results/' + result_file_name).sheet_by_index(0)
        riding_num = int(re.findall(r'\d+', result_file_name)[0])
        results[riding_num] = dict()
        party_cols = assign_party_cols(candidates[ridings_2014[riding_num].name], results_sheet)
        #WARNING: shady excel parsing past this point
        #poll results start at two
        row = 2
        combined = dict()
        #the poll results end with a totals row
        while results_sheet.cell_value(row, 0) != 'Totals':
            comb_poll = assign_row_results(row, results_sheet, party_cols, results[riding_num])
            if comb_poll is not None:
                if combined.get(comb_poll) is None:
                    combined[comb_poll] = list()
                combined[comb_poll].append(int(re.findall(r'\d+', results_sheet.cell_value(row, 0))[0]))
            row += 1
        #split combined polls back into their original assignments
        for poll, combined in combined.items():
            split_poll_results = results[riding_num][poll]
            for party, result in split_poll_results.items():
                split_poll_results[party] = result / (len(combined) + 1)
            results[riding_num][poll] = split_poll_results
            for combined_poll in combined:
                results[riding_num][combined_poll] = split_poll_results
    return results

def calculate_results(ridings_2018, results):
    for riding in ridings_2018.values():
        riding.results['LIB'] = 0
        riding.results['PC'] = 0
        riding.results['NDP'] = 0
        riding.results['OTH'] = 0
        for poll, weight in riding.polls:
            try:
                poll_results = results[poll.riding_id][poll.poll_id]
            except KeyError:
                #this poll was probably not taken, don't worry about it
                pass
            for party, result in poll_results.items():
                riding.results[party] += result * weight
                if riding.id == 8:
                    print(poll.poll_id)
                    print(party)
                    print(result * weight)
        for riding_id, weight in riding.ridings:
            advanced_results  = results[riding_id]['ADV']
            for party, result in advanced_results.items():
                riding.results[party] += result * weight
                if riding.id == 8:
                    print(party)
                    print(result * weight)

start = timeit.time.time()
ridings_2018, riding_index = load_riding_data(2018)
ridings_2014, _ = load_riding_data(2014)
print('Riding data loaded.')
candidates = load_candidate_list()
print('Candidate list loaded.')
results = load_poll_results(ridings_2014, candidates)
print('2014 results loaded.')
assign_poll_weights(ridings_2018, riding_index)
print('Poll weights assigned.')
assign_riding_weights(ridings_2018, riding_index)
print('Riding weights assigned.')
calculate_results(ridings_2018, results)
print('Results calculated.')
end = timeit.time.time()
print('Took ' + str(end - start) + ' seconds.')
  