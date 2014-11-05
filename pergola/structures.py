from input import check_path
from csv   import reader
from os import getcwd
from os.path import join
from sys import stderr
from operator import itemgetter
from itertools import groupby

_genome_file_ext = ".fa"
_generic_nt = "N"

#Contains class and file extension
_dict_file = {'bed' : ('Bed', 'track_convert2bed', '.bed'),              
              'bedGraph': ('BedGraph', 'track_convert2bedGraph', '.bedGraph'),
              'txt': ('DataIter', '', '.txt')}

_black_gradient = ["226,226,226", "198,198,198", "170,170,170", "141,141,141", "113,113,113", "85,85,85", "56,56,56", "28,28,28", "0,0,0"]
_blue_gradient = ["229,229,254", "203,203,254", "178,178,254", "152,152,254", "127,127,254", "102,102,254", "76,76,173", "51,51,162", "0,0,128"]
_red_gradient = ["254,172,182", "254,153,162", "254,134,142", "254,115,121", "254,96,101", "254,77,81", "254,57,61", "254,38,40", "254,19,20"]
_green_gradient = ["203,254,203", "178,254,178", "152,254,152", "127,254,127", "102,254,102", "76,254,76", "51,254,51", "0,254,0", "25,115,25"]

_dict_colors = {
                'black' : _black_gradient,
                'blue' : _blue_gradient,
                'red' : _red_gradient,
                'green' : _green_gradient}

_intervals = [0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 1, 1000]

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
        List with the genimic fields corresponding each column in the file    
    
    .. attribute:: data
        List of tuples containing the data read from the file
    
    .. attribute:: min
        First time value in the file. Read from field set as "chromStart"
    
    .. attribute:: max
        Last timepoint in the file. Read from field set as "chromEnd"
    
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
        self.fieldsB = self._set_fields_b(kwargs.get('fields'))
        self.fieldsG = self._set_fields_g(ontology_dict)
        self.min = self.max = 0
        self.data = self._read(multiply_t = kwargs.get('multiply_t', 1), intervals=kwargs.get('intervals', False))
        self.dataTypes = self.get_field_items(field ="dataTypes", data = self.data, default="a")
        self.tracks  =  self.get_field_items(field="track", data = self.data, default="1")
        
    def _check_delimiter (self, path, delimiter):
        """ 
        Check whether the delimiter works, if delimiter is not set then tries ' ', '\t' and ';'
         
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
        
        #Input file at least should have two fields that correspond to:
        mandatory_fields = ["chromStart", "dataValue"]
        
        if not all(f in name_fields_g for f in mandatory_fields):
            raise ValueError("Input file mandatory fields  are \"chromStart\" and \"chromEnd\" \n" \
                             "Your current assigned fields are \"%s\"\n" \
                             "TIP: Check your ontology_file"                               
                             % ("\",\"".join(name_fields_g)))
        
        return name_fields_g
    
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
        self.reader.next()
        
        # Field assign to data value should be an integer or float
        idx_dataValue = [self.fieldsG.index("dataValue")]
         
        _int_points = ["chromStart", "chromEnd"]
        idx_fields2int = [10000000000000]
        i_new_field = [10000000000000]                                    
        
        if intervals:             
            print >>stderr, "Intervals will be inferred from timepoints"
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
            raise ValueError("Field '%s' for max interval calculation time not in file %s \n" \
                             "TIP: If your file contains timepoints you can transform them to intervals" \
                             " setting the field containing them to chromStart and setting intervals=True" 
                             % (f, self.path))
              
        v = 0
        p_v = 0
        first = True
        p_temp = []
        
        for interv in self.reader:            
            temp = []            
                                    
            for i in range(len(self.fieldsG)): 
                               
                # Values in idx_fields2int have to be integers
                if i in idx_fields2int:
                    a = int(float(interv[i]) * multiply_t)
                    b = float(interv[i]) * multiply_t
                    if a-b != 0:
                        raise ValueError ("Values in chromStart and chromEnd should be integers.\n" \
                                        "TIP: If you have to transform value from lets say " \
                                        "seconds to miliseconds try using multiply_t.")

                # Field assign to data value should be an integer or float        
                if i in idx_dataValue:                    
                    try:
                        float(interv[i])
                    except ValueError:
                        raise ValueError("Values in dataValue should be numerical not others: %s.\n" %
                                          interv[i]) 
                
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
        
        self.min = p_min
        self.max = p_max
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
            
#             print idx_fields2rel#del
            self.data = self._time2rel_time(idx_fields2rel)
                
        idx_fields2int = [10000000000000]
        
#         return self.data
        return DataIter(self.data, self.fieldsG, dataTypes=self.dataTypes) #TODO assess whether there is any difference in this two lines of code

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
                    temp.append(row[i]- self.min)
                else:
                    temp.append(row[i])
    
            data_rel.append((tuple(temp)))   
            
        return (data_rel)

#     def convert(self, mode='bed', **kwargs):
#         """
#         Calls function to convert data (as a list of tuples) into a dictionary of 
#         the one or several object of class set by mode
#         
#         :param bed mode: class of the output objects returned set to `bed` by
#             default
#                 
#         :return: dictionary containing object/s of the class set by mode 
#         
#         """
#         kwargs['relative_coord'] = kwargs.get("relative_coord",False)
#         
#         print >> stderr, self.fieldsG         
#         
#         if mode not in _dict_file: 
#             raise ValueError("Mode \'%s\' not available. Possible convert() modes are %s"%(mode,', '.join(['{}'.format(m) for m in _dict_file.keys()])))
#         
# #         dict_tracks = (self._convert2single_track(self._read(**kwargs), mode, **kwargs)) #TODO
#         dict_tracks = (self._convert2single_track(self._read(), mode, **kwargs)) 
# #         dict_tracks = (self._convert2single_track(self.data, mode, **kwargs)) #TODO
#         
#         return (dict_tracks)
#         
#     def _convert2single_track (self, data_tuples,  mode=None, **kwargs):
#         """
#         Split data (as a list of tuples) into one or several objects depending on options 
#         selected. Each object will correspond to a track in the genome browser
#         
#         :param data_tuples: list of tuples containing data
#         :param None mode: class of each single track that will be hold in dictionary
#             
#         :return: dictionary of tracks
#         
#         """   
#         dict_split = {}
#         
#         ### Data is separated by track and dataTypes
#         idx_fields2split = [self.fieldsG.index("track"), self.fieldsG.index("dataTypes")]
#         data_tuples = sorted(data_tuples, key=itemgetter(*idx_fields2split))
#         
#         for key,group in groupby(data_tuples, itemgetter(*idx_fields2split)):
#             if not dict_split.has_key(key[0]):
#                 dict_split [key[0]] = {}
#             dict_split [key[0]][key[1]] = tuple(group)
#         
#         ### Tracks not set in tracks option are filtered out
#         sel_tracks = []
#         if not kwargs.get('tracks'):
#             pass
#         else:
#             sel_tracks = map(str, kwargs.get("tracks",[]))
#                 
#         ### When any tracks are selected we consider that no track should be removed
#         if sel_tracks != []:
#             tracks2rm = self.tracks.difference(sel_tracks)            
#             dict_split = self.remove (dict_split, tracks2rm)
#             print >> stderr, "Removed tracks are:", ' '.join(tracks2rm)
#         
#         d_track_merge = {} 
#         
#         ### If tracks_merge is set we combine tracks selected                 
#         if not kwargs.get('tracks_merge'):
#             d_track_merge = dict_split
#         else:
#             tracks_merge = kwargs.get('tracks_merge',self.tracks)
#             if not all(tracks in self.tracks for tracks in tracks_merge):
#                 raise ValueError ("Tracks to merge: %s, are not in the track list: " % 
#                                   ",".join("'{0}'".format(n) for n in tracks_merge), 
#                                   ",".join("'{0}'".format(n) for n in self.tracks))
#             print >> stderr, ("Tracks that will be merged are: %s" %  " ".join(tracks_merge))
#             
#             d_track_merge = self.join_by_track(dict_split, tracks_merge)       
#         
#         d_dataTypes_merge = {}
#         
#         ### If set we join the dataTypes or natures
#         if not kwargs.get('dataTypes_actions') or kwargs.get('dataTypes_actions') == 'one_per_channel':
#             d_dataTypes_merge = d_track_merge
#         elif kwargs.get('dataTypes_actions') == 'all':
#             d_dataTypes_merge = self.join_by_dataType(d_track_merge, mode)
#     
#         track_dict = {}                        
#    
#         
#         ### Generating track dict (output)
#         #validacion del diccionario para imprimir o lo que sea
#         #mirar si es un diccionario de diccionarios la primera validacion hay que desarrolarla 
#         for k, v in d_track_merge.items():
#             if isinstance(v,dict):
#                 print "Is a dictionary"#del
#                                    
#         window = kwargs.get("window", 300)
#         
#         ### Assigning data to output dictionary    
#         for k, d in d_dataTypes_merge.items():
#             for k_2, d_2 in d.items():
#                 track_dict[k,k_2] = globals()[_dict_file[mode][0]](getattr(self,_dict_file[mode][1])(d_2, True, window), track=k, dataType=k_2)
#                        
#         return (track_dict)
#     
#     
#     def remove (self, dict_t, tracks2remove):
#         """
#         Removes selected tracks from a dictionary of tracks that is the input of the function those that are 
#         set by tracks2remove
#         
#         :param dict_t: py:func:`dict` dictionary containing one or more tracks, keys represent each 
#             of these tracks
#         :param tracks2remove: :py:func:`list` of tracks to remove from the dict_t
#              
#         :return: dict_t dictionary, that contains the remaining tracks
#         
#         #TODO I can make this function more general as remove from dictionary it can be use outside
#         
#         """
#         for key in tracks2remove:
#             key = str(key)
#     
#             dict_t.pop(key, None)
#     
#             if key in self.tracks:
#                 self.tracks.remove(key)
#                 
#         return (dict_t)
#     
#     def join_by_track(self, dict_t, tracks2join):  
#         """
#         Join tracks by track name or id 
#         
#         :param dict_t: py:func:`dict` containing one or more tracks, keys 
#             represent each of these tracks
#         :param tracks2join: :py:func:`list` of tracks to join in a single track
#              
#         :return: d_track_merge dictionary that contains the joined tracks
#         
#         TODO What if I give to the function only some tracks to join, what happen
#             to the remaining tracks
#          
#         """
#         
#         d_track_merge = {} 
#         new_tracks = set()
#         
#         for key, nest_dict in dict_t.items():
#             
#             if key not in tracks2join: 
#                 print "Track not use because was not set when join_by_track is called: %s" % key
#                 continue
#             
#             if not d_track_merge.has_key('_'.join(tracks2join)):
#                 d_track_merge['_'.join(tracks2join)] = {}
#                 new_tracks.add('_'.join(tracks2join))
#             
#             for key_2, data in nest_dict.items():                            
#                 if not d_track_merge['_'.join(tracks2join)].has_key(key_2):
#                     d_track_merge['_'.join(tracks2join)] [key_2]= data
#                 else:  
#                     d_track_merge['_'.join(tracks2join)] [key_2] = d_track_merge['_'.join(tracks2join)] [key_2] + data
# 
#         self.tracks = new_tracks
#                    
#         return (d_track_merge)
#     
#     
#     def join_by_dataType (self, dict_d, mode):
#         """
#         Join tracks by dataType
#         
#         :param dict_d: py:func:`dict` containing one or more tracks, primary key 
#             are tracks id and secondary tracks are dataTypes
#         :param mode: :py:func:`str` class of the object that is going to be 
#             generated
#              
#         :return: d_dataTypes_merge dictionary that contains the joined tracks
#          
#         """
#         d_dataTypes_merge = {}
#         
#         for key, nest_dict in dict_d.items():
#             
#             d_dataTypes_merge[key] = {}
#             new_dataTypes = set()
#             
#             for key_2, data in nest_dict.items(): 
#                 
#                 if not d_dataTypes_merge[key].has_key('_'.join(nest_dict.keys())):
#                     d_dataTypes_merge[key]['_'.join(nest_dict.keys())] = data
#                     new_dataTypes.add('_'.join(nest_dict.keys())) 
#                 else:                    
#                     d_dataTypes_merge[key]['_'.join(nest_dict.keys())] = d_dataTypes_merge[key]['_'.join(nest_dict.keys())] + data
#                     new_dataTypes.add('_'.join(nest_dict.keys()))          
#         
#         #New dataTypes only set if objects is bedGraph. Bed objects needs to 
#         #know all original dataTypes to display them with different colors
#         if mode == 'bedGraph':
#             self.dataTypes = new_dataTypes
# 
#         return (d_dataTypes_merge)
#     
#     def track_convert2bed(self, track, in_call=False, restricted_colors=None, **kwargs):
#         """
#         Converts a single data belonging to a single track in a list of tuples in
#         an object of class Bed
#         
#         :param track: :py:func:`list` of tuples containing data of a single track
#         :param False in_call: If False the call to the function is from the user otherwise
#             is from inside :py:func: `convert2single_track()`
#         :param None restricted_colors: Set colors not to be used #TODO this is not clear example??
#              
#         :return: Bed object
#         
#         """
#         
#         #This fields are mandatory in objects of class Bed
#         _bed_fields = ["track","chromStart","chromEnd","dataTypes", "dataValue"]
#         
#         #Check whether these fields are in the original otherwise raise exception
#         try:
#             [self.fieldsG.index(f) for f in _bed_fields]
#         except ValueError:
#             raise ValueError("Mandatory field for bed creation '%s' not in file %s." % (f, self.path))
# 
#         if (not in_call and len(self.tracks) != 1):
#             raise ValueError("Your file '%s' has more than one track, only single tracks can be converted to bed" % (self.path))
#         
#         i_track = self.fieldsG.index("track")
#         i_chr_start = self.fieldsG.index("chromStart")
#         i_chr_end = self.fieldsG.index("chromEnd")
#         i_data_value = self.fieldsG.index("dataValue")
#         i_data_types = self.fieldsG.index("dataTypes")
#         
#         #Generate dictionary of field and color gradients
#         _dict_col_grad = assign_color (self.dataTypes)
#             
#         for row in track:
#             temp_list = []
#             temp_list.append("chr1")
#             temp_list.append(row[i_chr_start])
#             temp_list.append(row[i_chr_end])
#             temp_list.append(row[i_data_types]) 
#             temp_list.append(row[i_data_value])   
#             temp_list.append("+")
#             temp_list.append(row[i_chr_start])
#             temp_list.append(row[i_chr_end])
#             for v in _intervals:
#                 if float(row[i_data_value]) <= v:
#                     j = _intervals.index(v)
#                     d_type = row [self.fieldsG.index("dataTypes")]
#                     color = _dict_col_grad[d_type][j]
#                     break
#             temp_list.append(color)          
#             
#             yield(tuple(temp_list))
# 
#     def track_convert2bedGraph(self, track, in_call=False, window=300):
#         """
#         Converts a single data belonging to a single track in a list of tuples in
#             an object of class BedGraph. The data is grouped in time windows.
#             
#             :param track: :py:func:`list` of tuples containing data of a single track
#             :param False in_call: If False the call to the function is from the user otherwise
#                 is from inside :py:func: `convert2single_track()`
#             :param window: :py:func:`int` length of windows inside bedGraph file in seconds (default 300)
#                  
#             :return: BedGraph object
#         """
#         
#         #This fields are mandatory in objects of class BedGraph
#         _bed_fields = ["track","chromStart","chromEnd","dataValue"] 
#         
#         #Check whether these fields are in the original otherwise raise exception
#         try:
#             idx_f = [self.fieldsG.index(f) for f in _bed_fields]                          
#         except ValueError:
#             raise ValueError("Mandatory field for bed creation '%s' not in file %s." % (f, self.path))
#         
#         if (not in_call and len(self.tracks)  != 1):            
#             raise ValueError("Your file '%s' has more than one track, only single tracks can be converted to bedGraph" % (self.path))
#         
#         i_track = self.fieldsG.index("track")
#         i_chr_start = self.fieldsG.index("chromStart")
#         i_chr_end = self.fieldsG.index("chromEnd")
#         i_data_value = self.fieldsG.index("dataValue")
#         ini_window = 0
#         delta_window = window      
#         end_window = delta_window
#         partial_value = 0 
#         cross_interv_dict = {}
#         
#         #When the tracks have been join it is necessary to order by chr_start
#         track = sorted(track, key=itemgetter(*[i_chr_start]))
#                               
#         for row in track:
#             temp_list = []
#             chr_start = row[i_chr_start]
#             chr_end = row[i_chr_end]
#             data_value = float(row[i_data_value])
#             self.fieldsG.index(f) 
#             
#             #Intervals happening after the current window
#             #if there is a value accumulated it has to be dumped otherwise 0
#             if chr_start > end_window:
#                 while (end_window < chr_start):                                      
#                     partial_value = partial_value + cross_interv_dict.get(ini_window,0)
#                     temp_list.append("chr1")
#                     temp_list.append(ini_window)
#                     temp_list.append(end_window)
#                     temp_list.append(partial_value)
#                     partial_value = 0
#                     ini_window += delta_window + 1
#                     end_window += delta_window + 1                                 
#                     yield(tuple(temp_list))
#                     temp_list = []
#     
#                 #Value must to be weighted between intervals
#                 if chr_end > end_window:                
#                     value2weight = data_value
#                     end_w = end_window
#                     start_new = chr_start
#                     end_new = chr_end
#                     
#                     for start_w in range (ini_window, chr_end, delta_window):
#                         weighted_value = 0
#                         
#                         if (end_w == start_w):
#                             weighted_value = (end_w - start_new + 1) / (end_new - start_new)
#                         else:     
#                             weighted_value = (end_w - start_new) / (end_new - start_new)
#                             
#                         weighted_value *= value2weight
#                         cross_interv_dict[start_w] = float(cross_interv_dict.get(start_w,0)) + float(weighted_value)                      
#                         start_new = end_w
#                         value2weight = value2weight - weighted_value                        
#     
#                         if ((end_w + delta_window) >= chr_end):
#                             new_start_w = start_w + delta_window
#                             cross_interv_dict[new_start_w] = cross_interv_dict.get(new_start_w,0) + value2weight
#                             break
#                         
#                         end_w = end_w + delta_window
#                 else:
#                     partial_value = partial_value + data_value
#                             
#             elif (chr_start <= end_window and chr_start >= ini_window):
#                 if chr_end <= end_window:
#                     partial_value = partial_value + data_value                 
#                 
#                 else:
#                     value2weight = data_value
#                     end_w = end_window
#                     start_new = chr_start
#                     end_new = chr_end
#                     
#                     for start_w in range (ini_window, chr_end, delta_window):
#                         weighted_value = 0
#                         
#                         if (end_w == start_w):
#                             weighted_value = (end_w - start_new + 1) / (end_new - start_new)
#                         else:    
#                             weighted_value = (end_w - start_new) / (end_new - start_new)
#                             
#                         weighted_value *= value2weight
#                         cross_interv_dict[start_w] = float(cross_interv_dict.get(start_w,0)) + float(weighted_value)
#                         start_new = end_w
#                         value2weight = value2weight - weighted_value
#                         
#                         if ((end_w + delta_window) >= chr_end):
#                             new_start_w = start_w + delta_window
#                             cross_interv_dict[new_start_w] = cross_interv_dict.get(new_start_w,0) + value2weight
#                             break
#                         
#                         end_w = end_w + delta_window
#             else:
#                 print >> stderr,("FATAL ERROR: Something went wrong")
#         
#         #Last value just printed out
#         temp_list.append("chr1")
#         temp_list.append(ini_window)
#         temp_list.append(end_window)
#         temp_list.append(data_value)
#         yield(tuple(temp_list))
                    
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
    genomeFile.write (_generic_nt * (self.max - self.min))
    genomeFile.close()
    print >>stderr, 'Genome fasta file created: %s' % (pwd + chrom + _genome_file_ext)

class DataIter(object):
    def __init__(self, data, fields=None, dataTypes=None, **kwargs):
        if isinstance(data,(tuple)):            
            data = iter(data)
        
        if not fields:
            raise ValueError("Must specify a 'fields' attribute for %s." % self.__str__())
        
        self.data = data
        self.fields = fields
        print "......dataTypes in DataIter are:", dataTypes#del
        self.dataTypes = dataTypes 
        print "......dataTypes in DataIter are:",self.dataTypes#del      
        self.format = kwargs.get("format",'txt')
        self.track = kwargs.get('track', "1")
        
    def __iter__(self):
        return self.data

    def next(self):
        return self.data.next()
    
    def convert(self, mode='bed', **kwargs):
        """
        Calls function to convert data (as a list of tuples) into a dictionary of 
        the one or several object of class set by mode
        
        :param bed mode: class of the output objects returned set to `bed` by
            default
                
        :return: dictionary containing object/s of the class set by mode 
        
        """
        kwargs['relative_coord'] = kwargs.get("relative_coord",False)
        
        print >> stderr, self.fields        
        
        if mode not in _dict_file: 
            raise ValueError("Mode \'%s\' not available. Possible convert() modes are %s"%(mode,', '.join(['{}'.format(m) for m in _dict_file.keys()])))
        
#         dict_tracks = (self._convert2single_track(self._read(**kwargs), mode, **kwargs)) #TODO
        dict_tracks = (self._convert2single_track(self.data, mode, **kwargs)) 
#         dict_tracks = (self._convert2single_track(self.data, mode, **kwargs)) #TODO
        
        return (dict_tracks)
        
    def _convert2single_track (self, data_tuples,  mode=None, **kwargs):
        """
        Split data (as a list of tuples) into one or several objects depending on options 
        selected. Each object will correspond to a track in the genome browser
        
        :param data_tuples: list of tuples containing data
        :param None mode: class of each single track that will be hold in dictionary
            
        :return: dictionary of tracks
        
        """   
        dict_split = {}
        
        ### Data is separated by track and dataTypes
        idx_fields2split = [self.fields.index("track"), self.fields.index("dataTypes")]
        data_tuples = sorted(data_tuples, key=itemgetter(*idx_fields2split))
        
        for key,group in groupby(data_tuples, itemgetter(*idx_fields2split)):
            if not dict_split.has_key(key[0]):
                dict_split [key[0]] = {}
            dict_split [key[0]][key[1]] = tuple(group)
        
        ### Tracks not set in tracks option are filtered out
        sel_tracks = []
        if not kwargs.get('tracks'):
            pass
        else:
            sel_tracks = map(str, kwargs.get("tracks",[]))
                
        ### When any tracks are selected we consider that no track should be removed
        if sel_tracks != []:
            tracks2rm = self.tracks.difference(sel_tracks)            
            dict_split = self.remove (dict_split, tracks2rm)
            print >> stderr, "Removed tracks are:", ' '.join(tracks2rm)
        
        d_track_merge = {} 
        
        ### If tracks_merge is set we combine tracks selected                 
        if not kwargs.get('tracks_merge'):
            d_track_merge = dict_split
        else:
            tracks_merge = kwargs.get('tracks_merge',self.tracks)
            if not all(tracks in self.tracks for tracks in tracks_merge):
                raise ValueError ("Tracks to merge: %s, are not in the track list: " % 
                                  ",".join("'{0}'".format(n) for n in tracks_merge), 
                                  ",".join("'{0}'".format(n) for n in self.tracks))
            print >> stderr, ("Tracks that will be merged are: %s" %  " ".join(tracks_merge))
            
            d_track_merge = self.join_by_track(dict_split, tracks_merge)       
        
        d_dataTypes_merge = {}
        
        ### If set we join the dataTypes or natures
        if not kwargs.get('dataTypes_actions') or kwargs.get('dataTypes_actions') == 'one_per_channel':
            d_dataTypes_merge = d_track_merge
        elif kwargs.get('dataTypes_actions') == 'all':
            d_dataTypes_merge = self.join_by_dataType(d_track_merge, mode)
    
        track_dict = {}                        
   
        
        ### Generating track dict (output)
        #validacion del diccionario para imprimir o lo que sea
        #mirar si es un diccionario de diccionarios la primera validacion hay que desarrolarla 
        for k, v in d_track_merge.items():
            if isinstance(v,dict):
                print "Is a dictionary"#del
                                   
        window = kwargs.get("window", 300)
        
        ### Assigning data to output dictionary    
        for k, d in d_dataTypes_merge.items():
            for k_2, d_2 in d.items():
                track_dict[k,k_2] = globals()[_dict_file[mode][0]](getattr(self,_dict_file[mode][1])(d_2, True, window), track=k, dataTypes=k_2)
                       
        return (track_dict)
    
    
    def remove (self, dict_t, tracks2remove):
        """
        Removes selected tracks from a dictionary of tracks that is the input of the function those that are 
        set by tracks2remove
        
        :param dict_t: py:func:`dict` dictionary containing one or more tracks, keys represent each 
            of these tracks
        :param tracks2remove: :py:func:`list` of tracks to remove from the dict_t
             
        :return: dict_t dictionary, that contains the remaining tracks
        
        #TODO I can make this function more general as remove from dictionary it can be use outside
        
        """
        for key in tracks2remove:
            key = str(key)
    
            dict_t.pop(key, None)
    
            if key in self.tracks:
                self.tracks.remove(key)
                
        return (dict_t)
    
    def join_by_track(self, dict_t, tracks2join):  
        """
        Join tracks by track name or id 
        
        :param dict_t: py:func:`dict` containing one or more tracks, keys 
            represent each of these tracks
        :param tracks2join: :py:func:`list` of tracks to join in a single track
             
        :return: d_track_merge dictionary that contains the joined tracks
        
        TODO What if I give to the function only some tracks to join, what happen
            to the remaining tracks
         
        """
        
        d_track_merge = {} 
        new_tracks = set()
        
        for key, nest_dict in dict_t.items():
            
            if key not in tracks2join: 
                print "Track not use because was not set when join_by_track is called: %s" % key
                continue
            
            if not d_track_merge.has_key('_'.join(tracks2join)):
                d_track_merge['_'.join(tracks2join)] = {}
                new_tracks.add('_'.join(tracks2join))
            
            for key_2, data in nest_dict.items():                            
                if not d_track_merge['_'.join(tracks2join)].has_key(key_2):
                    d_track_merge['_'.join(tracks2join)] [key_2]= data
                else:  
                    d_track_merge['_'.join(tracks2join)] [key_2] = d_track_merge['_'.join(tracks2join)] [key_2] + data

        self.tracks = new_tracks
                   
        return (d_track_merge)
    
    
    def join_by_dataType (self, dict_d, mode):
        """
        Join tracks by dataType
        
        :param dict_d: py:func:`dict` containing one or more tracks, primary key 
            are tracks id and secondary tracks are dataTypes
        :param mode: :py:func:`str` class of the object that is going to be 
            generated
             
        :return: d_dataTypes_merge dictionary that contains the joined tracks
         
        """
        d_dataTypes_merge = {}
        
        for key, nest_dict in dict_d.items():
            
            d_dataTypes_merge[key] = {}
            new_dataTypes = set()
            
            for key_2, data in nest_dict.items(): 
                
                if not d_dataTypes_merge[key].has_key('_'.join(nest_dict.keys())):
                    d_dataTypes_merge[key]['_'.join(nest_dict.keys())] = data
                    new_dataTypes.add('_'.join(nest_dict.keys())) 
                else:                    
                    d_dataTypes_merge[key]['_'.join(nest_dict.keys())] = d_dataTypes_merge[key]['_'.join(nest_dict.keys())] + data
                    new_dataTypes.add('_'.join(nest_dict.keys()))          
        
        #New dataTypes only set if objects is bedGraph. Bed objects needs to 
        #know all original dataTypes to display them with different colors
        if mode == 'bedGraph':
            self.dataTypes = new_dataTypes

        return (d_dataTypes_merge)
    
    def track_convert2bed(self, track, in_call=False, restricted_colors=None, **kwargs):
        """
        Converts a single data belonging to a single track in a list of tuples in
        an object of class Bed
        
        :param track: :py:func:`list` of tuples containing data of a single track
        :param False in_call: If False the call to the function is from the user otherwise
            is from inside :py:func: `convert2single_track()`
        :param None restricted_colors: Set colors not to be used #TODO this is not clear example??
             
        :return: Bed object
        
        """
        
        #This fields are mandatory in objects of class Bed
        _bed_fields = ["track","chromStart","chromEnd","dataTypes", "dataValue"]
        
        #Check whether these fields are in the original otherwise raise exception
        try:
            [self.fields.index(f) for f in _bed_fields]
        except ValueError:
            raise ValueError("Mandatory field for bed creation '%s' not in file %s." % (f, self.path))

        if (not in_call and len(self.tracks) != 1):
            raise ValueError("Your file '%s' has more than one track, only single tracks can be converted to bed" % (self.path))
        
        i_track = self.fields.index("track")
        i_chr_start = self.fields.index("chromStart")
        i_chr_end = self.fields.index("chromEnd")
        i_data_value = self.fields.index("dataValue")
        i_data_types = self.fields.index("dataTypes")
        
        #Generate dictionary of field and color gradients
        _dict_col_grad = assign_color (self.dataTypes)
            
        for row in track:
            temp_list = []
            temp_list.append("chr1")
            temp_list.append(row[i_chr_start])
            temp_list.append(row[i_chr_end])
            temp_list.append(row[i_data_types]) 
            temp_list.append(row[i_data_value])   
            temp_list.append("+")
            temp_list.append(row[i_chr_start])
            temp_list.append(row[i_chr_end])
            for v in _intervals:
                if float(row[i_data_value]) <= v:
                    j = _intervals.index(v)
                    d_type = row [self.fields.index("dataTypes")]
                    color = _dict_col_grad[d_type][j]
                    break
            temp_list.append(color)          
            
            yield(tuple(temp_list))

    def track_convert2bedGraph(self, track, in_call=False, window=300):
        """
        Converts a single data belonging to a single track in a list of tuples in
            an object of class BedGraph. The data is grouped in time windows.
            
            :param track: :py:func:`list` of tuples containing data of a single track
            :param False in_call: If False the call to the function is from the user otherwise
                is from inside :py:func: `convert2single_track()`
            :param window: :py:func:`int` length of windows inside bedGraph file in seconds (default 300)
                 
            :return: BedGraph object
        """
        
        #This fields are mandatory in objects of class BedGraph
        _bed_fields = ["track","chromStart","chromEnd","dataValue"] 
        
        #Check whether these fields are in the original otherwise raise exception
        try:
            idx_f = [self.fields.index(f) for f in _bed_fields]                          
        except ValueError:
            raise ValueError("Mandatory field for bed creation '%s' not in file %s." % (f, self.path))
        
        if (not in_call and len(self.tracks)  != 1):            
            raise ValueError("Your file '%s' has more than one track, only single tracks can be converted to bedGraph" % (self.path))
        
        i_track = self.fields.index("track")
        i_chr_start = self.fields.index("chromStart")
        i_chr_end = self.fields.index("chromEnd")
        i_data_value = self.fields.index("dataValue")
        ini_window = 0
        delta_window = window      
        end_window = delta_window
        partial_value = 0 
        cross_interv_dict = {}
        
        #When the tracks have been join it is necessary to order by chr_start
        track = sorted(track, key=itemgetter(*[i_chr_start]))
                              
        for row in track:
            temp_list = []
            chr_start = row[i_chr_start]
            chr_end = row[i_chr_end]
            data_value = float(row[i_data_value])
            self.fieldsG.index(f) 
            
            #Intervals happening after the current window
            #if there is a value accumulated it has to be dumped otherwise 0
            if chr_start > end_window:
                while (end_window < chr_start):                                      
                    partial_value = partial_value + cross_interv_dict.get(ini_window,0)
                    temp_list.append("chr1")
                    temp_list.append(ini_window)
                    temp_list.append(end_window)
                    temp_list.append(partial_value)
                    partial_value = 0
                    ini_window += delta_window + 1
                    end_window += delta_window + 1                                 
                    yield(tuple(temp_list))
                    temp_list = []
    
                #Value must to be weighted between intervals
                if chr_end > end_window:                
                    value2weight = data_value
                    end_w = end_window
                    start_new = chr_start
                    end_new = chr_end
                    
                    for start_w in range (ini_window, chr_end, delta_window):
                        weighted_value = 0
                        
                        if (end_w == start_w):
                            weighted_value = (end_w - start_new + 1) / (end_new - start_new)
                        else:     
                            weighted_value = (end_w - start_new) / (end_new - start_new)
                            
                        weighted_value *= value2weight
                        cross_interv_dict[start_w] = float(cross_interv_dict.get(start_w,0)) + float(weighted_value)                      
                        start_new = end_w
                        value2weight = value2weight - weighted_value                        
    
                        if ((end_w + delta_window) >= chr_end):
                            new_start_w = start_w + delta_window
                            cross_interv_dict[new_start_w] = cross_interv_dict.get(new_start_w,0) + value2weight
                            break
                        
                        end_w = end_w + delta_window
                else:
                    partial_value = partial_value + data_value
                            
            elif (chr_start <= end_window and chr_start >= ini_window):
                if chr_end <= end_window:
                    partial_value = partial_value + data_value                 
                
                else:
                    value2weight = data_value
                    end_w = end_window
                    start_new = chr_start
                    end_new = chr_end
                    
                    for start_w in range (ini_window, chr_end, delta_window):
                        weighted_value = 0
                        
                        if (end_w == start_w):
                            weighted_value = (end_w - start_new + 1) / (end_new - start_new)
                        else:    
                            weighted_value = (end_w - start_new) / (end_new - start_new)
                            
                        weighted_value *= value2weight
                        cross_interv_dict[start_w] = float(cross_interv_dict.get(start_w,0)) + float(weighted_value)
                        start_new = end_w
                        value2weight = value2weight - weighted_value
                        
                        if ((end_w + delta_window) >= chr_end):
                            new_start_w = start_w + delta_window
                            cross_interv_dict[new_start_w] = cross_interv_dict.get(new_start_w,0) + value2weight
                            break
                        
                        end_w = end_w + delta_window
            else:
                print >> stderr,("FATAL ERROR: Something went wrong")
        
        #Last value just printed out
        temp_list.append("chr1")
        temp_list.append(ini_window)
        temp_list.append(end_window)
        temp_list.append(data_value)
        yield(tuple(temp_list))
        
    def save_track(self, mode="w", path=None):#modify maybe I have to change the method name now is the same as the os.write()??? #TODO
        
        if not path: 
            pwd = getcwd()
        print >> stderr, "No path selected, files dump into path: ", pwd 
                             
        if not(isinstance(self, DataIter)):
            raise Exception("Not writable object, type not supported '%s'."%(type(self)))    
        
        try:
            file_ext = _dict_file.get(self.format)[2]      
        except KeyError:
            raise ValueError("File types not supported \'%s\'"%(self.format))
        
        conc_dataTypes = self.dataTypes
        if isinstance(conc_dataTypes, set):
            conc_dataTypes="_".join(self.dataTypes)        
                        
        name_file = "tr_" + self.track + "_dt_" + conc_dataTypes + file_ext
        print >> stderr, "File %s generated" % name_file       

        track_file = open(join(pwd, name_file), mode)
                
        #Annotation track to set the genome browser interface
        annotation_track = ''
        if self.format == 'bed':
            annotation_track = 'track type=' + self.format + " " + 'name=\"' +  self.track + "_" + self.dataTypes + '\"' + " " + '\"description=' + self.track + " " + self.dataTypes + '\"' + " " + "visibility=2 itemRgb=\"On\" priority=20" 
        elif self.format == 'bedGraph':
            annotation_track = 'track type=' + self.format + " " + 'name=\"' + self.track + "_" + self.dataTypes + '\"' + " " + '\"description=' + self.track + "_" + self.dataTypes + '\"' + " " + 'visibility=full color=' + self.color[7] + ' altColor=' + self.color[8] + ' priority=20'        
        
            track_file.write (annotation_track + "\n")
           
        for row in self.data: 
            track_file.write('\t'.join(str(i) for i in row))
            track_file.write("\n")      
        track_file.close()
          
class Bed(DataIter):
    """
    A dataIter object dessigned to include the fields that are specific
    of bed files
    
    Specific fields used are::
        
         ['chr','start','end','name','score','strand',
          'thick_start','thick_end','item_rgb']
    
    :return: Bed object
     
        
    """
    def __init__(self, data, **kwargs):
        kwargs['format'] = 'bed'
        kwargs['fields'] = ['chr','start','end','name','score','strand','thick_start','thick_end','item_rgb']        

        DataIter.__init__(self,data,**kwargs)

class BedGraph(DataIter):
    """
    dataInt class for bedGraph file format data
    
    .. attribute:: color
       Gradient of colors that assign by value to display in the genome browser
       
    Fields used in this application are:
        
         ['chr','start','end', 'score']
    
    :return: BedGraph object  

          
    """
    def __init__(self,data,**kwargs):
        kwargs['format'] = 'bedGraph'
        kwargs['fields'] = ['chr','start','end','score']        
        self.color = kwargs.get('color',_blue_gradient)
        DataIter.__init__(self,data,**kwargs)
                
def assign_color (set_dataTypes, color_restrictions=None):
    """
    Assign colors to fields, it is optional to set given color to given fields, for example set water to blue
    different data types get a different color in a circular manner
    
    :param set_dataTypes: (list) each of the fields that should be linked to colors
    :param color_restrictions: (dict) fields with colors set by the user
    
    :return: d_dataType_color dictionary with dataTypes as keys and colors as values
    
    """
    d_dataType_color = {}
    colors_not_used = []
    
    if color_restrictions is not None:
        rest_colors = (list (color_restrictions.values()))

        #If there are restricted colors they should be on the default colors list
        if not all(colors in _dict_colors for colors in rest_colors):
            raise ValueError("Not all restricted colors are available") 
        
        #If there are fields link to related colors they also must be in the data type list 
        if not all(key in set_dataTypes for key in color_restrictions):                      
            raise ValueError("Some values of data types provided as color restriction are not present in the file")
            
        for dataType in color_restrictions:
            d_dataType_color[dataType] = _dict_colors[color_restrictions[dataType]] 
    
        colors_not_used = _dict_colors.keys()
        colors_not_used.remove (color_restrictions[dataType])

    for dataType in set_dataTypes:        
        if not colors_not_used:
            colors_not_used = _dict_colors.keys() 
        
        if dataType in d_dataType_color:
            print ("Data type color gradient already set '%s'."%(dataType))
        else:
            d_dataType_color[dataType] = _dict_colors[colors_not_used.pop(0)]    
            
    return d_dataType_color
        