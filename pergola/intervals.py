"""
=========================
Module: pergola.intervals
=========================

.. module:: intervals

This module provides the way to read the input intervals files.
It contains a class :class:`~pergola.intervals.IntData` which has 
the attributes and methods needed for reading the data.

:py:func:`~pergola.intervals.write_chr` generates a chromosome fasta file
to map tracks that are genereted by the application

"""

from mapping import check_path
from csv   import reader
from os import getcwd
from os.path import join
from sys import stderr
# from operator import itemgetter
# from itertools import groupby 
from tracks import Track 
from operator import itemgetter
from re import split, search
from math import pow

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
    
    .. attribute:: fieldsG
    
        List with the genomic fields corresponding each column in the file    
    
    .. attribute:: min
    
        First time value in the file. Read from field set as "chromStart"
    
    .. attribute:: max
    
        Last timepoint in the file. Read from field set as "chromEnd"
    
    .. attribute:: range_values
    
        Range of values inside dataValue field
        
    .. attribute:: data
    
        List of tuples containing the data read from the file
    
    .. attribute:: dataTypes
    
        All different dataTypes that appear in the data read from "dataTypes" field.
        If dataTypes field not in file, all intervals are set as belonging to dataTypes "a"

    .. attribute:: tracks
    
        Set of tracks in the file. Read from "tracks" field.
        If tracks field not in file, all intervals are set as belonging to track "1" 
        
    :return: IntData object
    
     
    """
    def __init__(self, path, ontology_dict, **kwargs):
        self.path = check_path(path)
        self.delimiter = self._check_delimiter(self.path, kwargs.get('delimiter', "\t"))
        self.header = kwargs.get('header',True)
        self.fieldsB = self._set_fields_b(kwargs.get('fields_names', None))
        self.fieldsG_dict = self._set_fields_g(ontology_dict)
        self.fieldsG = []
        self.min = self.max = 0
        self.range_values = 0
        self.data = self._read(multiply_t = kwargs.get('multiply_t', 1), intervals=kwargs.get('intervals', False))
        self.dataTypes = self.get_field_items(field ="dataTypes", data = self.data, default="a")
        self.tracks  =  self.get_field_items(field="track", data = self.data, default="1")
        
    def _check_delimiter (self, path, delimiter):
        """ 
        Check whether the set delimiter works, if delimiter not set then tries ' ', '\t' and ';'
         
        :param path: :py:func:`str` name of path to a behavioral file in the form of a csv file
        :param delimiter: :py:func:`str` delimiter used in the file ("tab", ";", "space") 
        
        :return: delimiter
        
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
        
        fieldsB = []
        
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
                
                ori_fieldsB = [header[0].strip('# ')]+header[1:]  #del
                                
                for f in ori_fieldsB:
                    if f in fields: fieldsB.append(f)
                    else: fieldsB.append("")      
                print "fields B all fields of header", fieldsB#del
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
#         print "..............fieldsB",fieldsB #del
        return fieldsB
    
    def _set_fields_g (self, ontology_dict):
        """
        Extracts the correspondence of fields in genomic grammar of the behavioral file.
        
        :param ontology_dict: relationship between genomic and behavioral data (:py:class:`dict`)
        
        :return: list with the corresponding genomics names of the fields inside behavioral (input) data
         
        """
        dict_fields_g = {}
        i_field_b=0
        
        for field_B in self.fieldsB:
            if field_B:
                try:
                    ontology_dict [field_B]
                except KeyError:
                    raise KeyError ("Field %s is not map in your ontology mapping. " \
                                    "TIP: Fields that are not use from the input data have to be set to dummy" \
                                    "in the ontology mapping. Example: behavioural_file:%s > genome_file:dummy"                               
                                    % (field_B, field_B))                                                                                                        

                dict_fields_g[ontology_dict [field_B]] = i_field_b
            i_field_b = i_field_b + 1                    
        
        name_fields_g = [ontology_dict[k] for k in self.fieldsB if k]   
#         if all(field_b in ontology_dict for field_b in self.fieldsB):
#             name_fields_g = [ontology_dict [k] for k in self.fieldsB]
#         else:    
#             raise ValueError("Fields param \"%s\" contains a field not present in config_file \"%s\"" 
#                              % ("\",\"".join(self.fieldsB), "\",\"".join(ontology_dict.keys()))) #del 
#          YA ESTA HECVHO ARRIBA
        
        #Input file at least should have two fields that correspond to:
        mandatory_fields = ["chromStart", "dataValue"]
        
        if not all(f in dict_fields_g.keys() for f in mandatory_fields):
            raise ValueError("Input file mandatory fields  are \"chromStart\" and \"dataValue\" \n" \
                             "Your current assigned fields are \"%s\"\n" \
                             "TIP: Check your ontology_file"                               
                             % ("\",\"".join(name_fields_g)))            
        
        return dict_fields_g
    
    def _read(self, multiply_t=1, intervals=False):
        """
        Reads the information inside the input file and returns minimun and maximun.
        
        :param 1 multiply: multiplies the values of the field set as chromStart and 
            chromEnd
        :param False intervals: if True pergola creates intervals from the field set
            as chromStart, 
        
        :return: list with intervals contained in file, minimum and maximum values inside the file 
        
        TODO add example of input file structure and the output of the function
        
        """
        
        list_data = list()
        self.inFile  = open(self.path, "rb")
        self.reader = reader(self.inFile, delimiter='\t')
        
        if self.header: self.reader.next()
        
        # Field assign to data value should be an integer or float
        idx_dataValue = [self.fieldsG_dict["dataValue"]]
        
        _int_points = ["chromStart", "chromEnd"]
        idx_fields2int = [10000000000000]
        i_new_field = [10000000000000]                                    
        
        if intervals:             
            print >>stderr, "Intervals will be inferred from timepoints"
            _time_points = ["chromStart"]
            f_int_end = "chromEnd"
        
            if f_int_end in self.fieldsG_dict:
                raise ValueError("Intervals can not be generated as '%s' already exists in file %s." % (f_int_end, self.path))
                
            try:
                idx_fields2int = [self.fieldsG_dict[f] for f in _time_points]     
            except ValueError:
                raise ValueError("Parameter intervals=True needs that field '%s' is in file is not missing %s." 
                                 % (f, self.path))
            
            i_new_field = len(self.fieldsB)
            
            print "new field index is:", i_new_field
            self.fieldsG_dict[f_int_end] = i_new_field
            
            i_new_field = [i_new_field]#del
        
        try:            
            f=""
            name_fields2mult = [f for f in _int_points if f in self.fieldsG_dict] 
            idx_fields2mult = [self.fieldsG_dict[f] for f in name_fields2mult]                
        except ValueError:
            raise ValueError("Field '%s' not in file %s." % (f, self.path))
        
        p_min = None
        p_max = None
        
        _start_f = ["chromStart"]
        
        try:
#             i_min = [self.fieldsG_dict.index(f) for f in _start_f]
            i_min = [self.fieldsG_dict[f] for f in _start_f]              
        except ValueError:
            raise ValueError("Field '%s' for min interval calculation time not in file %s." % (f, self.path))
            
        _end_f = ["chromEnd"]
        try:
            i_max = [self.fieldsG_dict[f] for f in _end_f]              
        except ValueError:
            raise ValueError("Field '%s' for max interval calculation time not in file %s \n" \
                             "TIP: If your file contains timepoints you can transform them to intervals" \
                             " setting the field containing them to chromStart and setting intervals=True" 
                             % (f, self.path))
        
        # Range of dataValue field
        p_min_data_v = None
        p_max_data_v = None
        
        _start_f = ["dataValue"]
        
        try:
            i_data_value = [self.fieldsG_dict[f] for f in _start_f]
        except ValueError:
            raise ValueError("Field '%s' for dataValue range calculation time not in file %s." % (f, self.path))
        
        v = 0
        p_v = 0
        first = True
        p_temp = []
        
        print "range in dicitionary is", range(len(self.fieldsG_dict))
        
        # Setting the factor to multiply if it is not set by the user
        # different to 1 and the timepoints are decimal numbers
        if multiply_t == 1:
            
            n = 0
    #         test_decimal = list(self.reader)
            file_int = open(self.path, "rb")
            test_decimal = reader(file_int, delimiter=self.delimiter)
            test_decimal.next()        
            max_dec_len = 0
            pattern_dec_p = '\.|\,'
            
            for r in test_decimal:            
                n = n + 1
                
                print n
                if n == 200 :
    #                 self.reader.seek(0)
                    break               
                for i in sorted(self.fieldsG_dict.values()):
    #                 
    #                 
    #                 print "idx of fields to intervals are",idx_fields2int
                      
                    if i in idx_fields2int and search(pattern_dec_p, r[i]):
                        dec_len = len(split(pattern_dec_p, r[i])[1])
                        if max_dec_len < dec_len: max_dec_len = dec_len 
                        print "..............................................",max_dec_len
    # #                     print re.split('\.|\,', '0,00092')
            multiply_t = pow(10, max_dec_len)
        print "multiply_t............",multiply_t        
        exit("|||||||||||||||||||1")
        
        
        
        
        j = 0 
                          
        for interv in self.reader: 
            temp = []
            j = j + 1 
                        
            
            if j == 10 : exit("cullllllll")
            for i in sorted(self.fieldsG_dict.values()):
#                 print "index are:", i#del
#             for i in range(len(self.fieldsG_dict)):#del 
            #TODO                                   
                # Values in idx_fields2int have to be integers
#                 if i in idx_fields2int:
#                     print interv[i]
#                 
#                     a = float(interv[i]) * multiply_t
#                     print "---------", a
#                     if a.is_integer():
#                         pass
#                     else:
#                         raise ValueError ("Values in chromStart and chromEnd should be integers.\n" \
#                                           "TIP: If you have to transform value from lets say " \
#                                           "seconds to miliseconds try using multiply_t.")
# #                     a = int(float(interv[i]) * multiply_t)
#                     b = float(interv[i]) * multiply_t
#                     print "-----", interv[i], a,b, int(float(interv[i]) * multiply_t), float(interv[i]) * multiply_t
#                     if a-b != 0:
#                         raise ValueError ("Values in chromStart and chromEnd should be integers.\n" \
#                                         "TIP: If you have to transform value from lets say " \
#                                         "seconds to miliseconds try using multiply_t.")

                # Field assign to data value should be an integer or float        
#                 print ".........",idx_dataValue
                if i in idx_dataValue:                    
                    try:                        
                        float(interv[i])
                    except ValueError:
                        raise ValueError("Values in dataValue should be numerical not others: \"%s\".\n" %
                                          interv[i]) 
#                 print "Are they always the same interval column and fields to multiply:.....", (idx_fields2int, idx_fields2mult)
                if i in idx_fields2mult and i in idx_fields2int:        
                    print "idx_fields2mult --- idx_fields2int", (idx_fields2mult, idx_fields2int)
                    a = round (float(interv[i]) * multiply_t, 10)
                    
                    b = int(a)
                    print "value without int() applied and .....", (float(interv[i]) * multiply_t, b)
                    print "original value file", interv[i]
                    print "a............", (a)
                    print "b--------------",(b)
                    print "a-b",(a-b)
                    # AQUI
                    if a-b != 0:
                        raise ValueError ("Intervals values can not be decimal")                                                
                    v = int(float(interv[i]) * multiply_t)
                    print "coordinate is...............", (interv[i],v)
                    temp.append(v)
                    p_v = v - 1
                    
                    if intervals: last_start = v
                    
                elif i in i_new_field and i in idx_fields2mult:
                    print "caaaaa",(idx_fields2int, idx_fields2mult)#del
                    if first:                                                
                        pass
                    else:
                        print "coordinate is+++++++++++++++", p_v
                        p_temp.append(p_v)  
                                              
                elif i in idx_fields2mult and i not in idx_fields2int:
                    print "ciiiii",(idx_fields2int, idx_fields2mult, i)#del
                    print "Are they always the same interval column and fields to multiply:.....", (idx_fields2int, idx_fields2mult)
                    
                    
                    
                    
                    a = round (float(interv[i]) * multiply_t, 10)
                    b = int(a)
                    if a-b != 0:
                        raise ValueError ("Intervals values can not be decimal")         
                    
                    v = int(float(interv[i]) * multiply_t)
                    
                    #### AQUI
                    temp.append(v)
                
                else:
                    print "cuuuu",(idx_fields2int, idx_fields2mult)
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
                
                if i in i_data_value:
                    v = float(v)                    
                    if p_min_data_v is None: p_min_data_v = v
                    if p_min_data_v > v: p_min_data_v = v
                    if p_max_data_v is None: p_max_data_v = v
                    if p_max_data_v < v: p_max_data_v = v
                
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
        
        self.min = p_min
        self.max = p_max
        self.range_values = [p_min_data_v, p_max_data_v]
        
        #Setting the data fields that output data have in the order they are
        data_fields = []
        
        sorted_index_f = sorted(self.fieldsG_dict.items(), key=itemgetter(1))
        for field_gen in sorted_index_f:
            data_fields.append(field_gen[0])
        self.fieldsG = data_fields
        print "..........", sorted_index_f #del
        
#         DataIter(self._read(indexL, idx_fields2rel, idx_fields2int, l_startChrom, l_endChrom, multiply_t), self.fieldsG)
#         return (list_data, p_min, p_max)
        return (list_data)
    
    def get_field_items(self, data, field="dataTypes", default=None): 
        """
        Reads the unique values inside a field and returns them as a set
        If default is set and field does not exist in the data then the field is
        added to the the data and set to default value
        
        :param data: :py:func:`list` with the intervals read from data 
        :param field: :py:func:`str` field from data from which to inferred set of 
            unique values
        :param None default: if field is not present in data is created and set to 
            default
            
        :return: set with unique values inside field
        
        """

        set_fields = set()
        
        if field in self.fieldsG:
            i =  self.fieldsG.index(field)
            
            idx_field = self.fieldsG.index(field)
            field = [field]    
            
            for row in self.data:
                set_fields.add(row[idx_field])    
        elif default:
            new_data = list()
            new_field = (default,)
            
            set_fields.add(default)
            
            for row in self.data:
                row = row + new_field
                new_data.append(row)    
            
            self.data = new_data
            self.fieldsG.append(str(field))
        else:
            raise ValueError("Data has not field \'%s\' and no default value has been set \'%s\'"%(field, default)) 
        
        return set_fields
    
    
    def read(self, fields=None, relative_coord=False, intervals=False, fields2rel=None, multiply_t=1,**kwargs):
        """        
        Reads the data and converts it depending on selected options
        
        :param fields: :py:func:`list` with data columns to read
        :param False relative_coord: If true all coordinates in chromStart and chromEnd are
            make relative to the minimal value
        :param False intervals: if set to true intervals will be inferred from timepoints in
            chromStart 
        :param fields2rel: :py:func:`list` with data columns to make relative
        :param 1 multiply: :py:func:`int` multiplies the values of the field set as chromStart and 
            chromEnd
        
        :return: self.data
        
        """
                
        # If fields is not set then I all the data columns are processed
        if fields is None:
            fields = self.fieldsG
            indexL = range(len(self.fieldsG))
        else:
            try:
                indexL = [self.fieldsG.index(f) for f in fields] 
                
            except ValueError:
                raise ValueError("Field '%s' not in file %s." % (f, self.path))
           
        idx_fields2rel = [10000000000000]
        print >>stderr, "Relative coordinates set to:", relative_coord 
           
        if relative_coord:             
                
            if fields2rel is None and intervals: 
                _f2rel = ["chromStart","chromEnd"] 
            elif fields2rel is None and not intervals:
                if "chromEnd" in self.fieldsG:
                    _f2rel = ["chromStart","chromEnd"] 
                else:
                    _f2rel = ["chromStart"]
                    
            else:
                if isinstance(fields2rel, basestring): fields2rel = [fields2rel]
                _f2rel = [f for f in fields2rel if f in self.fieldsG]
                
            try:
                idx_fields2rel = [self.fieldsG.index(f) for f in _f2rel]                
            except ValueError:
                raise ValueError("Field '%s' not in file %s mandatory when option relative_coord=T." % (f, self.path))
            
            self.data = self._time2rel_time(idx_fields2rel)
                
        idx_fields2int = [10000000000000]
        
        #TODO now fields is not doing anything!!!
        
#         return self.data
        return Track(self.data, self.fieldsG, dataTypes=self.dataTypes, list_tracks=self.tracks, range_values=self.range_values) #TODO assess whether there is any difference in this two lines of code

    def _time2rel_time(self, i_fields):
        """
        Calculates relative values of selected data columns 
        
        :param i_fields: :py:func:`list` with data columns to calculate relative values
        
        :return: list of tuples (like self.data)
        
        TODO check whether field for min and max is the same as the one selected by i_fields otherwise
        give either exception of warning
        
        """
        data_rel = list()
    
        for row in self.data:
            temp = []
            for i in range(len(row)):
                
                if i in i_fields:
                    temp.append(row[i]- self.min + 1)
                else:
                    temp.append(row[i])
    
            data_rel.append((tuple(temp)))   
            
        return (data_rel)
    