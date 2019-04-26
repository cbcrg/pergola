#!/usr/bin/env python
#
#  Copyright (c) 2014-2019, Centre for Genomic Regulation (CRG).
#  Copyright (c) 2014-2019, Jose Espinosa-Carrasco and the respective authors.
#
#  This file is part of Pergola.
#
#  Pergola is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pergola is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Pergola.  If not, see <http://www.gnu.org/licenses/>.

from pergola import parsers
from pergola import jaaba_parsers
from argparse import ArgumentParser
from sys      import stderr, exit
import pergola_rules
from os.path import dirname, abspath, basename, splitext
from os import chdir, getcwd
from shutil import copy, rmtree

from tempfile import NamedTemporaryFile, mkdtemp

def main(args=None):
    """
    main function
    """
    parser_jaaba_parser = ArgumentParser(parents=[parsers.jaaba_parser])        
    
    args = parser_jaaba_parser.parse_args()
    
#     jaaba_to_pergola(option=args.command)
    jaaba_to_pergola(option=args.command, args=args)
    
def jaaba_to_pergola(option, args):
    """
    main function
    sc: scores to csv 
    sp: scores to pergola
    fc: features to csv
    fp: features to pergola
    """

    for input_file in args.input:
        if option == "sc" or option =="sp":

            print >> stderr,     "@@@jaaba_to_pergola.py: Input file is %s" % input_file

            tmp_track = NamedTemporaryFile(prefix='jaaba_csv', suffix='.csv', delete=True)

            name_tmp = splitext(basename(tmp_track.name))[0]
            path_out = dirname(abspath(tmp_track.name))

            jaaba_parsers.jaaba_scores_to_csv(input_file=input_file, path_w=path_out, name_file=name_tmp, norm=True, data_type="chase")

            output_file = tmp_track.name

            if option == "sc":
                path_w = dirname(abspath(input_file))
                f_out = path_w + '/' + 'JAABA_scores.csv'

                copy (tmp_track.name, f_out)
                print >> stderr,  "@@@jaaba_to_pergola.py: Scores dumped in %s" % f_out

            elif option == "sp":
                pergola_rules.pergola_rules(path=output_file, map_file_path=args.mapping_file, sel_tracks=args.tracks,
                      list=args.list, range=args.range, track_actions=args.track_actions,
                      data_types_actions=args.data_types_actions, data_types_list=args.data_types_list,
                      write_format=args.format, relative_coord=args.relative_coord,
                      intervals_gen=args.intervals_gen, multiply_f=args.multiply_intervals,
                      no_header=args.no_header, fields2read=args.fields_read, window_size=args.window_size,
                      no_track_line=args.no_track_line, separator=args.field_separator,
                      bed_lab_sw=args.bed_label, color_dict=args.color_file, window_mean=args.window_mean)

        elif option == "fc" or option == "fp":
            print >> stderr,  "@@@jaaba_to_pergola.py: Extracting Jaaba features from %s" % input_file
            print >> stderr,  "@@@jaaba_to_pergola.py: Selected feature/s %s" %args.feature


            if not args.dumping_dir:
                dumping_dir = getcwd()
                print >> stderr, "@@@jaaba_to_pergola.py: No path selected, files dump into path: ", dumping_dir
            else:
                dumping_dir = args.dumping_dir
                print >> stderr, "@@@jaaba_to_pergola.py: Files dump into path: ", dumping_dir

            path_tmp = mkdtemp()

            for f in args.feature:
                jaaba_parsers.extract_jaaba_features(dir_perframe=input_file, map_jaaba="", delimiter="\t",
                                               feature=f, output="csv", path_w=path_tmp)

                tmp_file = path_tmp + '/' + f + '.csv'

                if option == "fc":
                    f_out = dumping_dir + '/' + f +  '.csv'

                    copy (tmp_file, f_out)

                elif option == "fp":
                    chdir(dumping_dir)
    #                 pergola_rules.main(path=tmp_file, map_file_path=args.mapping_file, sel_tracks=args.tracks,
                    pergola_rules.pergola_rules(path=tmp_file, map_file_path=args.mapping_file, sel_tracks=args.tracks,
                      list=args.list, range=args.range, track_actions=args.track_actions,
                      data_types_actions=args.data_types_actions, data_types_list=args.data_types_list,
                      write_format=args.format, relative_coord=args.relative_coord,
                      intervals_gen=args.intervals_gen, multiply_f=args.multiply_intervals,
                      no_header=args.no_header, fields2read=args.fields_read, window_size=args.window_size,
                      no_track_line=args.no_track_line, separator=args.field_separator,
                      bed_lab_sw=args.bed_label, color_dict=args.color_file, window_mean=args.window_mean)

            rmtree(path_tmp)
                                                       
if __name__ == '__main__':
        
#     parser_jaaba_parser = ArgumentParser(parents=[parsers.jaaba_parser])        
    
#     args = parser_jaaba_parser.parse_args()
    
    exit(main())