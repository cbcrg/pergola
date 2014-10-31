from input import check_path
from csv   import reader

class IntData: 
    """
    Generic class for input data
    
    .. attribute:: path
       Name of path to a csv/tab input file
    
    .. attribute:: delimiter
       Character use to separate values of the same record in file (default "\t").
    
    .. attribute:: header
       Indicates the presence of a header.
       * `False` if there is no header. Fields should the be provided using fields param
       * `True` if the file have a header line with names. This names should match names in ontology_dict (default).
    
    .. attribute:: fieldsB
        List with the behavioral fields corresponding each column in the file
        
    
    :return: IntData object
    
     
    """
    def __init__(self, path, ontology_dict, **kwargs):
        self.path = check_path(path)
        self.delimiter = self._check_delimiter(self.path, kwargs.get('delimiter', "\t"))
        self.header = kwargs.get('header',True)
        self.fieldsB = self._set_fields_b(kwargs.get('fields'))
        self.fieldsG = self._set_fields_g(ontology_dict)
        self.data, self.min, self.max = self._new_read(multiply_t = kwargs.get('multiply_t', 1), intervals=kwargs.get('intervals', False))
        
    def _check_delimiter (self, path, delimiter):
        """ 
        Check whether the delimiter works, if delimiter is not set then tries ' ', '\t' and ';'
         
        :param path: :py:func:`str` name of path to a behavioral file in the form of a csv file
        :param delimiter: :py:func:`str` delimiter used in the file ("tab", ";", "space") 
        
        return delimiter
        
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
    
    def _set_fields_b(self, fields=None):
        """
        Reading the behavioral fields from the header file or otherwise setting  
        the fields to numeric values corresponding the column index starting at 0
        
        :param None fields: :py:func:`list` with the behavioral fields corresponding each column in the file
        
        :return: list with the behavioral fields
            
        """ 
        self.inFile  = open(self.path, "rb")
        self.reader =  reader(self.inFile, delimiter=self.delimiter)       
        
        if self.header:            
            header = self.reader.next()
            first_r = self.reader.next()
            
            if len(header) != len(first_r):
                raise ValueError("Number of fields in header '%d' does not match number of fields in first row '%d'" 
                                 % (len(header), len(first_r)))
            
            if fields:
                if len(fields) > len(first_r):
                    raise ValueError("Input field list \"%s\" is longer than totals fields available in file \'%s\'" 
                                     % ("\",\"".join(fields), len(first_r)))
                
                if not all(field in header for field in fields):
                    raise ValueError("Input field list \"%s\" has items not present in file header \'%s " 
                                     '\n'
                                     "Also make sure you don't need to set header=False"
                                     % ("\",\"".join(fields), "\",\"".join(header)))
                
                fieldsB = fields
                     
            else:       
                fieldsB = [header[0].strip('# ')]+header[1:]        
        else:
            first_r = self.reader.next()
            
            if fields:
                if len(fields) > len(first_r):
                    raise ValueError("Input field list \"%s\" is longer than totals fields available in file \'%s\'" % ("\",\"".join(fields), len(first_r)))            
                            
                fieldsB = fields
                
                print ("WARNING: As header=False you col names set by fields will be consider to have the order "
                        "you provided: %s" 
                        %"\",\"".join(fields))                 
            else:                                
                raise ValueError ('File should have a header, otherwise you should set ' 
                                  'an ordered list of columns names using fields')     
                
        self.inFile.close()
        
        return fieldsB
    
    def _set_fields_g (self, ontology_dict):
        """
        Extracts the correspondence of fields in genomic grammar of the behavioral file.
        
        :param ontology_dict: relationship between genomic and behavioral data (:py:class:`dict`)
        
        :return: list with the corresponding genomics names of the fields inside behavioral (input) data
         
        """
            
        if all(field_b in ontology_dict for field_b in self.fieldsB):
            name_fields_g = [ontology_dict [k] for k in self.fieldsB]
        else:    
            raise ValueError("Fields param \"%s\" contains a field not present in config_file \"%s\"" 
                             % ("\",\"".join(self.fieldsB), "\",\"".join(ontology_dict.keys())))

        return name_fields_g
    
    def _new_read(self, multiply_t=1, intervals=False):
        """
        Reads the information inside the input file and returns minimun and maximun.
        
        :param 1 multiply: multiplies the values of the field set as chromStart and 
            chromEnd
        :param False intervals: if True pergola creates intervals from the field set
            as chromStart, 
            
        TODO add example of input file structure and the output of the function
        
        return: list with intervals contained in file, minimum and maximum values inside the file 
        
        """
        
        list_data = list()
        self.inFile  = open(self.path, "rb")
        self.reader = reader(self.inFile, delimiter='\t')
        self.reader.next()
                        
        _int_points = ["chromStart", "chromEnd"]
        idx_fields2int = [10000000000000]
        i_new_field = [10000000000000]                                    
        
        if intervals:             
            print >>sys.stderr, "Intervals inferred from timepoints"
            _time_points = ["chromStart"]
            f_int_end = "chromEnd"
        
            if f_int_end in self.fieldsG:
                raise ValueError("Intervals can not be generated as '%s' already exists in file %s." % (f_int_end, self.path))
                
            try:
                idx_fields2int = [self.fieldsG.index(f) for f in _time_points]              
            except ValueError:
                raise ValueError("Parameter intervals=True needs that field '%s' is in file is not missing %s." 
                                 % (f, self.path))
            
            self.fieldsG.append(f_int_end)   
            i_new_field = [len(self.fieldsG) - 1]
        
        try:            
            f=""
            name_fields2mult = [f for f in _int_points if f in self.fieldsG] 
            idx_fields2mult = [self.fieldsG.index(f) for f in name_fields2mult]
                 
        except ValueError:
            raise ValueError("Field '%s' not in file %s." % (f, self.path))
        
        p_min = None
        p_max = None
        
        _start_f = ["chromStart"]
        try:
            i_min = [self.fieldsG.index(f) for f in _start_f]              
        except ValueError:
            raise ValueError("Field '%s' for min interval calculation time not in file %s." % (f, self.path))
            
        _end_f = ["chromEnd"]
        try:
            i_max = [self.fieldsG.index(f) for f in _end_f]              
        except ValueError:
            raise ValueError("Field '%s' for max interval calculation time not in file %s." % (f, self.path))
              
        v = 0
        p_v = 0
        first = True
        p_temp = []
        
        for interv in self.reader:            
            temp = []            
            
            for i in range(len(self.fieldsG)): 
                if i in idx_fields2mult and i in idx_fields2int:
                    v = int(float(interv[i]) * multiply_t)
                    temp.append(v)
                    p_v = v - 1
                    if intervals: last_start = v
                elif i in i_new_field and i in idx_fields2mult:
                    if first:
                        pass
                    else:
                        p_temp.append(p_v)                        
                elif i in idx_fields2mult and i not in idx_fields2int:
                    v = int(float(interv[i]) * multiply_t)
                    temp.append(v)
                else:
                    v = interv[i]              
                    temp.append(v)
                
                if i in i_min:
                    if p_min is None: p_min = v
                    if p_min > v: p_min = v
                
                if i in i_max:
                    if i_max == i_new_field:
                        if first: pass
                        if p_max is None: p_max = p_v
                        if p_max < p_v: p_max = p_v
                    else:
                        if p_max is None: p_max = v
                        if p_max < v: p_max = v
            if first:
                first = False 
                p_temp = temp
            else:               
                list_data.append((tuple(p_temp))) 
                p_temp = temp
            
        # last line of the file when intervals are generated
        if intervals: temp.append(last_start + 1)

        list_data.append((tuple(temp)))             

        self.inFile.close()
#         dataIter(self._read(indexL, idx_fields2rel, idx_fields2int, l_startChrom, l_endChrom, multiply_t), self.fieldsG)
        return (list_data, p_min, p_max)