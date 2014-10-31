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
        self.data, self.min, self.max = self._read(multiply_t = kwargs.get('multiply_t', 1), intervals=kwargs.get('intervals', False))
        self.dataTypes = self.get_field_items(field ="dataTypes", data = self.data, default="a")
        
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
                        
        _int_points = ["chromStart", "chromEnd"]
        idx_fields2int = [10000000000000]
        i_new_field = [10000000000000]                                    
        
        if intervals:             
            print >>stderr, "Intervals inferred from timepoints"
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
#         DataIter(self._read(indexL, idx_fields2rel, idx_fields2int, l_startChrom, l_endChrom, multiply_t), self.fieldsG)
        return (list_data, p_min, p_max)
    
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
            
            if fields2rel is None:
                _f2rel = ["chromStart","chromEnd"] 
#             if fields2rel is None and intervals: #TODO
#                 _f2rel = ["chromStart","chromEnd"] 
#             elif fields2rel is None and not intervals:
#                 _f2rel = ["chromStart"]    
            else:
                if isinstance(fields2rel, basestring): fields2rel = [fields2rel]
                _f2rel = [f for f in fields2rel if f in self.fieldsG]
                
            try:
                idx_fields2rel = [self.fieldsG.index(f) for f in _f2rel]                
            except ValueError:
                raise ValueError("Field '%s' not in file %s mandatory when option relative_coord=T." % (f, self.path))
            
            print idx_fields2rel
            self.data = self._time2rel_time(idx_fields2rel)
                
        idx_fields2int = [10000000000000]
        
        return self.data
#         return DataIter(self.data)

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

    def convert(self, mode = 'bed', **kwargs):
        """
        :param i_fields: :py:func:`list`
        :param bed mode: :py:class: `bed` object returned, other options are  :py:class: `bedGraph`
         
        :return: object/s of the class set by mode 
        
        """
        kwargs['relative_coord'] = kwargs.get("relative_coord",False)
        
        print >> stderr, self.fieldsG
            
        if mode not in _dict_file: 
            raise ValueError("Mode \'%s\' not available. Possible convert() modes are %s"%(mode,', '.join(['{}'.format(m) for m in _dict_file.keys()])))
        
        dict_tracks = (self._convert2single_track(self.read(**kwargs), mode, **kwargs))
        
        return (dict_tracks)
        
    def _convert2single_track (self, data_tuple,  mode=None, **kwargs):
        """
        Transform data into a bed file if all the necessary fields present
        """   
        dict_split = {}
        
        ###################
        ### Data is separated by track and dataTypes
        idx_fields2split = [self.fieldsG.index("track"), self.fieldsG.index("dataTypes")]
        data_tuple = sorted(data_tuple,key=itemgetter(*idx_fields2split))
        
        for key,group in groupby(data_tuple, itemgetter(*idx_fields2split)):
            if not dict_split.has_key(key[0]):
                dict_split [key[0]] = {}
            dict_split [key[0]][key[1]] = tuple(group)
        
        ###################
        ### Filtering tracks
        sel_tracks = []
        if not kwargs.get('tracks'):
            pass
        else:
            sel_tracks = map(str, kwargs.get("tracks",[]))
                
        #When any tracks are selected we consider that any track should be removed
        if sel_tracks != []:
            tracks2rm = self.tracks.difference(sel_tracks)            
            dict_split = self.remove (dict_split, tracks2rm)
            print >> sys.stderr, "Removed tracks are:", ' '.join(tracks2rm)
        
        d_track_merge = {} 
        
        ###################
        ###tracks_merge                 
        if not kwargs.get('tracks_merge'):
            d_track_merge = dict_split
        else:
            tracks_merge = kwargs.get('tracks_merge',self.tracks)
            if not all(tracks in self.tracks for tracks in tracks_merge):
                raise ValueError ("Tracks to merge: %s, are not in the track list: " % ",".join("'{0}'".format(n) for n in tracks_merge), ",".join("'{0}'".format(n) for n in self.tracks))
            print >>sys.stderr, ("Tracks that will be merged are: %s" %  " ".join(tracks_merge))
            
            d_track_merge = self.join_by_track(dict_split, tracks_merge)       
        
        d_dataTypes_merge = {}
        
        ##################
        # Joining the dataTypes or natures
        if not kwargs.get('dataTypes_actions') or kwargs.get('dataTypes_actions') == 'one_per_channel':
            d_dataTypes_merge = d_track_merge
        elif kwargs.get('dataTypes_actions') == 'all':
            d_dataTypes_merge = self.join_by_dataType(d_track_merge, mode)
    
        track_dict = {}                        
   
        #######
        # Generating track dict (output)
        #validacion del diccionario para imprimir o lo que sea
        #mirar si es un diccionario de diccionarios la primera validacion hay que desarrolarla 
        for k, v in d_track_merge.items():
            if isinstance(v,dict):
                print "Is a dictionary"#del
                                   
        window = kwargs.get("window", 300)
        
        #Output    
        for k, d in d_dataTypes_merge.items():
            for k_2, d_2 in d.items():
#                 track_dict[k,k_2] = globals()[_dict_file[mode][0]](getattr(self,_dict_file[mode][1])(d_2, True, window), track=k, dataType=k_2, color=_dict_col_grad[k_2])
                track_dict[k,k_2] = globals()[_dict_file[mode][0]](getattr(self,_dict_file[mode][1])(d_2, True, window), track=k, dataType=k_2)
                       
        return (track_dict)
    
    def track_convert2bed (self, track, in_call=False, restrictedColors=None, **kwargs):
        #fields pass to read should be the ones of bed file
        _bed_fields = ["track","chromStart","chromEnd","dataTypes", "dataValue"]
        
        #Check whether these fields are in the original otherwise raise exception
        try:
            [self.fieldsG.index(f) for f in _bed_fields]
        except ValueError:
            raise ValueError("Mandatory field for bed creation '%s' not in file %s." % (f, self.path))

        if (not in_call and len(self.tracks) != 1):
            raise ValueError("Your file '%s' has more than one track, only single tracks can be converted to bed" % (self.path))
        
        i_track = self.fieldsG.index("track")
        i_chr_start = self.fieldsG.index("chromStart")
        i_chr_end = self.fieldsG.index("chromEnd")
        i_data_value = self.fieldsG.index("dataValue")
        i_data_types = self.fieldsG.index("dataTypes")
        
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
                    d_type = row [self.fieldsG.index("dataTypes")]
                    color = _dict_col_grad[d_type][j]
                    break
            temp_list.append(color)          
            
            yield(tuple(temp_list))
def write_chr(self, mode="w", path_w=None):
    """
    Creates a fasta file of the length of the range of value inside the IntData object
    that will be use for the mapping the data into it
    
    :param mode: :py:func:`str` mode to use by default write 
    
    """
    chrom = 'chr1'
    if not path_w: 
        pwd = getcwd()
        print >>stderr, """Chromosome fasta like file will be dump into %s be set to %s 
                             as it has not been set using path_w""", pwd

    genomeFile = open(join(pwd, chrom + _genome_file_ext), mode)        
    genomeFile.write(">" + chrom + "\n")
    genomeFile.write (_generic_nt * (self.max - self.min))
    genomeFile.close()
    print >>stderr, 'Genome fasta file created: %s' % (pwd + chrom + _genome_file_ext)

class DataIter(object):
    def __init__(self, data, fields=None, **kwargs):
        if isinstance(data,(tuple)):            
            data = iter(data)
        
        if not fields:
            raise ValueError("Must specify a 'fields' attribute for %s." % self.__str__())
        
        self.data = data
        self.fields = fields       
        self.format = kwargs.get("format",'txt')
        self.track = kwargs.get('track', "")
        self.dataType = kwargs.get('dataType', "")
        
    def __iter__(self):
        return self.data

    def next(self):
        return self.data.next()

    def write(self, mode="w"):#modify maybe I have to change the method name now is the same as the os.write()???
        
        if not(isinstance(self, DataIter)):
            raise Exception("Not writable object, type not supported '%s'."%(type(self)))    
        
        try:
            file_ext = _dict_file.get(self.format)[2]      
        except KeyError:
            raise ValueError("File types not supported \'%s\'"%(self.format))
                                                           
#         if self.track is "":  # modify
#             self.track = "1"
        
#         if self.dataType is "":
#             self.dataType = "a"
                
        name_file = "tr_" + self.track + "_dt_" + self.dataType + file_ext
        print >>sys.stderr, "File %s generated" % name_file       

        track_file = open(os.path.join(_pwd, name_file), mode)
                
        #Annotation track to set the genome browser interface
        annotation_track = ''
        if self.format == 'bed':
            annotation_track = 'track type=' + self.format + " " + 'name=\"' +  self.track + "_" + self.dataType + '\"' + " " + '\"description=' + self.track + " " + self.dataType + '\"' + " " + "visibility=2 itemRgb=\"On\" priority=20" 
        elif self.format == 'bedGraph':
            annotation_track = 'track type=' + self.format + " " + 'name=\"' + self.track + "_" + self.dataType + '\"' + " " + '\"description=' + self.track + "_" + self.dataType + '\"' + " " + 'visibility=full color=' + self.color[7] + ' altColor=' + self.color[8] + ' priority=20'        
        
            track_file.write (annotation_track + "\n")
           
        for row in self.data: 
            track_file.write('\t'.join(str(i) for i in row))
            track_file.write("\n")      
        track_file.close()
          
class Bed(DataIter):
    """
    dataInt class for bed file format data
    
    Fields used in this application are:
        
         ['chr','start','end','name','score','strand',
          'thick_start','thick_end','item_rgb']
          
    """
    def __init__(self, data, **kwargs):
        kwargs['format'] = 'bed'
        kwargs['fields'] = ['chr','start','end','name','score','strand','thick_start','thick_end','item_rgb']        
        
        DataIter.__init__(self,data,**kwargs)
        