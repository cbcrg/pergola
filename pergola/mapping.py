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

from re      import match
from os      import getcwd
from sys     import stderr
from os.path import join

_genome_file_ext = ".fa"
_generic_nt = "N"
_cytoband_file_ext = ".txt"
_bed_file_ext = ".bed"

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
    
    :returns: ConfigInfo object
    
    """
    
    def __init__(self, path, **kwargs):
        self.path = check_path(path)
        self.correspondence = self._correspondence_from_config(self.path)
    
    #TODO documentation
    def _correspondence_from_config(self, path):
        with open(path) as config_file:
            #Eliminates possible empty lines at the end
            config_file_list = filter(lambda x:  not match(r'^\s*$', x), config_file)
            
            if config_file_list[0][0] == '#':
                del config_file_list [0]
                return(self._tab_config(config_file_list))

            elif config_file_list[0][0] == '!':
                del config_file_list[:2]
                return(self._mapping_config(config_file_list))
            else:
                raise TypeError("Configuration file format is not recognized: \"%s\"." % (path))
                
    #TODO documentation            
    def _tab_config(self, file_tab):
        dict_correspondence ={}
        
        for row in file_tab:            
            row_split = row.rstrip('\n').split('\t')
            dict_correspondence[row_split[0]] = row_split[1]
        return (dict_correspondence)    
    
    #TODO documentation
    def _mapping_config(self, file_map):
        dict_correspondence ={}
       
        for row in file_map:
            l=row.split(">")
            dict_correspondence[l[0].split(":")[1].rstrip()] = l[1].split(":")[1].rstrip('\t\n')        

        return (dict_correspondence)   
    
    def write(self, indent=0):
        """ 
        Writes correspondence between the genomic and the behavioral data 
         
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
    
    """
    assert isinstance(path, basestring), "Expected string or unicode, found %s." % type(path)
    try:
        open(path, "r")
    except IOError:
        raise IOError('File does not exist: %s' % path)
    return path      

def write_chr(self, mode="w", path_w=None):
    """
    
    Creates a fasta file of the length of the range of value inside the IntData object
    that will be use for the mapping the data into it
    
    :param mode: :py:func:`str` mode to use by default write
    :param None path_w: :py:func:`str` path to dump the files, by default None 
    
    """
    chrom = 'chr1'
    path = ""
    
    if not path_w: 
        path = getcwd()
        print >>stderr, 'Chromosome fasta like file will be dump into \"%s\" ' \
                       'as it has not been set using path_w' % (path)
    else:
        path = path_w
                            
    genomeFile = open(join(path, chrom + _genome_file_ext), mode)        
    genomeFile.write(">" + chrom + "\n")
    genomeFile.write (_generic_nt * (self.max - self.min) + "\n")
    genomeFile.close()
    print >>stderr, 'Genome fasta file created: %s' % (path + "/" + chrom + _genome_file_ext)

def write_cytoband(self, end, start=0, delta=43200, start_phase="light", mode="w", path_w=None):
    """
     
    Creates a cytoband-like and a bed file with phases of the experiment 
    
    :param end: :py:func:`int` last timepoint in the series
    :param start: :py:func:`int` first timepoint in the series, by default 0
    :param delta: :py:func:`int` delta between intervals, by default 43200 seconds, 12 hours
    :param light start_phase: :py:func:`str` first phase "light" or "dark", by default light
    :param w mode: :py:func:`str` mode to use for file, by default write  
    :param None path_w: :py:func:`str` path to dump the files, by default None 
    
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
    phases_bed_file = open(join(path, name_bed + _bed_file_ext), mode)  
    phases_bed_light_f = open(join(path, name_bed_light + _bed_file_ext), mode) 
    phases_bed_dark_f = open(join(path, name_bed_dark + _bed_file_ext), mode) 
    
    phases_bed_file.write("track name=\"phases\" description=\"Track annotating phases of the experiment\" visibility=2 color=0,0,255 useScore=1 priority=user\n")
    phases_bed_light_f.write("track name=\"phases\" description=\"Track annotating phases of the experiment\" visibility=2 color=0,0,255 useScore=1 priority=user\n")
    phases_bed_dark_f.write("track name=\"phases\" description=\"Track annotating phases of the experiment\" visibility=2 color=0,0,255 useScore=1 priority=user\n")
    
    phase = start_phase
    
    if phase not in dict_stain:
        raise ValueError("Phase allowed values are dark or light, current value is:  %s." % (phase)) 
         
    if start != 0:
        line =  "{0}\t{1}\t{2}\t{3}\t{4}\n".format(chr, t, start, phase, dict_stain[phase])
        line_bed = "{0}\t{1}\t{2}\t{3}\t{4}\n".format(chr, t, start, phase, dict_bed_values[phase])
        t = t + start + 1
        end_t = t + delta
        
        if phase == light_ph: 
            phase=dark_ph
            phases_bed_light_f.write(line_bed)
        elif phase == dark_ph: 
            phase=light_ph
            phases_bed_dark_f.write(line_bed) 
        
        cytoband_file.write(line)
        phases_bed_file.write(line_bed)
    else:
        t = end_t + 1
        end_t += delta
                
    while t < end - delta:
        line =  "{0}\t{1}\t{2}\t{3}\t{4}\n".format(chr, t, end_t, phase, dict_stain[phase])
        line_bed = "{0}\t{1}\t{2}\t{3}\t{4}\n".format(chr, t, end_t, phase, dict_bed_values[phase])
        cytoband_file.write(line)
        phases_bed_file.write(line_bed)
        t = end_t + 1
        end_t += delta
        
        if phase == light_ph: 
            phase=dark_ph
            phases_bed_light_f.write(line_bed)
        elif phase == dark_ph: 
            phase=light_ph 
            phases_bed_dark_f.write(line_bed) 
            
    line =  "{0}\t{1}\t{2}\t{3}\t{4}\n".format(chr, t, end, phase, dict_stain[phase]) 
    line_bed = "{0}\t{1}\t{2}\t{3}\t{4}\n".format(chr, t, end, phase, dict_bed_values[phase])   
    
    cytoband_file.write(line)
    phases_bed_file.write(line_bed)
    cytoband_file.close()
    phases_bed_file.close()
    phases_bed_light_f.close()
    phases_bed_dark_f.close()