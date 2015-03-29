#!/usr/bin/python

import sys
import json
from optparse import OptionParser

sys.path.append('..')

import plot_travel_times as ptt

def main():
    usage = """
    python create_grid.py all_connections_x.csv

    Calculate an y x y grid for the travel times in the entire region.
    """
    num_args= 1
    parser = OptionParser(usage=usage)

    parser.add_option('-r', '--resolution', dest='resolution', default=4, 
            help="The resolution we want the grid to be at", type='int')
    parser.add_option('-o', '--output-file', dest='output_file', default=None,
            help="A file to dump the output to", type='str')
    parser.add_option('-d', '--old', dest='old', action='store_true', default=False,
            help='Use old grid function')
    parser.add_option('', '--min-x', dest='min_x', default=None,
            help='The minimum longitude', type='float')
    parser.add_option('', '--max-x', dest='max_x', default=None,
            help='The maximum longitude', type='float')
    parser.add_option('', '--min-y', dest='min_y', default=None,
            help='The minimum latitude', type='float')
    parser.add_option('', '--max-y', dest='max_y', default=None,
            help='The maximum latitude', type='float')

    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    print >>sys.stderr, "res:", options.resolution
    (distances, xs, ys, zs) = ptt.get_connection_coordinates_and_times(args[0])

    
    sys.setrecursionlimit(8500)

    if options.old:
        (grid_x, grid_y, grid_z, min_x, max_x, min_y, max_y) = ptt.create_grid(distances, xs, ys, zs, complex(0, options.resolution))
    else:
        (grid_x, grid_y, grid_z, min_x, max_x, min_y, max_y) = ptt.create_grid2(distances, xs, ys, zs, complex(0, options.resolution), options.min_x, options.max_x, options.min_y, options.max_y)

    if options.output_file is None:
        json.dump({'grid_z':[list(g) for g in grid_z], 'min_x':min_x,
                   'max_x': max_x, 'min_y': min_y, 'max_y': max_y}, sys.stdout)
    else:
        with open(options.output_file, 'w') as f:
            json.dump({'grid_z':[list(g) for g in grid_z], 'min_x': min_x, 
                       'max_x': max_x, 'min_y': min_y, 'max_y': max_y}, f)

if __name__ == '__main__':
    main()
