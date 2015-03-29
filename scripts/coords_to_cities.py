#!/usr/bin/python

import datetime as dt
import re
import sys
import json
import urllib2
from optparse import OptionParser

def main():
    usage = """
    python coords_to_cities.py grid_100.json
    """
    num_args= 1
    parser = OptionParser(usage=usage)

    #parser.add_option('-o', '--options', dest='some_option', default='yo', help="Place holder for a real option", type='str')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)
    
    with open(args[0], 'r') as f:
        coords = json.load(f)[:20]
        out_jsons = []

        for xy in coords:
            x = xy['x']
            y = xy['y']

            url = "http://maps.googleapis.com/maps/api/geocode/json?latlng={},{}&sensor=false".format(y, x)
            u = urllib2.urlopen(url)
            result_json = json.load(u)

            if len(result_json['results']) > 0:
                for result in result_json['results']:
                    if "types" in result:
                        if "administrative_area_level_1" in result["types"]:
                            print result['formatted_address']

            #print result_json
            
if __name__ == '__main__':
    main()
