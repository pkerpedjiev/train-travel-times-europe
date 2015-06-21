#!/usr/bin/python

import gzip
import sys
from optparse import OptionParser

def main():
    usage = """
    python grep_for_name_in_file_list.py file_list.lst [term]

    Search for a term in a list of files.
    """
    num_args= 2
    parser = OptionParser(usage=usage)

    #parser.add_option('-o', '--options', dest='some_option', default='yo', help="Place holder for a real option", type='str')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    if args[0] == '-':
        f = sys.stdin
    else:
        f = open(args[0], 'r')

    for line in f:
        with gzip.open(line.strip(), 'r') as f1:
            found = False
            for line1 in f1:
                if found:
                    break

                if line1.find(args[1]) >= 0:
                    print line.strip()
                    found = True


if __name__ == '__main__':
    main()

