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

class IntData(object): 
    """
    Generic class for input data
    
    .. attribute:: path
    
       Name of path to a csv/tab input file
    
    .. attribute:: delimiter
    
       Character use to separate values of the same record in file (default "\t").
    
    .. attribute:: header
    
       Indicates the presence of a header.
       * `False` if there is no header. Fields should the be provided using fields param
       * `True` if the file have a header line with names. This names should match names in map_dict (default).
    
    .. attribute:: fieldsB
    
        List with the behavioral fields corresponding each column in the file
    
    .. attribute:: fieldsG_dict
    
        A dictionary with the equivalence to map fields in the input file and the pergola
        ontology to describe behavioral data    
    
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
        
    :returns: IntData object 
    """
    def __init__(self, path, map_dict, header=True, **kwargs):
        self.path = check_path(path)
        self._in_file = open(self.path, "rb")
        self.delimiter = self._check_delimiter(self.path, kwargs.get('delimiter', "\t"))
#         self.header = kwargs.get('header',True)
        self.header = header
        
        self._reader =  reader(self._in_file, delimiter=self.delimiter)
        
        self.fieldsB = self._set_fields_b(kwargs.get('fields_names', None))
        self.fieldsG_dict = self._set_fields_g(map_dict)
        self.fieldsG = self.fieldsG_dict.keys() #here before I added the new fields
        self.min = self.max = 0
        self.range_values = 0
        self.data = self._simple_read()        
#         self.data = self._read(multiply_t = kwargs.get('multiply_t', 1), intervals=kwargs.get('intervals', False))
        self.dataTypes = self.get_field_items(field ="dataTypes", data = self.data, default="a")
        self.tracks = self.get_field_items(field="track", data = self.data, default="1")#TODO maybe this function will be more general if instead of giving field name
        #i pass the index 
        
    def _check_delimiter (self, path, delimiter):
        """ 
        Check whether the set delimiter works, if delimiter not set then tries ' ', '\t' and ';'
         
        :param path: :py:func:`str` name of path to a behavioral file in the form of a csv file
        :param delimiter: :py:func:`str` delimiter used in the file ("tab", ";", "space") 
        
        :returns: delimiter
        
        """                
#         self.in_file  = open(path, "rb") #del eliminate path as an argument
        
        for row in self._in_file:
            
            #Delimiter set by user        
            if row.count(delimiter) >= 1: break
            else: raise ValueError("Input delimiter does not correspond to delimiter found in file \'%s\'"%(delimiter))
            
            #Delimiter guess by function       
            if row.count(" ") >= 1:
                self.delimiter = " "
                break
            if row.count("\t") >= 1:
                self.delimiter = "\t"
                break
            if row.count(";") >= 1:
                self.delimiter = ";"
                break      
        
        if delimiter is None: 
            raise ValueError("Delimiter must be set \'%s\'"%(delimiter))
        
        self._in_file.seek(0)
           
        return delimiter
    
    def _set_fields_b(self, fields=None):
        """
        Reading the behavioral fields from the header file or otherwise setting  
        the fields to numeric values corresponding the column index starting at 0
        
        :param None fields: :py:func:`list` with the behavioral fields corresponding each column in the file
        
        :returns: list with the behavioral fields
            
        """ 
#         self.in_file  = open(self.path, "rb")
#         self.reader =  reader(self.in_file, delimiter=self.delimiter)       
        
        fieldsB = []
        
        if self.header:            
            header = self._reader.next()
            first_r = self._reader.next()
            
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
#                 print "============= fields B all fields of header", fieldsB#del
#                 fieldsB = fields                     
            else:       
                fieldsB = [header[0].strip('# ')]+header[1:]        
        else:
            first_r = self._reader.next()
            
            if fields:
                if len(fields) > len(first_r):
                    raise ValueError("Input field list \"%s\" is longer than totals fields available in file \'%s\'" % ("\",\"".join(fields), len(first_r)))            
                            
                fieldsB = fields
                
                print ("WARNING: As header=False you col names set by fields will be considered to have the order "
                        "you provided: \"%s\"" 
                        %"\",\"".join(fields))                 
            else:                                
                raise ValueError ('File should have a header, otherwise you should set ' 
                                  'an ordered list of columns names using fields')     
                
#         self.in_file.close()
        self._in_file.seek(0)        
        
        return fieldsB
    
    def _set_fields_g (self, map_dict):
        """
        Extracts the correspondence of fields in genomic grammar of the behavioral file.
        
        :param map_dict: relationship between behavioral data fields and pergola ontology (:py:class:`dict`)
        
        :returns: list with the corresponding genomics names of the fields inside behavioral (input) data
         
        """
        dict_fields_g = {}
        i_field_b=0
        
        for field_B in self.fieldsB:
            if field_B:
                try:
                    map_dict [field_B]
                except KeyError:
                    raise KeyError ("Field %s is not mapped in your ontology mapping. " \
                                    "TIP: Fields that are not use from the input data have to be set to dummy " \
                                    "in the ontology mapping. Example: behavioural_file:%s > pergola:dummy"                               
                                    % (field_B, field_B))                                                                                                                        
                dict_fields_g[map_dict [field_B]] = i_field_b
            i_field_b = i_field_b + 1                    
        
        name_fields_g = [map_dict[k] for k in self.fieldsB if k]   
#         if all(field_b in map_dict for field_b in self.fieldsB):
#             name_fields_g = [map_dict [k] for k in self.fieldsB]
#         else:    
#             raise ValueError("Fields param \"%s\" contains a field not present in config_file \"%s\"" 
#                              % ("\",\"".join(self.fieldsB), "\",\"".join(map_dict.keys()))) #del 
#          YA ESTA HECVHO ARRIBA
        
        #Input file at least should have two fields that correspond to:
        mandatory_fields = ["chromStart", "dataValue"]
        
        if not all(f in dict_fields_g.keys() for f in mandatory_fields):
            raise ValueError("Input file mandatory fields  are \"chromStart\" and \"dataValue\" \n" \
                             "Your current assigned fields are \"%s\"\n" \
                             "TIP: Check your ontology_file"                               
                             % ("\",\"".join(name_fields_g)))            

        return dict_fields_g
    
    def _simple_read(self):
        """
        This function just needs to read the raw data set min and maximum, dataTypes and this stuff
        _read was too much complicated
        
        :returns: list with intervals contained in file, minimum and maximum values inside the file 
        """
        
        list_data = list()
        
        if self.header: self._reader.next()
        
        for row in self._reader:
            list_data.append(tuple(row)) #TODO what is better tuple or list 
        
        #Initialize min, max
        self.min, self.max = self._min_max(list_data)
        
        #Initialize range_values
        self.range_values = list(self._min_max(list_data,t_start="dataValue", t_end="dataValue"))
        
        # Back to file beginning
        self._in_file.seek(0)
        
        return (list_data)

#     def _read(self, multiply_t=1, intervals=False):
#         """
#         Reads the information inside the input file and returns minimun and maximun.
#         
#         :param 1 multiply: multiplies the values of the field set as chromStart and 
#             chromEnd
#         :param False intervals: if True pergola creates intervals from the field set
#             as chromStart, 
#         
#         :returns: list with intervals contained in file, minimum and maximum values inside the file 
#         
#         TODO add example of input file structure and the output of the function
#         
#         """
#         
#         list_data = list()
#         self.in_file  = open(self.path, "rb")
#         self.reader = reader(self.in_file, delimiter=self.delimiter)
#         
#         if self.header: self.reader.next()
#         
#         # Field assign to data value should be an integer or float
#         idx_dataValue = [self.fieldsG_dict["dataValue"]]
#         
#         _int_points = ["chromStart", "chromEnd"]
#         idx_fields2int = [10000000000000]
#         i_new_field = [10000000000000]                                    
#         
#         if intervals:             
#             print >>stderr, "Intervals will be inferred from timepoints"
#             _time_points = ["chromStart"]
#             f_int_end = "chromEnd"
#         
#             if f_int_end in self.fieldsG_dict:
#                 raise ValueError("Intervals can not be generated as '%s' already exists in file %s." % (f_int_end, self.path))
#                 
#             try:
#                 idx_fields2int = [self.fieldsG_dict[f] for f in _time_points]     
#             except ValueError:
#                 raise ValueError("Parameter intervals=True needs that field '%s' is not missing in file %s." 
#                                  % (f, self.path))
#             
#             i_new_field = len(self.fieldsB)
#             
#             print "new field index is:", i_new_field
#             self.fieldsG_dict[f_int_end] = i_new_field
#             
#             i_new_field = [i_new_field]
#         
#         try:            
#             f=""
#             name_fields2mult = [f for f in _int_points if f in self.fieldsG_dict] 
#             idx_fields2mult = [self.fieldsG_dict[f] for f in name_fields2mult]                
#         except ValueError:
#             raise ValueError("Field '%s' not in file %s." % (f, self.path))
#         
#         p_min = None
#         p_max = None
#         
#         _start_f = ["chromStart"]
#         
#         try:
# #             i_min = [self.fieldsG_dict.index(f) for f in _start_f]
#             i_min = [self.fieldsG_dict[f] for f in _start_f]              
#         except KeyError:
#             raise KeyError("Field '%s' for min interval calculation time not in file %s." % (f, self.path))
#             
#         _end_f = ["chromEnd"]
#         
#         try:
#             i_max = [self.fieldsG_dict[f] for f in _end_f]              
#         except KeyError:
#             raise KeyError("Field '%s' for max interval calculation time not in file %s \n" \
#                              "TIP: If your file contains timepoints you can transform them to intervals" \
#                              " setting the field containing them to chromStart and setting intervals=True" 
#                              % (f, self.path))
#         
#         # Range of dataValue field
#         p_min_data_v = None
#         p_max_data_v = None
#         
#         _start_f = ["dataValue"]
#         
#         try:
#             i_data_value = [self.fieldsG_dict[f] for f in _start_f]
#         except ValueError:
#             raise ValueError("Field '%s' for dataValue range calculation time not in file %s." % (f, self.path))
#         
#         v = 0
#         p_v = 0
#         first = True
#         p_temp = []
#                 
#         # Setting the factor to multiply if it is not set by the user
#         # different to 1 and the timepoints are decimal numbers
#         if multiply_t == 1:
#             
#             n = 0
#             file_int = open(self.path, "rb")
#             test_decimal = reader(file_int, delimiter=self.delimiter)
#             test_decimal.next()        
#             max_dec_len = 0
#             pattern_dec_p = '\.|\,'
#             
#             for r in test_decimal:            
#                 n = n + 1
#                 if n == 200 :
#                     break               
#                 for i in sorted(self.fieldsG_dict.values()):
#                     if  i in idx_fields2int or i in idx_fields2mult and i not in i_new_field:
#                         if search(pattern_dec_p, r[i]):
#                             dec_len = len(split(pattern_dec_p, r[i])[1])
#                             if max_dec_len < dec_len: max_dec_len = dec_len 
#             
#             file_int.close()                
#             multiply_t = pow(10, max_dec_len)
#             
#             # If the value of multiply has been changed then I report it to the usert to
#             # give the info of how to set the value #COPIAR
#             if multiply_t != 1:
#                 print ("Factor to transform time values has been set to %s. "%multiply_t)
#                 print ("pergola set this parameter because values in chromStart are decimals.\n"  
#                        "You can set your own factor using option -mi,--multiply_intervals n")        
#         
#         # If track exists data is order by track, this way I can avoid having problems 
#         # at the last interval
#         _track_f = "track"
#         tr_change = False
#         tr = ""
#         p_tr = ""
#         i_track = None
# 
#         if _track_f in self.fieldsG_dict:
#             i_track = self.fieldsG_dict[_track_f]
#             
#             #             self.reader = sorted(self.reader, key=itemgetter(*[i_track]))
# 
#             # Checking whether first track is numeric, if it is code assumes all tracks
#             # are numeric and sort consequently  
#             file_int = open(self.path, "rb")
#             test_numeric = reader(file_int, delimiter=self.delimiter)
#             test_numeric.next()
#             first_row = test_numeric.next()
#             if first_row[i_track].isdigit():
#                 # Force numerical sorting
#                 self.reader = sorted(self.reader, key=lambda x: (int(x[i_track]), int(x[i_min[0]])))
#             else:
#                 self.reader = sorted(self.reader, key=itemgetter(i_track, i_min[0]))  
#             
#         for interv in self.reader: 
#             temp = []
# 
#             for i in sorted(self.fieldsG_dict.values()):
#                 if i_track and i ==  i_track:
#                     if first:
#                         tr = interv[i]
#                         p_tr = interv[i] 
#                         pass
#                     tr = interv[i]
# #                     print "tr ----- p_tr@@@@@@@@@@@@@@@@", tr, p_tr
# #                     if tr != p_tr:
# #                         print "tr ----- p_tr@@@@@@@@@@@@@@@@", tr, p_tr#del
# #                         tr_change = True
# #                     else:
# #                         tr_change = False
# #                     p_tr = interv[i]
#                     
#                 # Field assign to data value should be an integer or float        
#                 if i in idx_dataValue:                    
#                     try:                        
#                         float(interv[i])
#                     except ValueError:
#                         raise ValueError("Values in dataValue should be numerical not others: \"%s\".\n" %
#                                           interv[i])
#                 if i in idx_fields2int:
#                     try:
#                         float(interv[i])
#                     except ValueError:
#                         raise ValueError("Values set as chromStart and chromEnd should be numerical not others: \"%s\".\n" %
#                                           interv[i])
#                         
#                 if i in idx_fields2mult and i in idx_fields2int:        
#                     a = round (float(interv[i]) * multiply_t, 6)
#                     
#                     b = int(a)
# 
#                     if a-b != 0:
#                         raise ValueError ("Intervals values (chromStart and chromEnd)can not be decimal\nPlease set a bigger factor " \
#                                           "using -m,--multiply_intervals flag to multiply your values, current value is %s"%multiply_t)                                                
#                     v = int(float(interv[i]) * multiply_t)
#                     
#                     print "I append here in temp******************", v #del
#                     temp.append(v)
#                     p_v = v - 1 
#                     print "===========", intervals, p_v, v #del
#                     # detectar cuando cambia de track, if last no append
#                     # hacer un bed de 4 lineas para trabajar
#                     
#                     if intervals: last_start = v
#                     
#                 elif i in i_new_field and i in idx_fields2mult:
#                     if first:                                                 
#                         pass
#                     else:
#                         if tr != p_tr:
#                             #print "Track change>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>!!!!!", tr, p_tr, p_v, v #del
# #                             print "Track change>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>!!!!!", p_temp[1] #del
#                             p_temp.append(p_temp[1] + 1)  
#                             p_tr = tr
#                         else:    
# #                             print "tr_change is set to ", tr_change
# #                             print "appending p_v here", p_v #del #Creo que esta aqui OJO
# #                             print "If I put v it would be", v#del                   
#                             p_temp.append(p_v)  
# #                         p_temp.append(0)  
#                                               
#                 elif i in idx_fields2mult and i not in idx_fields2int:
#                     a = round (float(interv[i]) * multiply_t, 6)
#                     b = int(a)
#                     if a-b != 0:
#                         raise ValueError ("Intervals values (chromStart and chromEnd)can not be decimal\nPlease use a bigger factor " \
#                                           "using -m,--multiply_intervals flag to multiply your values, current value is %s"%multiply_t)          
#                     
#                     v = int(float(interv[i]) * multiply_t)
#                     # print "appending v here", v #del 
#                    
#                     if tr != p_tr:
#                         #print "Track change>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>!!!!!", p_temp #del
#                         #print "p_v is:::::::::::", v #del
#                         temp.append(v)
#                         p_tr = tr
#                     else:
#                         p_tr = tr    
#                         temp.append(v)
#                 
#                 else:
#                     v = interv[i]              
#                     temp.append(v)
#                 
#                 if i in i_min:
#                     if p_min is None: p_min = v
#                     if p_min > v: p_min = v                    
#                 
#                 if i in i_max:
#                     if i_max == i_new_field:
#                         if first: pass
#                         if p_max is None: p_max = p_v
#                         if p_max < p_v: p_max = p_v
#                     else:
#                         if p_max is None: p_max = v
#                         if p_max < v: p_max = v
#                 
#                 if i in i_data_value:
#                     v = float(v)                    
#                     if p_min_data_v is None: p_min_data_v = v
#                     if p_min_data_v > v: p_min_data_v = v
#                     if p_max_data_v is None: p_max_data_v = v
#                     if p_max_data_v < v: p_max_data_v = v
#                 
#             if first:
#                 first = False 
#                 p_temp = temp
#             else:               
#                 list_data.append((tuple(p_temp))) 
#                 p_temp = temp
#             
#         # last line of the file when intervals are generated
# #         print "intervals is set to **********", intervals #del
#         if intervals:
#             #print "este hace lo mismo para el ultimo intervalo************************$$$$$$$$", last_start #del
#             temp.append(last_start + 1)
# 
#         list_data.append((tuple(temp)))             
# 
#         self.in_file.close()
#         
#         self.min = p_min
#         self.max = p_max
#         self.range_values = [p_min_data_v, p_max_data_v]
#         
#         #Setting the data fields that output data have in the order they are
#         data_fields = []
#         
#         sorted_index_f = sorted(self.fieldsG_dict.items(), key=itemgetter(1))
#         for field_gen in sorted_index_f:
#             data_fields.append(field_gen[0])
#         self.fieldsG = data_fields
#         
# #         DataIter(self._read(indexL, idx_fields2rel, idx_fields2int, l_startChrom, l_endChrom, multiply_t), self.fieldsG)
# #         return (list_data, p_min, p_max)
#         return (list_data)
    
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
            
        :returns: set with unique values inside field
        
        """

        set_fields = set()
        
        if field in self.fieldsG:
#             i =  self.fieldsG.index(field)
#             i = self.fieldsG_dict[field]
#             print "intervals.py &&&&&&&&&&&&&&&&&&&&&&&&", field, i#del
            
            idx_field = self.fieldsG_dict[field]
            field = [field]    
#             print "intervals.py &&&&&&&&&&&&&&&&&&&&&&&&", field, idx_field#del
            
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
            pos = len(self.fieldsG)
            self.fieldsG.append(str(field))
            self.fieldsG_dict[field]=pos
        else:
            raise ValueError("Data has not field \'%s\' and no default value has been set \'%s\'"%(field, default)) 
        
#         print "intervals.py &&&&&&&&&&&&&&&&&&&&&&&&", field,set_fields#del 
        return set_fields
    
    def read(self, fields=None, relative_coord=False, intervals=False, fields2rel=None, multiply_t=None,**kwargs):
        """        
        Reads the data and converts it depending on selected options
        
        :param fields: :py:func:`list` with data columns to read
        :param False relative_coord: If true all coordinates in chromStart and chromEnd are
            make relative to the minimal value
        :param False intervals: if set to true intervals will be inferred from timepoints in
            chromStart 
        :param fields2rel: :py:func:`list` with data columns to make relative
        :param multiply_t: :py:func:`int` multiplies the values of the field set as chromStart and 
            chromEnd
        
        :returns: Track object
        
        TODO: By the moment I make this function as a method of the closs eventually I would make this a
        separated function
        Eventually do not change self.data but a list inside read and return the Track object with the modifications
        this way data is always the original one.
        """
        _f_rel_mand = "chromStart"
        _f_int_end = "chromEnd"
        _f2rel = ["chromStart","chromEnd"]
        _f2mult = ["chromStart","chromEnd"]
        i_time_f = [10000000000000]
        
        #If fields is not set then all the data columns are read
        if fields is None:
            fields = self.fieldsG
            indexL = range(len(self.fieldsG))
        else:
            try:
                indexL = [self.fieldsG.index(f) for f in fields] 
                 
            except ValueError:
                raise ValueError("Field '%s' not in file %s." % (f, self.path))
        
        # If chromStart not present out     
        try:
 
            idx_fields2int = self.fieldsG_dict[_f_rel_mand] 
        except ValueError:
            raise ValueError("Parameter intervals=True needs that field '%s' is not missing in file %s." 
                             % (_f_rel_mand, self.path))
                                            
        ##################################
        # If there are several tracks we order by track
        # Control for interval change bw tracks        
        _f_track = "track"
        i_track = None
        
        if _f_track in self.fieldsG_dict:
            i_track = self.fieldsG_dict[_f_track]
            
            if all(row[i_track].isdigit() for row in self.data):                
                self.data = sorted(self.data, key=lambda x: (int(x[i_track]), x[idx_fields2int]))
            else:
                self.data = sorted(self.data, key=itemgetter(i_track, idx_fields2int))
                            
        # Coordinates multiplied by a given factor set by the user
        if multiply_t:
            print >>stderr, "Fields containing time points will be multiplied by: ", multiply_t 
            
            try:            
                f=""
                name_fields2mult = [f for f in _f2mult if f in self.fieldsG_dict] 
                idx_fields2mult = [self.fieldsG_dict[f] for f in name_fields2mult]                
            except ValueError:
                raise ValueError("Field '%s' not in file %s." % (f, self.path))
            
            self.data = self._multiply_values(i_fields=idx_fields2mult, factor=multiply_t)
            
        # Coordinates transformed into relative to the minimun time point
        print >>stderr, "Relative coordinates set to:", relative_coord
                
        if relative_coord:
            if fields2rel is None:
                # Do I have intervals or single points
                f2rel = list(set(_f2rel) & set(self.fieldsG))
                if f2rel is None: 
                    raise ValueError("You need at least a field containing time points when relative_coord=T. %s" % (self.fieldsG))
                
            else:
                # Are the provided fields present in data and are numeric #TODO en realidad si no es numerico ya petara
                if isinstance(fields2rel, basestring): fields2rel = [fields2rel]
                f2rel = [f for f in fields2rel if f in self.fieldsG]
            
            # Getting indexes of fields to relativize
            try:
                i_time_f = [self.fieldsG_dict[f] for f in f2rel]                
            except ValueError:
                raise ValueError("Field '%s' not in file %s mandatory when option relative_coord=T." % (f, self.path))

            self.data = self._time2rel_time(i_time_f)
        
        # From only start value for each time point we generate intervals
        if intervals:
            print >>stderr, "Intervals will be inferred from timepoints"
            
            # If chromend is present ERROR
#             _time_points = ["chromStart"]#del
#         _f_rel_mand#del
            if _f_int_end in self.fieldsG_dict:
                raise ValueError("Intervals can not be generated as '%s' already exists in file %s." % (_f_int_end, self.path))
                        
            self.data = self._create_int(idx_fields2int)
        
        # To continue intervals are mandatory
        try:
            i_max = self.fieldsG_dict[_f_int_end]              
        except KeyError:
            raise KeyError("Field '%s' for max interval calculation time not in file %s. " \
                           "TIP: You can transform timepoints to intervals setting intervals=True"                         
                           % (_f_int_end, self.path))
 
        # Updated and order list of the fields        
        list_fields = [None] * len(self.fieldsG_dict)
#         print "length of the dictionary",len(self.fieldsG_dict)#del
        
#         print "======================", self.fieldsG#del
#         print "======================", self.fieldsG_dict#del
        
        for field, i in self.fieldsG_dict.iteritems():
            list_fields[i] = field
            
        self.fieldsG = list_fields
        
        return Track(self.data, self.fieldsG, dataTypes=self.dataTypes, list_tracks=self.tracks, range_values=self.range_values, min=self.min, max=self.max) 
       
#     def read(self, fields=None, relative_coord=False, intervals=False, fields2rel=None, multiply_t=1,**kwargs):
#         """        
#         Reads the data and converts it depending on selected options
#         
#         :param fields: :py:func:`list` with data columns to read
#         :param False relative_coord: If true all coordinates in chromStart and chromEnd are
#             make relative to the minimal value
#         :param False intervals: if set to true intervals will be inferred from timepoints in
#             chromStart 
#         :param fields2rel: :py:func:`list` with data columns to make relative
#         :param 1 multiply: :py:func:`int` multiplies the values of the field set as chromStart and 
#             chromEnd
#         
#         :returns: Track object
#         """
#                 
#         # If fields is not set then I all the data columns are processed
#         if fields is None:
#             fields = self.fieldsG
#             indexL = range(len(self.fieldsG))
#         else:
#             try:
#                 indexL = [self.fieldsG.index(f) for f in fields] 
#                 
#             except ValueError:
#                 raise ValueError("Field '%s' not in file %s." % (f, self.path))
#            
#         idx_fields2rel = [10000000000000]
#         print >>stderr, "Relative coordinates set to:", relative_coord 
#            
#         if relative_coord:             
#                 
#             if fields2rel is None and intervals: 
#                 _f2rel = ["chromStart","chromEnd"] 
#             elif fields2rel is None and not intervals:
#                 if "chromEnd" in self.fieldsG:
#                     _f2rel = ["chromStart","chromEnd"] 
#                 else:
#                     _f2rel = ["chromStart"]
#                     
#             else:
#                 if isinstance(fields2rel, basestring): fields2rel = [fields2rel]
#                 _f2rel = [f for f in fields2rel if f in self.fieldsG]
#                 
#             try:
#                 idx_fields2rel = [self.fieldsG.index(f) for f in _f2rel]                
#             except ValueError:
#                 raise ValueError("Field '%s' not in file %s mandatory when option relative_coord=T." % (f, self.path))
#             
#             self.data = self._time2rel_time(idx_fields2rel)
#                 
#         idx_fields2int = [10000000000000]
#         
# #         return self.data
#         return Track(self.data, self.fieldsG, dataTypes=self.dataTypes, list_tracks=self.tracks, range_values=self.range_values) #TODO assess whether there is any difference in this two lines of code
    
    def _min_max(self, list_data, t_start="chromStart", t_end="chromEnd"):
        """
        TODO Documentation
        """
         # Min and maximun time points
        t_min = None
        t_max = None
        
        i_time = self.fieldsG_dict[t_start]
        
        t_min = float(min(list_data, key=itemgetter(i_time))[i_time])
        
        if t_end in self.fieldsG_dict.keys():
            i_time = self.fieldsG_dict[t_end]
        
        t_max = float(max(list_data, key=itemgetter(i_time))[i_time])
        
        if t_min.is_integer(): 
            t_min = int(t_min)
        else:
            t_min = t_min
        
        if t_max.is_integer(): 
            t_max = int(t_max)
        else:
            t_max = t_max
        
        return (t_min, t_max)
    
    def _time2rel_time(self, i_fields):
        """
        Calculates relative values of selected data columns 
        
        :param i_fields: :py:func:`list` with data columns to calculate relative values
        
        :returns: list of tuples (self.data-like)
        
        TODO check whether field for min and max is the same as the one selected by i_fields otherwise
        give either exception of warning
        I have two problems with this, first that if i have intervals min will be only in one of the two
        fields set for convert into relative.
        The second problem is that the min is read far before here is where I have to check this
        In principal this should be always in chromStart that is why I have the terms in the ontology!!!!!
        
        """
        data_rel = list()
    
        for row in self.data:
            temp = []
            for i in range(len(row)):
                
                if i in i_fields:
                    
                    if is_number(row[i]):
                        n = float(row[i])
                        
                        if n % 1 == 0:                        
#                             temp.append(int(row[i])- self.min + 1)
                            temp.append(int(row[i])- self.min)
                        else: 
                            raise ValueError("Value can not be relativize because is not an integer \'%.16f\'" \
                                            ". Use option -mi,--multiply_intervals n"%(row[i]))  #correct this is only true for pergola_rules
                else:
                    temp.append(row[i])
    
            data_rel.append((tuple(temp)))   
        
        self.min, self.max = self._min_max(data_rel)    
        
        return (data_rel)

    def _multiply_values(self, i_fields, factor=1):
        """
        Multiplicate values of selected data columns by the given factor
        
        :param i_fields: :py:func:`list` with data columns to calculate relative values
        
        :param factor: :py:func:`int` factor to multiply data columns selected
        
        :returns: list of tuples (self.data-like)
        
        TODO change min and max of the data to new values
        The simpler way is multiply this values as well
        I don't need to generate a temporal list do I?
        For this think maybe is better to have a list of list than a list of tupple
        """
        data_mult = list()
                
        for row in self.data:
            temp = []
            for i in range(len(row)):
                
                if i in i_fields:
                    value = row[i]
#                     value = row[i].replace(" ", "")
                                        
                    if is_number(value):
                        v_m = round (float(row[i]) * factor, 6)
                        v_i = int(v_m)
                        if v_m-v_i != 0:
                            raise ValueError ("Intervals values (chromStart and chromEnd) can not be decimal\nPlease use a bigger factor " \
                                              "with -m,--multiply_intervals flag to multiply your values, current value is %s"%factor)
                        temp.append(v_m)
                        
                    else: 
                        raise ValueError("Value can not be multiplied because is not a number \'%s\'" \
                                            "\nCheck mapping of fields in your input file n"%(row[i]))  #corregir    
                else:
                    temp.append(row[i])
    
            data_mult.append((tuple(temp)))             
        
        self.min, self.max = self._min_max(data_mult)
        
        return (data_mult) #Correct eventually self.data in a list of list directly modificable

    def _create_int(self, start_int):
        """
        From single time points generates intervals of time
        
        :param start_int: :py:func:`int` with index containing time points 
        
        :returns: list of tuples (self.data-like)
        """
        data_int = list()
        _f_int_end = "chromEnd"
        
        #Field is add as supplementary column
        end_int = len(self.fieldsG)      
        self.fieldsG_dict[_f_int_end] = end_int
        self.fieldsG.append(_f_int_end)
        
        #I have to check whther track field exist
        #if exist then bw tracks I have a last row 
        _f_track = "track"
        i_track = None
        track_sw = False
        
        if _f_track in self.fieldsG_dict:
            i_track = self.fieldsG_dict[_f_track]
#             p_track = self.data[0][i_track]
            track_sw = True
        
#         if tr != p_tr:
#             lfl
            
        #All items except last
        for i in range(len(self.data[:-1])):
#             if p_track and p_track == self.data[i][i_track]:
            
            row = self.data[i]
            
            if track_sw:
                if row[i_track] == self.data[i+1][i_track]:
                    value_end = (self.data[i+1][start_int]-1,)                    
                else:
                    value_end = (row[start_int] + 1,)
                                    
            else:
                value_end = (self.data[i+1][start_int]-1,)
            
            temp = row + value_end 
            data_int.append((tuple(temp)))
                
        #Last item
        last_row = self.data[-1]
        value_end = (last_row[start_int] + 1,)
        temp = last_row + value_end
        
        data_int.append((tuple(temp)))
            
        return (data_int)  
       
def is_number(var):
    """
    Checks whether an string is a number, if is already an integer or float it also returns True
    
    :param factor: :py:func:`str` :py:func:`int` :py:func:`float` variable to check
    
    :returns: :py:func:`boolean` True when input variable is a number otherwise False
    """
    try:
        float(var)
        return True
    except ValueError:
        return False