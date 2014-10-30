#!/usr/bin/env python

"""
30 oct 2014

Script to run pergola from the command line
"""

from re       import match
from pergola  import structures
from argparse import ArgumentParser, ArgumentTypeError
import os


def main():
    parser = ArgumentParser(description = 'Script to transform behavioral data into GB readable data')
    parser.add_argument('-i','--input', help='Input file path', required=True, metavar="PATH")

    args = parser.parse_args()
    
    print("Input file: %s" % args.input )
    
def parseNumRange(string):
    m = re.match(r'(\d+)(?:-(\d+))?$', string)

    if not m:
        raise ArgumentTypeError("'" + string + "' is not a range of number. Expected '0-5' or '2'.")
    start = m.group(1)
    end = m.group(2) or start
    list_range=list(range(int(start,10), int(end,10)+1))
    set_range=set(['{0}'.format(t) for t in list_range]) #str because track can be set in the form of track_1 for instance
    
    return set_range

if __name__ == '__main__':
    exit(main())