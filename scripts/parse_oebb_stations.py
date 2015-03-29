
#!/usr/bin/python

import datetime as dt
import re
import sys
import time
import json
import urllib2
from optparse import OptionParser

def main():
    usage = """
    python parse_oebb_stations.py oebb_stations.sql

    Parse the stations file from Fred Schultthze
    """
    num_args= 1
    parser = OptionParser(usage=usage)

    parser.add_option('-a', '--after-id', dest='after_id', default=None, help="Start after ID", type='str')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    with open(args[0], 'r') as f:
        rex = re.compile("\([\d]+?, (?P<oebb_id>[\d]+?), \'.*?\', [\d]+?, \'.*?\', [\d]+?, \'.*?\', \'(?P<station>.+?)\', [\d]+?, (?P<x>[-]?[\d]+?), (?P<y>[-]?[\d]+?)\)")

        output_data = []
        started = False
        
        for line in f:
            m = rex.match(line)

            if m:
                if not started:
                    if options.after_id is not None:
                        if m.group('oebb_id') == options.after_id:
                            started = True
                        else:
                            continue

                sleep_time = 1.
                gotten = False

                while not gotten:
                    try:
                        time.sleep(sleep_time)

                        url = "http://transport.opendata.ch/v1/locations?x={}&y={}".format(float(m.group("y")) / 1000000., float(m.group("x")) / 1000000.)
                        u = urllib2.urlopen(url)
                        js = json.load(u)
                        gotten = True
                    except urllib2.HTTPError as he:
                        print >>sys.stderr, "sleeping...", sleep_time, m.group("x"), m.group("y"), he
                        sleep_time *= 2

                        if sleep_time > 20:
                            break

                if not gotten:
                    continue

                if 'stations' in js:
                    if len(js['stations']) > 0:
                        station = js['stations'][0]
                        output_data += [u"{}\t{}\t{}\t{}\t{}".format(m.group("oebb_id"), station['id'], station['name'], station['coordinate']['x'], station['coordinate']['y']).encode('utf-8')]

                        print output_data[-1]
                        sys.stderr.write('.')
                    else:
                        print >>sys.stderr, "Empty station", m.group("station")
                else:
                    print >> sys.stderr, "No stations in result", m.group("station")

                sys.stdout.flush()
                sys.stderr.flush()


if __name__ == '__main__':
    main()
