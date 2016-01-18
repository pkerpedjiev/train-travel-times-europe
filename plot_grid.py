#!/usr/bin/python

import sys
from optparse import OptionParser

import plot_travel_times as ptt

def fix_grid(grid):
    return grid
    sorted_vals = sorted(np.array(grid).ravel())
    max_val = min(sorted_vals[len(sorted_vals)/20:])
    new_grid = [[max_val if x < max_val else x for x in g] for g in grid]
    return new_grid

import json
import numpy as np
import os.path as op

def main():
    usage = """
    usage
    """
    num_args= 1
    parser = OptionParser(usage=usage)

    #parser.add_option('-o', '--options', dest='some_option', default='yo', help="Place holder for a real option", type='str')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    parser.add_option('-o', '--output-dir', dest='output_dir', default='.', 
            help='the directory into which to place the images', type='str')
    parser.add_option('-s', '--show-plot', dest='show_plot', default=False, 
            action='store_true', help='show the plot')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    filename = args[0]
    output_filename = op.join(options.output_dir, op.splitext(op.basename(filename))[0] + ".png")

    print >>sys.stderr, "output_filename:", output_filename

    with open(filename, 'r') as f:
        grid = json.load(f)

    cont = ptt.plot_map_grid(np.array(fix_grid(grid['grid_z'])),
                               grid['min_x'], grid['max_x'], grid['min_y'], grid['max_y'],
                               filename=output_filename, showgrid=options.show_plot)

if __name__ == '__main__':
    main()

