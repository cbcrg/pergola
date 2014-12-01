#!/usr/bin/env python

"""
26 Nov 2014

Script to run pergola from the command line using isatab format
"""

sp = " "

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
    
#     print ("pergola_rules.py" + sp + "-i" + sp + file + sp + "-o" + sp + args.ontology_file + sp +
#                        track_actions + sp + dataTypes_actions + 
#                        sp + format + sp + relative_coord + sp + 
#                        multiply_factor + sp + fields_read) 
    
    relative_coord = ""
    track_actions = ""
    dataTypes_actions = ""
    format = ""
    multiply_factor = ""
    fields_read = ""
    
    if args.relative_coord:
        relative_coord = "-e"
        
    if args.track_actions:
        track_actions = "-a " + args.track_actions
    
    if args.dataTypes_actions:
        dataTypes_actions = "-d " + args.dataTypes_actions
    
    if args.format:
        format = "-f " + args.format
    
    if args.multiply_factor:
        multiply_factor = "-f " + args.multiply_factor
        
    if args.fields_read: 
        fields_read = "-m " + args.fields_read
                
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
#                 print "file is :", file
                print ("")
                print ("pergola_rules.py" + sp + "-i" + sp + file + sp + "-o" + sp + args.ontology_file + sp +
                       track_actions + sp + dataTypes_actions + 
                       sp + format + sp + relative_coord + sp + 
                       multiply_factor + sp + fields_read) 
#                 os.system("pergola_rules.py")


# parser.add_argument('-a', '--track_actions', required=False, choices=_tr_act_options,
#                     help='Option of action with tracks selected, split_all, join_all,' + \
#                          ' join_odd, join_even, join_range or join_list')
# parser.add_argument('-d', '--dataTypes_actions', required=False, choices=_dt_act_options,
#                     help='Unique values of dataTypes field should be dumped on' + \
#                          ' different data structures or not')
# parser.add_argument('-f', '--format', required=False, type=str, 
#                     help='Write file output format (bed or bedGraph)')
# parser.add_argument('-e', '--relative_coord', required=False, action='store_true', 
#                     default=False, help='Sets first timepoint' \
#                     ' to 0 and make all the others relative to this timepoint')
# parser.add_argument('-n', '--intervals_gen', required=False, action='store_true', 
#                     default=False, help='Set startChrom and endChrom from just a timepoint in the file' \
#                                         'using field set as startChrom')
# parser.add_argument('-m', '--multiply_factor', metavar='N', type=int, required=False,
#                     help='Multiplies value in dataValue by the given value')
# parser.add_argument('-s', '--fields_read', metavar='FIELDS2READ', type=str, nargs='+',
#                     help='List of fields to read from input file')



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