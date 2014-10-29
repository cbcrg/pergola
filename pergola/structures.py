class IntData: 
    """
    Generic class for input data
    
    .. attribute:: path
       Name of path to a csv/tab input file
    
    .. attribute:: delimiter
       Character use to separate values of the same record in file (default "\t").
    
    list with the behavioral fields corresponding each column in the original file
    
    :return: IntData object
    
     
    """
    def __init__(self, path, ontology_dict, **kwargs):
        self.path = check_path(path)
        self.delimiter = self._check_delimiter(self.path, kwargs.get('delimiter', None))
        
    def _check_delimiter (self, path, delimiter):
        """ 
        Check whether the delimiter works, if delimiter is not set then tries ' ', '\t' and ';'
         
        :param path: (str) name of path to a behavioral file in the form of a csv file
        :param delimiter: (str) delimiter used in the file ("tab", ";", "space") 
         
        """
                        
        self.inFile  = open(path, "rb")
        
        for row in self.inFile:            
            if row.count(delimiter) >= 1: break
            else: raise ValueError("Input delimiter does not correspond to delimiter found in file \'%s\'"%(self.delimiter))
            
            if row.count(" ") >= 1:
                self.delimiter = " "
                break
            if row.count("\t") >= 1:
                self.delimiter = "\t"
                break
            if row.count(";") >= 1:
                self.delimiter = "\t"
                break      
        
        if delimiter is None: 
            raise ValueError("Delimiter must be set \'%s\'"%(delimiter))
            
        return delimiter