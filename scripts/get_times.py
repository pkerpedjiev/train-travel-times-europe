import os.path as op
import random
import sys
import time
import urllib2
import gzip

#!/usr/bin/python

import sys
from optparse import OptionParser

def main():
    usage = """
    python get_times.py from_id to_id

    Get the list of connections from station from_id to station to_id.
    """
    num_args= 2
    parser = OptionParser(usage=usage)

    parser.add_option('-o', '--output-dir', dest='output_dir', default='all_times', help="The directory into which to place the connection times.", type='str')
    parser.add_option('-c', '--check-existing', dest='check_existing', default=False, action='store_true', help='Check if there are existing entries for that station')

    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    url = 'http://transport.opendata.ch/v1/connections?from={}&to={}&date=2015-08-01&time=08:00'.format(args[0], args[1])

    found = False
    to_sleep = 1
    while not found and to_sleep < 2:
        filename = op.join(options.output_dir, '_'.join(args) + ".gz")
        if options.check_existing:
            if op.exists(filename):
                sys.stdout.write("exists... {}\n".format(filename))
                return
        try:
            u = urllib2.urlopen(url, timeout=60)
            sys.stdout.write('_'.join(args) + "\n")
            with gzip.open(filename, 'w') as f:
                f.write(u.read())
            sys.stdout.flush()
            found = True
        except Exception as ex:
            #print sys.stderr, "Exception:", ex
            print "sleeping...", to_sleep
            time.sleep(to_sleep)
            to_sleep *= 2

    if not found:
        sys.stdout.write('x_' + "_".join(args))
        print >>sys.stderr, "not_found:", args[0], args[1]

if __name__ == '__main__':
    main()

