#!/usr/bin/python

import json
import plot_travel_times as ptt

import sys
from optparse import OptionParser

def main():
    usage = """
    python area_reachable_in_time grid.json time_in_seconds

    Approximate the area that is reachable in an amount of time.
    """
    num_args= 2
    parser = OptionParser(usage=usage)

    #parser.add_option('-o', '--options', dest='some_option', default='yo', help="Place holder for a real option", type='str')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    with open(args[0], 'r') as f:
        grid = json.load(f)

    res_x = len(grid['grid_z'])
    res_y = len(grid['grid_z'][0])

    time_limit = float(args[1])

    area = 0

    for i in range(res_x):
        for j in range(res_y):

            if grid['grid_z'][i][j] < time_limit:
                lon1 = grid['min_x'] + i * (grid['max_x'] - grid['min_x']) / res_x
                lon2 = grid['min_x'] + (i+1) * (grid['max_x'] - grid['min_x']) / res_x

                lat1 = grid['min_x'] + j * (grid['max_y'] - grid['min_y']) / res_y
                lat2 = grid['min_x'] + (j+1) * (grid['max_y'] - grid['min_y']) / res_y

                '''
                print >>sys.stderr, "lat_width:", (grid['max_x'] - grid['min_x']) / res_x
                print >>sys.stderr, "lon1", lon1, "lon2:", lon2
                print >>sys.stderr, "lat1", lat1, "lat2:", lat2
                '''

                width = ptt.haversine(lon1, (lat1 + lat2) / 2., lon2, (lat1 + lat2) / 2.)
                height = ptt.haversine((lon1+lon2) / 2., lat1, (lon1+lon2) / 2, lat2)

                '''
                print >>sys.stderr, "width:", width
                print >>sys.stderr, "height:", height
                '''

                area += width * height
    
    print int(time_limit), int(area)

if __name__ == '__main__':
    main()

