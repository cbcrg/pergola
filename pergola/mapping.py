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

"""
=======================
Module: pergola.mapping
=======================

.. module:: mapping

This module  provides the class and functions to map the fields of input files 
into pergola ontology genomic-like fields.

It provides a class :class:`~pergola.mapping.MappingInfo` that reads the information
from a mapping file.
 
"""
from re      import compile, match, split
from os      import getcwd
from sys     import stderr, exit
from os.path import join
from tracks  import Track

_genome_file_ext = ".fa"
_generic_nt = "N"
_cytoband_file_ext = ".txt"
_bed_file_ext = ".bed"
_chrm_size_ext = ".sizes"

_p_ontology_terms = ["start", "data_value", "end", "data_types", "track", "chrom", "dummy"]


class MappingInfo():
    """
    Class holds a dictionary with the mappings between the pergola ontology and the phenomics fields
    Mapping can be read both from a tabulated file or the _external_mapping_file_format from the 
    Gene Ontology Consortium 
    
    .. _external_mapping_file_format: http://geneontology.org/page/external-mapping-file-format 
    
    .. attribute:: path
       Name of/path to a configuration file
    
    .. attribute::  correspondence 
       Dictionary with keys fields in behavioral file and values correspondence in genomic grammar
    
    :returns: MappingInfo object
    
    """
    
    def __init__(self, path, **kwargs):
        self.path = check_path(path)
        self.correspondence = self._correspondence_from_config(self.path)

    def _correspondence_from_config(self, path):
        """
        Recognizes the type of mapping file tab separated or the External Mapping File Format
        from the Gene Ontology Consortium. Deletes comments        

        :param path: :py:func:`str` path to the mapping file aka configuration file

        :returns: dictionary with mappings

        """

        with open(path) as config_file:
            # Eliminates possible empty lines at the end
            config_file_list = filter(lambda x: not match(r'^\s*$', x), config_file)

            file_list_no_comments = [l for l in config_file_list if l[0] != "!" if l[0] != "#"]

            for i, line in enumerate(file_list_no_comments):
                if not match(r"^\w+\:[\"\w\"]|[\w]+\s\>\s\w+\:\w+] ", line) and not match(r"(\w+)\s+(\w+)", line):
                    raise TypeError("Mapping file format is not recognized: \"%s\"." % (path))

            # Checks that files is a tsv and has the desired number of fields
            if match(r"^\w+\:[\"\w\"]|[\w]+\s\>\s\w+\:\w+] ", file_list_no_comments[0]):
                return self._mapping_config(file_list_no_comments)
            elif match(r"(\w+)\s+(\w+)", file_list_no_comments[0]):
                return self._tab_config(file_list_no_comments)
            else:
                raise TypeError("Mapping file format is not recognized: \"%s\"." % (path))

    def _tab_config(self, file_tab):
        """
        Reads mappings from a tab separated files        
       
        :param file_tab: :py:func:`list` with the content of mapping file 
        
        :returns: dictionary with mappings

        """

        dict_correspondence = {}
        comment_tag_t = "#"
        
        dummy_ctr=0
        
        for row in file_tab:
            if row.startswith(comment_tag_t):
                continue
            row_split = split(r'\s+', row.rstrip('\n'))

            file_term = row_split[0]
            pergola_term = row_split[1]
            
            # Validation of the ontology term
            if pergola_term not in _p_ontology_terms:
                raise ValueError("Term %s is not a valid pergola term." % (pergola_term))
            
            if pergola_term == "dummy": 
                    pergola_term = pergola_term + "_" + str(dummy_ctr)
                    dummy_ctr = dummy_ctr + 1
            
            dict_correspondence[file_term] = pergola_term

        return (dict_correspondence)    

    def _mapping_config(self, file_map):
        """
        Reads mappings from a file formatted following the External Mapping File Format
        from the Gene Ontology Consortium      

        :param file_map: :py:func:`list` with the content of mapping file 

        :returns: dictionary with mappings

        """

        dict_correspondence = {}
        mapping_l_ex = "tag_file:field_input_file > pergola:pergola_ontology_term"
        # comment_tag = ("#", "!")
        comment_tag_m = "!"
#         p_mapping = compile(r'^\w+\:\w+\s\>\s\w+\:\w+') 
        p_mapping = compile(r"^\w+\:[\"\w\"]|[\w]+\s\>\s\w+\:\w+] ") 
        
        dummy_ctr=0
        
        for row in file_map:
            if p_mapping.match(row):
                row = row.replace('\"','')
                l=row.split(">")
                file_term = l[0].split(":")[1].rstrip()
                pergola_term = l[1].split(":")[1].rstrip('\t\n\r')
                
                # Validation of the ontology term
                if pergola_term not in _p_ontology_terms:
                    raise ValueError("Term %s is not a valid pergola term." % (pergola_term))
                
                if pergola_term == "dummy": 
                    pergola_term = pergola_term + "_" + str(dummy_ctr)
                    dummy_ctr = dummy_ctr + 1
                     
                dict_correspondence[file_term] = pergola_term
            
            elif(row.startswith(comment_tag_m)):   
                continue            
            else:
                raise TypeError("Mapping file format not recognized:\n \"%s\"\n"  \
                                "You can see a correct example below:\n\"%s\"."  \
                                % (row.rstrip('\n'), mapping_l_ex))
                
        return (dict_correspondence)   
    
    def write(self, indent=0):
        """ 
        Writes correspondence between the pergola ontology terms and the behavioral data 
         
        :param 0 indent: :py:func:`int` set indent to be used when writing 
        
        """

        for key, value in self.correspondence.iteritems():
            print '\t' * indent + str(key),
            
            if isinstance(value, dict):
                self.write(value, indent+1)
            else:
                print '\t' * (indent+1) + str(value)


def check_path(path):
    """ 
    Check whether the input file exists and is accessible and if OK returns path
    
    :param path: path to the intervals file
    
    :returns: the path assessed
    
    """

    assert isinstance(path, basestring), "Expected string or unicode, found %s." % type(path)
    try:
        open(path, "r")
    except IOError:
        raise IOError('File does not exist: %s' % path)
    return path      


def write_chr(self, mode="w", path_w=None, min_c=None, max_c=None):
    """
    Creates a fasta file of the length of the range of value inside the IntData object
    that will be use for the mapping the data into it
    
    :param mode: :py:func:`str` mode to use by default write
    :param None path_w: :py:func:`str` path to dump the files, by default None 
    :param None min_c: :py:func:`int` min coordinate for fasta file generation, by default None
    :param None max_c: :py:func:`int` max coordinate for fasta file generation, by default None
    """

    assert isinstance(self, Track), "Expected Track object, found %s." % type(self)
    
    chrom = 'chr1'
    path = ""
    
    if not path_w: 
        path = getcwd()
        print >>stderr, 'Chromosome fasta like file will be dump into \"%s\" ' \
                       'as it has not been set using path_w' % (path)
    else:
        path = path_w

    if min_c is None:
        min_c = self.min

    if max_c is None:
        max_c = self.max

    genomeFile = open(join(path, chrom + _genome_file_ext), mode)        
    genomeFile.write(">" + chrom + "\n")
    # genomeFile.write(_generic_nt * int(self.max - self.min) + "\n")
    genomeFile.write(_generic_nt * int(max_c - min_c) + "\n")
    genomeFile.close()
    print >>stderr, 'Genome fasta file created: %s' % (path + "/" + chrom + _genome_file_ext)


def write_chr_sizes(self, mode="w", path_w=None, file_n=None, min_c=None, max_c=None):
    """    
    Creates a text file of the length of the "chromomosomes" that is needed to 
    perform some BEDtools operations such as BEDcomplement
    
    :param mode: :py:func:`str` mode to use by default write
    :param None path_w: :py:func:`str` path to dump the files, by default None
    :param None file_n: :py:func:`str` name of file
    :param None min_c: :py:func:`int` min coordinate for chromosome size file, by default None
    :param None max_c: :py:func:`int` max coordinate for chromosome size file, by default None
    """

    assert isinstance(self, Track), "Expected Track object, found %s." % type(self)
    
    chrom = 'chr1'
    
    if file_n is None:
        file_sizes_n = 'chrom'
    else:
        file_sizes_n = file_n
        
    path = ""
    
    if not path_w: 
        path = getcwd()
        print >>stderr, 'chromsizes text file will be dump into \"%s\" ' \
                       'as it has not been set using path_w' % (path)
    else:
        path = path_w

    if min_c is None:
        min_c = self.min

    if max_c is None:
        max_c = self.max

    chrom_size_f = open(join(path, file_sizes_n + _chrm_size_ext), mode)        
    chrom_size_f.write('%s\t' % chrom)
#     chrom_size_f.write ('%d\n' % (self.max - self.min))
#     chrom_size_f.write ('%d\n' % (self.max - 0))
#     chrom_size_f.write('%d\n' % (self.max + 2))
    chrom_size_f.write('%d\n' % (max_c - min_c + 2))
    chrom_size_f.close()
    print >>stderr, 'File containing chrom sizes created: %s' % (path + "/" + file_sizes_n + _chrm_size_ext)


def write_cytoband(end, start=0, delta=43200, start_phase="light", mode="w", path_w=None, lab_bed=True, track_line=True):
    """
    Creates a cytoband-like and a bed file with phases of the experiment 
    
    :param end: :py:func:`int` last timepoint in the series
    :param start: :py:func:`int` first timepoint in the series, by default 0
    :param delta: :py:func:`int` delta between intervals, by default 43200 seconds, 12 hours
    :param light start_phase: :py:func:`str` first phase "light" or "dark", by default light
    :param w mode: :py:func:`str` mode to use for file, by default write
    :param None path_w: :py:func:`str` path to dump the files, by default None 
    :param True lab_bed: If true shows label corresponding to dataType in bed file otherwise 
        shows "."
    :param True track_line: If true includes track_line in the file 
        TODO: extend light and dark to other possible values using variables
        Eventually separate into two different functions write_cytoband and write_bed

    """

    t = 0
    end_t = 0
    path = ""
    chr = "chr1"
    name_cytob = "cytoband_file"
    phase = ""
    color = ""
    light_ph = "light" 
    light_stain = "gneg"
    dark_ph = "dark"
    dark_stain = "gpos25"
    dict_stain = {light_ph: "gneg", dark_ph:"gpos25"}
    
    name_bed = "phases"
    name_bed_light = name_bed + "_" + light_ph
    name_bed_dark = name_bed + "_" + dark_ph
    
    dict_bed_values = {light_ph: "0", dark_ph:"1000"}
     
    if not path_w: 
        path = getcwd()
        print >>stderr, 'Cytoband like file will be dump into \"%s\" ' \
                        'as it has not been set using path_w' % (path) 
        print >>stderr, 'Bed files with phases will be dump into \"%s\" ' \
                        'as it has not been set using path_w' % (path)     
    else:
        path = path_w
             
    cytoband_file = open(join(path, name_cytob + _cytoband_file_ext), mode)  
    # phases_bed_file = open(join(path, name_bed + _bed_file_ext), mode)
    phases_bed_light_f = open(join(path, name_bed_light + _bed_file_ext), mode)
    phases_bed_dark_f = open(join(path, name_bed_dark + _bed_file_ext), mode) 
    
    if track_line:
        # phases_bed_file.write("track name=\"phases\" description=\"Track annotating phases of the experiment\" visibility=2 color=0,0,255 useScore=1 priority=user\n")
        phases_bed_light_f.write("track name=\"phases\" description=\"Track annotating phases of the experiment\" visibility=2 color=0,0,255 useScore=1 priority=user\n")
        phases_bed_dark_f.write("track name=\"phases\" description=\"Track annotating phases of the experiment\" visibility=2 color=0,0,255 useScore=1 priority=user\n")
    
    phase = start_phase
    
    if lab_bed: phase_bed = phase
    else: phase_bed = "."
    
    if phase not in dict_stain:
        raise ValueError("Phase allowed values are dark or light, current value is:  %s." % (phase))
    
    if start != 0:
        line =  "{0}\t{1}\t{2}\t{3}\t{4}\n".format(chr, t, start, phase, dict_stain[phase])
        line_bed = "{0}\t{1}\t{2}\t{3}\t{4}\n".format(chr, t, start, phase_bed, dict_bed_values[phase])
        t = t + start + 1
        end_t = t + delta
        
        if phase == light_ph: 
            phase=dark_ph
            phases_bed_light_f.write(line_bed)
        elif phase == dark_ph: 
            phase=light_ph
            phases_bed_dark_f.write(line_bed) 
        
        cytoband_file.write(line)
        # phases_bed_file.write(line_bed)
    else:
        t = end_t + 1
        end_t += delta
    
    if lab_bed: phase_bed = phase
    else: phase_bed = "."
         
    while t < end - delta:
        line =  "{0}\t{1}\t{2}\t{3}\t{4}\n".format(chr, t, end_t, phase, dict_stain[phase])
#         line_bed = "{0}\t{1}\t{2}\t{3}\t{4}\n".format(chr, t, end_t, phase, dict_bed_values[phase])
        line_bed = "{0}\t{1}\t{2}\t{3}\t{4}\n".format(chr, t, end_t, phase_bed, dict_bed_values[phase])
        cytoband_file.write(line)
        # phases_bed_file.write(line_bed)
        t = end_t + 1
        end_t += delta
        
        if phase == light_ph: 
            phase=dark_ph
            
            if lab_bed: phase_bed = phase
            else: phase_bed = "."
            
            phases_bed_light_f.write(line_bed)
        elif phase == dark_ph: 
            phase=light_ph
            
            if lab_bed: phase_bed = phase
            else: phase_bed = "."
            
            phases_bed_dark_f.write(line_bed)
        
        if lab_bed: phase_bed = phase
        else: phase_bed = "." 
            
    line =  "{0}\t{1}\t{2}\t{3}\t{4}\n".format(chr, t, end, phase, dict_stain[phase]) 
    line_bed = "{0}\t{1}\t{2}\t{3}\t{4}\n".format(chr, t, end, phase_bed, dict_bed_values[phase])   
    
    cytoband_file.write(line)
    # phases_bed_file.write(line_bed)
    cytoband_file.close()
    # phases_bed_file.close()
    phases_bed_light_f.close()
    phases_bed_dark_f.close()


def write_period_seq (end, start=0, delta=43200, tag="day", mode="w", path_w=None, name_file="period_seq", lab_bed=True, track_line=True):
    """
    Creates a cytoband-like and a bed file with phases of the experiment 
    
    :param end: :py:func:`int` last timepoint in the series
    :param start: :py:func:`int` first timepoint in the series, by default 0
    :param delta: :py:func:`int` delta between intervals, by default 43200 seconds, 12 hours
    :param day tag: :py:func:`str` tag to use in the sequence of events
    :param w mode: :py:func:`str` mode to use for file, by default write
    :param None path_w: :py:func:`str` path to dump the files, by default None
    :param period_seq name_file: :py:func:`str` output file name, by default period_seq    
    :param True lab_bed: If true shows label corresponding to dataType in bed file otherwise 
        shows "."
    :param True track_line: If true includes track_line in the file 
    
    """

    t = 0
    end_t = 0
    path = ""
    chr = "chr1"    
    name_bed = name_file
    index = 1
     
    if not path_w: 
        path = getcwd()
        print >>stderr, 'Bed files with period sequence will be dump into \"%s\" ' \
                        'as it has not been set using path_w' % (path)     
    else:
        path = path_w
             
    phases_bed_file = open(join(path, name_bed + _bed_file_ext), mode)  
    
    if track_line:
        phases_bed_file.write("track name=\"phases\" description=\"Track annotating a sequence of periods of the experiment\" visibility=2 color=0,0,255 useScore=1 priority=user\n")            
            
    for i in xrange(start, end, delta):
        if lab_bed: phase_bed = tag + "_" + str(index)
        else: phase_bed = "."
    
        if i + delta > end:
            line_bed = "{0}\t{1}\t{2}\t{3}\t{4}\n".format(chr, i+1, end, phase_bed, '1000')
        else:
            line_bed = "{0}\t{1}\t{2}\t{3}\t{4}\n".format(chr, i+1, i+delta, phase_bed, '1000')

        phases_bed_file.write(line_bed)        
        index = index + 1
    phases_bed_file.close()
