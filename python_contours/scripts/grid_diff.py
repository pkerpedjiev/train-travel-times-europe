#!/usr/bin/python

import json
import numpy as np
import sys
from optparse import OptionParser

def main():
    usage = """
    python grid_diff.py grid1.json grid2.json

    Take the difference of two grids.
    """
    num_args= 2
    parser = OptionParser(usage=usage)

    #parser.add_option('-o', '--options', dest='some_option', default='yo', help="Place holder for a real option", type='str')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    with open(args[0], 'r') as f0:
        with open(args[1], 'r') as f1:
            grid0 = json.load(f0)
            grid1 = json.load(f1)

            assert(grid0['min_x'] == grid1['min_x'])
            assert(grid0['max_x'] == grid1['max_x'])
            assert(grid0['min_y'] == grid1['min_y'])
            assert(grid0['max_y'] == grid1['max_y'])

            new_z = np.array(grid0['grid_z']) - np.array(grid1['grid_z'])
            grid0['grid_z'] = [list(z) for z in new_z]
            
            print json.dumps(grid0)

if __name__ == '__main__':
    main()

