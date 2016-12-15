#!/usr/bin/env python

from pergola import parsers
from argparse import ArgumentParser
from sys      import stderr, exit
import pergola_rules
from os.path import dirname, abspath

# parsers.jaaba_scores_to_csv(input_file='/Users/jespinosa/JAABA_MAC_0.5.1/sampledata_v0.5/Chase1_TrpA_Rig1Plate15BowlA_20120404T141155/scores_chase.mat', 
#                             path_w='/Users/jespinosa/git/pergola/test', norm=True, data_type="chase")

# '/Users/jespinosa/JAABA_MAC_0.5.1/sampledata_v0.5/Chase1_TrpA_Rig1Plate15BowlA_20120404T141155/scores_chase.mat'
# "/Users/jespinosa/git/pergola/sample_data/jaaba_example/scores_chase.mat"
# "/Users/jespinosa/git/pergola/test/jaaba2pergola.txt"
def main(option):
    """
    main function
    """
    print >> stderr,     "@@@jaaba_to_pergola.py: Input file is %s" % args.input 

    path_out = dirname(abspath(args.input))
    parsers.jaaba_scores_to_csv(input_file=args.input, path_w=path_out, norm=True, data_type="chase")
    output_file = path_out + '/' + 'JAABA_scores.csv'
        
    # lo que tengo que hacer es coger el input de jaaba scores to csv
    if option == "p":
        pergola_rules.main(path=output_file, map_file_path=args.mapping_file, sel_tracks=args.tracks, 
              list=args.list, range=args.range, track_actions=args.track_actions, 
              data_types_actions=args.data_types_actions, data_types_list=args.data_types_list,
              write_format=args.format, relative_coord=args.relative_coord, 
              intervals_gen=args.intervals_gen, multiply_f=args.multiply_intervals, 
              no_header=args.no_header, fields2read=args.fields_read, window_size=args.window_size, 
              no_track_line=args.no_track_line, separator=args.field_separator, 
              bed_lab_sw=args.bed_label, color_dict=args.color_file, window_mean=args.window_mean)
                                                       
    print  >> stderr, "Correct execution!"
    
    
if __name__ == '__main__':
        
    parser_jaaba_parser = ArgumentParser(parents=[parsers.jaaba_parser])        
    
    args = parser_jaaba_parser.parse_args()
    
    exit(main(option=args.command))
    

else:
    print ("You correctly transform your JAABA scores into a csv file")
    
    input_jaaba_file = '/Users/jespinosa/JAABA_MAC_0.5.1/sampledata_v0.5/Chase1_TrpA_Rig1Plate15BowlA_20120404T141155/scores_chase.mat'
    map_file_jaaba = "/Users/jespinosa/git/pergola/test/jaaba2pergola.txt"
    int_data_jaaba = parsers.jaaba_scores_to_intData(input_file = input_jaaba_file, map_jaaba = map_file_jaaba, norm=True, data_type="chase")
    
    print int_data_jaaba.min
    print int_data_jaaba.max
    print int_data_jaaba.tracks
    print int_data_jaaba.data
    
    exit ("You correctly transform your JAABA scores into IntData")