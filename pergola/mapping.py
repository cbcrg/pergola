"""
=======================
Module: pergola.mapping
=======================

.. module:: mapping

This module  provides the class and functions to map the fields of input files 
into genomic fields.

It provides a class :class:`~pergola.mapping.OntologyInfo` that reads the information
from a ontology file.
 
"""

from re      import match
from os      import getcwd
from sys     import stderr
from os.path import join

_genome_file_ext = ".fa"
_generic_nt = "N"

class OntologyInfo(): #cambiar ontologyInfo y quiza la libreria mapping
    """
    Class holds a dictionary with the ontology between the genomic fields and the phenomics fields
    Ontology can be read both from a tabulated file or a ontology format file 
    
    .. attribute:: path
       Name of/path to a configuration file
    
    .. attribute::  correspondence 
       Dictionary with keys fields in behavioral file and values correspondence in genomic grammar
    
    :return: ConfigInfo object
    
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
    
    """
    chrom = 'chr1'
    
    if not path_w: 
        pwd = getcwd()
        print >>stderr, 'Chromosome fasta like file will be dump into \"%s\" ' \
                        'as it has not been set using path_w' % (pwd)

    genomeFile = open(join(pwd, chrom + _genome_file_ext), mode)        
    genomeFile.write(">" + chrom + "\n")
    print "-----------min max",self.max - self.min #del
    genomeFile.write (_generic_nt * (self.max - self.min))
    genomeFile.close()
    print >>stderr, 'Genome fasta file created: %s' % (pwd + chrom + _genome_file_ext)
      