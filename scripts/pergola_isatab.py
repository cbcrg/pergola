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

def main():
    parser = ArgumentParser(parents=[parsers.parser])
    
    args = parser.parse_args()
    
    print >> stderr, "@@@Pergola_isatab.py: Input file: %s" % args.input 
    print >> stderr, "@@@Pergola_isatab.py: Configuration file: %s" % args.ontology_file
    print >> stderr, "@@@Pergola_isatab.py: Selected tracks are: ", args.tracks

#Make a function that retrieves files in isatab table and return it as a dictionary
    
#hacer una funcion que recoja todos los archivos del isatab y los meta en un diccionario

if __name__ == '__main__':
    exit(main())