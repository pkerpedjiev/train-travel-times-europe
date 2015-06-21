#!/usr/bin/python

import collections as col
import dateutil.parser as dp
import gzip
import itertools as it
import json
import os
import os.path as op
import sys
from optparse import OptionParser
from math import radians, cos, sin, asin, sqrt

cities_to_trains = {}
stretches_to_times = {}

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    
    Courtesy of:
    
    http://stackoverflow.com/a/4913653/899470
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 

    # 6371 km is the radius of the Earth
    km = 6371 * c

    return km 

def merge_journeys(pl1, pl2):
    '''
    Merge two journeys.

    The journeys have to have the same name.
    '''
    pl1_stations = [s['station']['id'] for s in pl1]
    pl2_stations = [s['station']['id'] for s in pl2]

    if len(pl1_stations) > len(pl2_stations):
        return pl1
    else:
        return pl2

    departures = col.defaultdict(lambda: None)
    arrivals = col.defaultdict(lambda: None)
    stations = col.defaultdict(lambda: None)

    for pl in it.chain(pl1, pl2):
        if pl['departure'] is not None:
            departures[pl['station']['id']] = pl['departure']

        if pl['arrival'] is not None:
            arrivals[pl['station']['id']] = pl['arrival']

        stations[pl['station']['id']] = pl

    pl = set(pl1_stations + pl2_stations)

    def pass_list_sort(a, b):
        '''
        Sort a pass list based on the departure and arrival 
        times.
        '''
        da = departures[a]
        db = departures[b]

        if da is None:
            return -1
        if db is None:
            return 1

        return int((dp.parse(da) - dp.parse(db)).total_seconds())

    pl = list(pl)
    pl.sort(pass_list_sort)

    newPl = []
    for sid in pl:
        stations[sid]['departure'] = departures[sid]
        stations[sid]['arrival'] = arrivals[sid]

        newPl += [stations[sid]]

    return newPl

def journey_to_tsv(pl, jname):
    '''
    Update the details of an existing journey
    '''

    for f, t in zip(pl, pl[1:]):
        if f['departure'] is None or t['arrival'] is None:
            continue

        from_lat = float(f['station']['coordinate']['x'])
        from_lon = float(f['station']['coordinate']['y'])

        to_lat = float(t['station']['coordinate']['x'])
        to_lon = float(t['station']['coordinate']['y'])

        dist = haversine(from_lon, from_lat, to_lon, to_lat)

        tf = dp.parse(f['departure'])
        tt = dp.parse(t['arrival'])

        elapsed_time = tt - tf
        try:
            output_data =  [jname, f['station']['name'], t['station']['name'], 
                int(3600 * dist / (elapsed_time.total_seconds() + 60)),
                int(dist), tf, elapsed_time, 
                from_lat, from_lon, to_lat, to_lon]
            print u"\t".join(map(unicode, output_data)).encode('utf-8')
        except ZeroDivisionError as zde:
            print "ZeroDivisionError:", elapsed_time.total_seconds()

def parse_sections(filename, existing_journeys=None):
    if existing_journeys is None:
        existing_journeys = col.defaultdict(dict)

    if not op.exists(filename):
        print >>sys.stderr, "Not found:", filename
        return existing_journeys

    with gzip.open(filename, 'r') as f:
        try:
            data = json.loads(f.read())
        except ValueError as ve:
            print >>sys.stderr, "Error decoding JSON:", filename
            return existing_journeys

        for connection in data['connections']:
            if 'sections' not in connection:
                continue

            for section in connection['sections']:
                if 'journey' in section:
                    journey = section['journey']

                    if journey is None:
                        continue

                    jname =  u"{} [{}]".format(journey['name'], journey['operator'])

                    if jname == 'ICE 102':
                        #print >>sys.stderr, "Journey", json.dumps(journey, indent=2)
                        print >>sys.stderr, journey['name'], journey['number'], journey['operator']

                    try:
                        if jname not in existing_journeys:
                            existing_journeys[jname] = journey['passList']
                        else:
                            existing_journeys[jname] = merge_journeys(existing_journeys[jname], journey['passList'])
                    except Exception as ex:
                        print >>sys.stderr, json.dumps(journey, indent=2)
                        with open('err.txt', 'w') as f1:
                            f1.write(json.dumps(existing_journeys))
                        print >>sys.stderr,  "Exception, filename:", filename, "ex:", ex

                        sys.exit(1)

    return existing_journeys

def main():
    usage = """
    python parse_sections file_list.txt
    """
    num_args= 0
    parser = OptionParser(usage=usage)

    #parser.add_option('-o', '--options', dest='some_option', default='yo', help="Place holder for a real option", type='str')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')
    parser.add_option('-l', '--file-list', dest='file_list', default=False, action='store_true', help='The input is actually a file containing a list of files')
    parser.add_option('-p', '--prefix', dest='prefix', default='.', help='A prefix path for the file list. Must be used in conjuction with the -l option', type='str')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)


    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    existing_journeys = {}

    if options.file_list:
        if args[0] == '-':
            f = sys.stdin
        else:
            f = open(args[0], 'r')

        for line in f:
            fn = op.join(options.prefix, line.strip())
            existing_journeys = parse_sections(fn, existing_journeys=existing_journeys)
    else:
        for arg in args:
             existing_journeys = parse_sections(arg, existing_journeys=existing_journeys)    

    tsvs = []
    print u"\t".join(["janme", "from", "to", "speed", 
        "dist", "time_from", "elapsed_time", 
        "from_lat", "from_lon", "to_lat", "to_lon"])

    for jname in existing_journeys:
        journey_to_tsv(existing_journeys[jname], jname)

if __name__ == '__main__':
    main()

