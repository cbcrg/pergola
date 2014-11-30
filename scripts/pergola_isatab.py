#!/usr/bin/env python

"""
26 Nov 2014

Script to run pergola from the command line using isatab format
"""

space = " "

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
#     isatab_ref = "/home/kadomu/Dropbox/isaTabTools/ISAcreator-1.7.7/isatab files/test2_int2GB"

    # I have to check whether when a isatab folder is given if it is actually a folder or a file
    # difference with -i
    if not os.path.isdir(args.input):
        raise ValueError ("Argument input must be a folder containning data in isatab format")
    
    rec = isatab.parse(args.input)
    study= rec.studies[0]
#     print study.nodes.keys() 
    
    #Sample name are the key shared by both study and assay
    
    for i in rec.studies:
#         print "studies are", i
        
        for j in i.assays:
            #print "assays are:", j
            for file in j.nodes.keys():
                print "file is :", file
                print ("")
                print ("pergola_rules.py" + space + "-i" + space + file + space + "-o" + space + args.ontology_file) 
#                 os.system("pergola_rules.py")
#     for i in rec.assays:
#         print "assays", i    
    
    
    
#     for k in study.nodes.keys() :
#         print k
#         node=study.nodes[k]
#         print node.assays.keys()
#         
    nodes=study.nodes
    
#     for node in nodes:
#         print "node------------", node ["Raw Data File"]
        #print "directory is ", args.input
#It might be interesting to implement a append option

if __name__ == '__main__':
    exit(main())