import fiona
import shapely
from shapely.geometry import Polygon, shape
import rtree
import pprint
import timeit

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

with fiona.open('data/2018/districts/districts.shp') as ridings_file_2018:
    #load in the 2018 ridings
    start = timeit.time.time()
    ridings_2018 = dict()
    riding_index = rtree.index.Index()
    for riding_record in ridings_file_2018:
        riding = Riding()
        riding.name = riding_record['properties']['ENGLISH_NA']
        riding.id = riding_record['properties']['ED_ID']
        riding.shape = shape(riding_record['geometry'])
        ridings_2018[riding.id] = riding
        riding_index.add(riding.id, riding.shape.bounds)
    assign_poll_weights(ridings_2018, riding_index)
    print('Poll weights assigned.')
    assign_riding_weights(ridings_2018, riding_index)
    print('Riding weights assigned.')
    end = timeit.time.time()
    print('Took ' + str(end - start) + ' seconds.')
  