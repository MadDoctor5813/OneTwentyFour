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
                riding.polls.append((poll, intersect[1] / sum_area))

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
                riding.ridings.append((riding_record['properties']['ED_ID'], intersect[1] / sum_area))

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

def load_candidate_list():
    with open('data/2014/results/candidates.csv') as candidate_file:
        candidates = dict()
        reader = csv.reader(candidate_file)
        #skip header
        next(reader)
        for line in reader:
            riding_candidates = dict()
            riding_candidates[line[1].upper()] = 'LIB'
            riding_candidates[line[2].upper()] = 'PC'
            riding_candidates[line[3].upper()] = 'NDP'
            candidates[line[0].upper()] = riding_candidates
        return candidates

def load_poll_results(ridings_2014, candidates):
    for result_file_name in os.listdir('data/2014/results/poll_results/'):
        results = xlrd.open_workbook('data/2014/results/poll_results/' + result_file_name).sheet_by_index(0)
        riding_num = int(re.findall(r'\d+', result_file_name)[0])
        #assign result columns to party
        party_cols = dict()
        #names start at the third column
        col = 3
        while results.cell_value(1, col) is not '':
            candidate_name = results.cell_value(1, col)
            candidate_list = candidates[ridings_2014[riding_num].name].items()
            for candidate in candidate_list:
                if candidate_name in candidate[0]:
                    party_cols[col] = candidate[1]
                    break
            #if we haven't found a match assign it to other
            if col not in party_cols.keys():
                party_cols[col] = 'OTH'
            col += 1
        if 'LIB' not in party_cols.values() or 'NDP' not in party_cols.values() or 'PC' not in party_cols.values():
            print(ridings_2014[riding_num].name)
            print(riding_num)
    return 1

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
end = timeit.time.time()
print('Took ' + str(end - start) + ' seconds.')
  