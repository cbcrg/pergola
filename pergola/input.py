"""
30 Oct 2014

"""

class ConfigInfo():
    """
    Class holds a dictionary with the ontology between the genomic fields and the phenomics fields
    Ontology can be read both from a tabulated file or a ontology format file 
    
    .. attribute:: path
       Name of/path to a configuration file
    
    .. attribute::  correspondence 
       Dictionary with keys fields in behavioral file and values correspondence in genomic grammar
    
    """
    
    def __init__(self, path, **kwargs):
        self.path = check_path(path)
        self.correspondence = self._correspondence_from_config(self.path)
    
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
                
                
    def _tab_config(self, file_tab):
        dict_correspondence ={}
        
        for row in file_tab:            
            row_split = row.rstrip('\n').split('\t')
            dict_correspondence[row_split[0]] = row_split[1]
        return (dict_correspondence)    
    
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
        
        return delimiter
        
        """
        for key, value in self.correspondence.iteritems():
            print '\t' * indent + str(key),
            
            if isinstance(value, dict):
                self.write(value, indent+1)
            else:
                print '\t' * (indent+1) + str(value)
