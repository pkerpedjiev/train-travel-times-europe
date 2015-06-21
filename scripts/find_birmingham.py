import gzip
import sys

f = gzip.open(sys.argv[1], 'r')

for line in f:
    if line.lower().find("birmingham") >= 0:
        print line
