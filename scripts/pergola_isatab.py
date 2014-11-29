#!/usr/bin/env python

"""
26 Nov 2014

Script to run pergola from the command line using isatab format
"""

from pergola import parsers
from pergola  import intervals
from pergola  import mapping
from argparse import ArgumentParser, ArgumentTypeError
from sys      import stderr
import os
from bcbio import isatab

def main():
    parser = ArgumentParser(parents=[parsers.parser])
    
    args = parser.parse_args()
    
    print >> stderr, "@@@Pergola_isatab.py: Input file: %s" % args.input 
    print >> stderr, "@@@Pergola_isatab.py: Configuration file: %s" % args.ontology_file
    print >> stderr, "@@@Pergola_isatab.py: Selected tracks are: ", args.tracks

    #Make a function that retrieves files in isatab table and return it as a dictionary
    isatab_ref = "/home/kadomu/Dropbox/isaTabTools/ISAcreator-1.7.7/isatab files/test2_int2GB"

    # I have to check whether when a isatab folder is given if it is actually a folder or a file
    # difference with -i
    if os.path.isdir(isatab_ref):
        print "Is a directory"
        print "Directory is", args.input 
        #print "directory is ", args.input
#It might be interesting to implement a append option

if __name__ == '__main__':
    exit(main())