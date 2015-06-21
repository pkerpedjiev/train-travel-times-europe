#!/usr/bin/python

import datetime as dt
import gzip
import re
import sys
import json
from optparse import OptionParser

def parse_connections(filename):
    duration_parse = re.compile('(?P<days>[\d]{2})d(?P<hours>[\d]{2}):(?P<minutes>[\d]{2}):(?P<seconds>[\d]{2})')
    with gzip.open(filename, 'r') as f:
        try:
            data = json.loads(f.read())
        except Exception as e:
            print >>sys.stderr, "Error decoding JSON", filename
            return []

        small_data = []
        for connection in data['connections']:
            m = duration_parse.match(connection['duration'])
            total_time = (int(m.group('days')) * (60 * 24) +
                          int(m.group('hours')) * (60) +
                          int(m.group('minutes')))

            #t = dt.datetime.strptime(connection['duration'], "
            small_data += [{"from": connection['from']['station'],
                            "to": connection['to']['station'],
                            "duration" : total_time }]

            if connection['from']['station']['name'].find('Birmingham') >= 0:
                print >>sys.stderr, "birmingham",  small_data

        fastest = sorted(small_data, key=lambda x: x['duration'])
        #print "fastest:", fastest

        if len(fastest) == 0:
            #print >>sys.stderr, "No connections:", filename
            return []

        return [fastest[0]]

def main():
    usage = """
    python parse_connections.py connection_output.json
    """
    num_args= 0
    parser = OptionParser(usage=usage)

    #parser.add_option('-o', '--options', dest='some_option', default='yo', help="Place holder for a real option", type='str')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')
    parser.add_option('-l', '--file-list', dest='file_list', default=False, action='store_true', help='The input is actually a file containing a list of files')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    data = []

    # add a connection to the origin station

    if options.file_list:
        with open(args[0], 'r') as f:
            for line in f:
                data += parse_connections(line.strip())
    else:
        for arg in args:
            data += parse_connections(arg)    

    import copy

    data += [copy.deepcopy(data[-1])]
    data[-1]['to'] = data[-1]['from']
    data[-1]['duration'] = 0

    print >>sys.stderr, "done"
    print json.dumps(data, indent=2)

if __name__ == '__main__':
    main()
