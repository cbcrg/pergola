
.. _getting_start:
                
Getting started
===============

Input data
==========

Sequence of temporal events
===========================

Pergola can process any sequence of temporal events contained in a
character-separated file as in the example below:

::

    Animal  StartT  EndT    Behavior    Value
    1   137 156 eat 0.06
    1   168 192 drink   0.02
    1   250 281 eat 0.07
    1   311 333 eat 0.08
    1   457 482 drink   0.02
    1   569 601 drink   0.03

*(note: this example loads a sequence of eating and drinking events from
a experiment where mice were used to study feeding behavior *

Mapping file
============

Pergola needs that you set the equivalences between the fields of the
input data and a controled vocabular defined by Pergola ontology. The
format of the mapping file is *`the external mapping file
format <http://geneontology.org/page/external-mapping-file-format>`__*
from the Gene Ontology Consortium, you can see an example below:

::

    ! Mapping of behavioural fields into genome browser fields
    !
    behavioural_file:Animal > pergola:track
    behavioural_file:StartT > pergola:chromStart
    behavioural_file:EndT > pergola:chromEnd
    behavioural_file:Behavior > pergola:dataTypes
    behavioural_file:Value > pergola:dataValue

.. code:: python

    # You might have to set the path to run this notebook directly from ipython notebook
    import sys
    
    my_path_to_modules = "/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/"
    sys.path.append(my_path_to_modules)
MappingInfo objects
===================

Mappings between the input data and pergola ontology are loaded in
MappingInfo objects:

.. code:: python

    from pergola import mapping
    # load mapping file 
    mapping_info = mapping.MappingInfo("../../sample_data/feeding_behavior/b2g.txt")
To view the mappings MappingInfo objects provide the
:func:``pergola.mapping.Mapping.write`` method

.. code:: python

    mapping_info.write()

.. parsed-literal::

    EndT 	chromEnd
    Nature 	dataTypes
    Value 	dataValue
    StartT 	chromStart
    Phase 	chrom
    CAGE 	track


MappingInfo objects are needed to load data into IntData objects as it
will be explained in the lines below.

IntData objects
===============

IntData objects load all the intervals of a file:

.. code:: python

    from pergola import parsers
    from pergola import intervals
    
    
    # load the data into an IntData object that will store the sequence of events
    int_data = intervals.IntData("../../sample_data/feedingBehavior_HF_mice.csv", map_dict=mapping_info.correspondence)

Intervals when loaded are stored in a list of tuples that can be
accessed by data attribute:

.. code:: python

    #Displays first 10 tuples of data list
    int_data.data[:10]



.. parsed-literal::

    [('1', '1335986261', 'food_sc', '1335986151', '0.06'),
     ('1', '1335986330', 'food_sc', '1335986275', '0.02'),
     ('1', '1335986427', 'food_sc', '1335986341', '0.02'),
     ('1', '1335986451', 'water', '1335986420', '0.08'),
     ('1', '1335986553', 'water', '1335986541', '0.02'),
     ('1', '1335986844', 'water', '1335986832', '0.02'),
     ('1', '1335986947', 'food_sc', '1335986845', '0.02'),
     ('1', '1335987059', 'water', '1335987044', '0.02'),
     ('1', '1335987223', 'food_sc', '1335987089', '0.02'),
     ('1', '1335987495', 'food_sc', '1335987424', '0.02')]



IntData objects also provide some other attributes like the set of
different tracks (term for IDs in pergola ontology) contained in the
data:

.. code:: python

    int_data.dataTypes



.. parsed-literal::

    {'food_fat', 'food_sc', 'water'}



The minimun value present in the data:

.. code:: python

    int_data.min



.. parsed-literal::

    1335985200



The maximun value:

.. code:: python

    int_data.max



.. parsed-literal::

    1337766069



The set of different tracks present in the data (term for different IDs
in pergola ontology). In this case the different IDs for each mice:

.. code:: python

    int_data.tracks



.. parsed-literal::

    {'1',
     '10',
     '11',
     '12',
     '13',
     '14',
     '15',
     '16',
     '17',
     '18',
     '2',
     '3',
     '4',
     '5',
     '6',
     '7',
     '8',
     '9'}



And finally the dataTypes (term for different types of data in pergola
ontology) that can be used to encode for example different behaviours:

.. code:: python

    int_data.dataTypes



.. parsed-literal::

    {'food_fat', 'food_sc', 'water'}



.. code:: python

    mapping_info.write()

.. parsed-literal::

    EndT 	chromEnd
    Nature 	dataTypes
    Value 	dataValue
    StartT 	chromStart
    Phase 	chrom
    CAGE 	track


.. code:: python

    mapping_info.correspondence['EndT']



.. parsed-literal::

    'chromEnd'



.. code:: python

    path_intervals = "../../sample_data/feedingBehavior_HF_mice.csv"
    int_data = intervals.IntData(path_intervals, map_dict=mapping_info.correspondence)
.. code:: python

    print int_data.min

.. parsed-literal::

    1335985200


.. code:: python

    print int_data.max

.. parsed-literal::

    1337766069


.. code:: python

    int_data.tracks



.. parsed-literal::

    {'1',
     '10',
     '11',
     '12',
     '13',
     '14',
     '15',
     '16',
     '17',
     '18',
     '2',
     '3',
     '4',
     '5',
     '6',
     '7',
     '8',
     '9'}



Data conversion:
================

GenomicContainer is a generic class from which three subclasses derive:

Track objects
=============

Data can be loaded into a Track objects by read function. This function
allows to convert the intervals to relative values using the first time
point as 0:

.. code:: python

    int_data_read = int_data.read(relative_coord=True)


.. parsed-literal::

    Relative coordinates set to: True


.. code:: python

    int_data_read.list_tracks



.. parsed-literal::

    {'1',
     '10',
     '11',
     '12',
     '13',
     '14',
     '15',
     '16',
     '17',
     '18',
     '2',
     '3',
     '4',
     '5',
     '6',
     '7',
     '8',
     '9'}



.. code:: python

    int_data_read.range_values



.. parsed-literal::

    [0.02, 4.46]



.. code:: python

    dict_bed = int_data_read.convert(mode='bed')
.. code:: python

    #dict_bed = data_read.convert(mode='bed')
    for key in dict_bed:
        print "key.......: ",key#del
        bedSingle = dict_bed [key]
        print "::::::::::::::",bedSingle.dataTypes

.. parsed-literal::

    key.......:  ('12', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('7', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('14', 'water')
    :::::::::::::: water
    key.......:  ('1', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('12', 'food_fat')
    :::::::::::::: food_fat
    key.......:  ('2', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('10', 'food_fat')
    :::::::::::::: food_fat
    key.......:  ('15', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('17', 'water')
    :::::::::::::: water
    key.......:  ('6', 'food_fat')
    :::::::::::::: food_fat
    key.......:  ('14', 'food_fat')
    :::::::::::::: food_fat
    key.......:  ('5', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('18', 'food_fat')
    :::::::::::::: food_fat
    key.......:  ('2', 'water')
    :::::::::::::: water
    key.......:  ('11', 'water')
    :::::::::::::: water
    key.......:  ('16', 'food_fat')
    :::::::::::::: food_fat
    key.......:  ('16', 'water')
    :::::::::::::: water
    key.......:  ('14', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('11', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('4', 'water')
    :::::::::::::: water
    key.......:  ('3', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('2', 'food_fat')
    :::::::::::::: food_fat
    key.......:  ('10', 'water')
    :::::::::::::: water
    key.......:  ('9', 'water')
    :::::::::::::: water
    key.......:  ('4', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('8', 'water')
    :::::::::::::: water
    key.......:  ('7', 'water')
    :::::::::::::: water
    key.......:  ('17', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('9', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('12', 'water')
    :::::::::::::: water
    key.......:  ('6', 'water')
    :::::::::::::: water
    key.......:  ('16', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('5', 'water')
    :::::::::::::: water
    key.......:  ('10', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('13', 'water')
    :::::::::::::: water
    key.......:  ('8', 'food_fat')
    :::::::::::::: food_fat
    key.......:  ('1', 'water')
    :::::::::::::: water
    key.......:  ('3', 'water')
    :::::::::::::: water
    key.......:  ('18', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('6', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('15', 'water')
    :::::::::::::: water
    key.......:  ('18', 'water')
    :::::::::::::: water
    key.......:  ('4', 'food_fat')
    :::::::::::::: food_fat
    key.......:  ('13', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('8', 'food_sc')
    :::::::::::::: food_sc


.. code:: python

    bed_12_food_sc = dict_bed[('2', 'food_sc')]
.. code:: python

    bed_12_food_sc.range_values



.. parsed-literal::

    ['0.02', '0.540000000000001']



.. code:: python

    type(bed_12_food_sc)



.. parsed-literal::

    pergola.tracks.Bed



.. code:: python

    bed_12_food_sc.data    
    
    # Code to print the data inside a bed object (generator object)
    #for row in bed_12_food_sc.data:
    #    print row



.. parsed-literal::

    <generator object track_convert2bed at 0x10cd5e730>



.. code:: python

    dict_bedGraph = int_data_read.convert(mode='bedGraph')
.. code:: python

    for key in dict_bedGraph:
        print "key.......: ",key#del
        bedGraphSingle = dict_bedGraph [key]
        print "::::::::::::::",bedGraphSingle.dataTypes

.. parsed-literal::

    key.......:  ('12', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('7', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('14', 'water')
    :::::::::::::: water
    key.......:  ('1', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('12', 'food_fat')
    :::::::::::::: food_fat
    key.......:  ('2', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('10', 'food_fat')
    :::::::::::::: food_fat
    key.......:  ('15', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('17', 'water')
    :::::::::::::: water
    key.......:  ('6', 'food_fat')
    :::::::::::::: food_fat
    key.......:  ('14', 'food_fat')
    :::::::::::::: food_fat
    key.......:  ('5', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('18', 'food_fat')
    :::::::::::::: food_fat
    key.......:  ('2', 'water')
    :::::::::::::: water
    key.......:  ('11', 'water')
    :::::::::::::: water
    key.......:  ('16', 'food_fat')
    :::::::::::::: food_fat
    key.......:  ('16', 'water')
    :::::::::::::: water
    key.......:  ('14', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('11', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('4', 'water')
    :::::::::::::: water
    key.......:  ('3', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('2', 'food_fat')
    :::::::::::::: food_fat
    key.......:  ('10', 'water')
    :::::::::::::: water
    key.......:  ('9', 'water')
    :::::::::::::: water
    key.......:  ('4', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('8', 'water')
    :::::::::::::: water
    key.......:  ('7', 'water')
    :::::::::::::: water
    key.......:  ('17', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('9', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('12', 'water')
    :::::::::::::: water
    key.......:  ('6', 'water')
    :::::::::::::: water
    key.......:  ('16', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('5', 'water')
    :::::::::::::: water
    key.......:  ('10', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('13', 'water')
    :::::::::::::: water
    key.......:  ('8', 'food_fat')
    :::::::::::::: food_fat
    key.......:  ('1', 'water')
    :::::::::::::: water
    key.......:  ('3', 'water')
    :::::::::::::: water
    key.......:  ('18', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('6', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('15', 'water')
    :::::::::::::: water
    key.......:  ('18', 'water')
    :::::::::::::: water
    key.......:  ('4', 'food_fat')
    :::::::::::::: food_fat
    key.......:  ('13', 'food_sc')
    :::::::::::::: food_sc
    key.......:  ('8', 'food_sc')
    :::::::::::::: food_sc


.. code:: python

    bedG_8_food_sc = dict_bedGraph[('8', 'food_sc')]
.. code:: python

    bedG_8_food_sc.data
    
    # Code to print the data inside a bed object (generator object)
    #for row in bedG_8_food_sc:
    #    print row



.. parsed-literal::

    <generator object track_convert2bedGraph at 0x10c9afe60>




.. code:: python

    type(int_data_read)



.. parsed-literal::

    pergola.tracks.Track



.. code:: python

    type(int_data_read.data)



.. parsed-literal::

    list



.. code:: python

    int_data_read.range_values



.. parsed-literal::

    [0.02, 4.46]



.. code:: python

    int_data_read.list_tracks



.. parsed-literal::

    {'1',
     '10',
     '11',
     '12',
     '13',
     '14',
     '15',
     '16',
     '17',
     '18',
     '2',
     '3',
     '4',
     '5',
     '6',
     '7',
     '8',
     '9'}



.. code:: python

    int_data_read.data[-10]



.. parsed-literal::

    ('18', 1778342, 'food_fat', 1778315, '0.0800000000000001')



.. code:: python

    Primero poner todo lo que se puede hacer con el intdata
    y luego ya poner el resto

.. code:: python

    data_read.dataTypes



.. parsed-literal::

    {'food_fat', 'food_sc', 'water'}



.. code:: python

    #data_read.convert(mode=write_format, tracks=sel_tracks, tracks_merge=tracks2merge, 
    #                                 data_types=data_types_list, dataTypes_actions=dataTypes_act, 
    #                                 window=window_size) 
.. code:: python

    mapping.write_chr (int_data)

.. parsed-literal::

    Chromosome fasta like file will be dump into "/Users/jespinosa/git/pergola/doc/notebooks" as it has not been set using path_w
    Genome fasta file created: /Users/jespinosa/git/pergola/doc/notebooks/chr1.fa


.. code:: python

    # Generate a cytoband file and a bed file with phases
    mapping.write_cytoband(int_data, end = int_data.max - int_data.min, delta=43200, start_phase="dark")

.. parsed-literal::

    Cytoband like file will be dump into "/Users/jespinosa/git/pergola/doc/notebooks" as it has not been set using path_w
    Bed files with phases will be dump into "/Users/jespinosa/git/pergola/doc/notebooks" as it has not been set using path_w


.. code:: python

    #data_read = intData.read(relative_coord=True, multiply_t=1)
    data_read = int_data.read(relative_coord=True)

.. parsed-literal::

    Relative coordinates set to: True


.. code:: python

    #for i in data_read.data:
    #        print i
.. code:: python

    data_type_col = {'food_sc': 'green', 'food_fat':'red'}
.. code:: python

    bed_str = data_read.convert(mode="bed", data_types=["food_sc", "food_fat"], dataTypes_actions="all", 
                                color_restrictions=data_type_col)

.. parsed-literal::

    Removed data types are: water


.. code:: python

    for key in bed_str:
        bedSingle = bed_str[key]
        bedSingle.save_track()

.. parsed-literal::

    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_8_dt_food_fat_food_sc.bed generated
    No path selected, files dump into path: 

.. parsed-literal::

    Data type color gradient already set 'food_fat'.
    Data type color gradient already set 'food_sc'.
    Data type color gradient already set 'food_fat'.

.. parsed-literal::

     /Users/jespinosa/git/pergola
    File tr_7_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_6_dt_food_fat_food_sc.bed generated
    No path selected, files dump into path: 

.. parsed-literal::

    
    Data type color gradient already set 'food_sc'.
    Data type color gradient already set 'food_fat'.
    Data type color gradient already set 'food_sc'.
    Data type color gradient already set 'food_fat'.

.. parsed-literal::

     /Users/jespinosa/git/pergola
    File tr_14_dt_food_fat_food_sc.bed generated
    No path selected, files dump into path: 

.. parsed-literal::

    
    Data type color gradient already set 'food_sc'.
    Data type color gradient already set 'food_fat'.

.. parsed-literal::

     /Users/jespinosa/git/pergola
    File tr_3_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_2_dt_food_fat_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_5_dt_food_sc.bed generated
    No path selected, files dump into path: 

.. parsed-literal::

    
    Data type color gradient already set 'food_sc'.
    Data type color gradient already set 'food_fat'.
    Data type color gradient already set 'food_sc'.
    Data type color gradient already set 'food_fat'.
    Data type color gradient already set 'food_sc'.
    Data type color gradient already set 'food_fat'.

.. parsed-literal::

     /Users/jespinosa/git/pergola
    File tr_10_dt_food_fat_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_1_dt_food_sc.bed generated
    No path selected, files dump into path: 

.. parsed-literal::

    
    Data type color gradient already set 'food_sc'.
    Data type color gradient already set 'food_fat'.
    Data type color gradient already set 'food_sc'.
    Data type color gradient already set 'food_fat'.

.. parsed-literal::

     /Users/jespinosa/git/pergola
    File tr_18_dt_food_fat_food_sc.bed generated
    No path selected, files dump into path: 

.. parsed-literal::

    
    Data type color gradient already set 'food_sc'.
    Data type color gradient already set 'food_fat'.

.. parsed-literal::

     /Users/jespinosa/git/pergola
    File tr_17_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_16_dt_food_fat_food_sc.bed generated
    No path selected, files dump into path: 

.. parsed-literal::

    
    Data type color gradient already set 'food_sc'.
    Data type color gradient already set 'food_fat'.
    Data type color gradient already set 'food_sc'.
    Data type color gradient already set 'food_fat'.

.. parsed-literal::

     /Users/jespinosa/git/pergola
    File tr_9_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_4_dt_food_fat_food_sc.bed generated
    No path selected, files dump into path: 

.. parsed-literal::

    
    Data type color gradient already set 'food_sc'.
    Data type color gradient already set 'food_fat'.
    Data type color gradient already set 'food_sc'.
    Data type color gradient already set 'food_fat'.

.. parsed-literal::

     /Users/jespinosa/git/pergola
    File tr_13_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_12_dt_food_fat_food_sc.bed generated
    No path selected, files dump into path: 

.. parsed-literal::

    
    Data type color gradient already set 'food_sc'.
    Data type color gradient already set 'food_fat'.
    Data type color gradient already set 'food_sc'.
    Data type color gradient already set 'food_fat'.
    Data type color gradient already set 'food_sc'.
    Data type color gradient already set 'food_fat'.
    Data type color gradient already set 'food_sc'.


.. parsed-literal::

     /Users/jespinosa/git/pergola
    File tr_15_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_11_dt_food_sc.bed generated


.. code:: python

    data_type_col_bedGraph = {'food_sc':'green', 'food_fat_food_sc':'red'}
.. code:: python

    bedGraph_str = data_read.convert(mode="bedGraph", window=1800, data_types=["food_sc", "food_fat"], dataTypes_actions="all", color_restrictions=data_type_col_bedGraph)

.. parsed-literal::

    Data type color gradient already set 'food_fat_food_sc'.
    Data type color gradient already set 'food_sc'.


.. parsed-literal::

    Removed data types are: water


.. code:: python

    for key in bedGraph_str:
        bedGraph_single = bedGraph_str[key]
        bedGraph_single.save_track()

.. parsed-literal::

    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_8_dt_food_fat_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_7_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_6_dt_food_fat_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_14_dt_food_fat_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_3_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_2_dt_food_fat_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_5_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_10_dt_food_fat_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_1_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_18_dt_food_fat_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_17_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_16_dt_food_fat_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_9_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_4_dt_food_fat_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_13_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_12_dt_food_fat_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_15_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File tr_11_dt_food_sc.bedGraph generated


.. code:: python

    ## Bed file showing the files (recordings)
    # reading correspondence file
    mapping_file_data = mapping.OntologyInfo("test/f2g.txt")
.. code:: python

    mapping_file_data.write()

.. parsed-literal::

    Value 	dataValue
    EndT 	chromEnd
    StartT 	chromStart
    File 	track
    NameFile 	dataTypes


.. code:: python

    # Reading file info
    files_data = intervals.IntData("data/sample_data/files.csv", ontology_dict=mapping_file_data.correspondence)
    data_file_read = files_data.read(relative_coord=True)

.. parsed-literal::

    ..............fieldsB ['File', 'NameFile', 'StartT', 'EndT', 'Value']
    {'track': 0, 'chromStart': 2, 'dataTypes': 1, 'dataValue': 4, 'chromEnd': 3}
    range in dicitionary is [0, 1, 2, 3, 4]
    Factor to transform time values has been set to 1.0 as values set as chromStart are decimals
    If you want to set your own factor please use -m,--multiply_intervals n
    .......... [('track', 0), ('dataTypes', 1), ('chromStart', 2), ('chromEnd', 3), ('dataValue', 4)]


.. parsed-literal::

    Relative coordinates set to: True


.. code:: python

    bed_file = data_file_read.convert(mode="bed", dataTypes_actions="all", tracks_merge=files_data.tracks)


.. parsed-literal::

    Tracks that will be merged are: 1 3 2 5 4 7 6 9 8


.. code:: python

    for key in bed_file:
        bed_file_single = bed_file[key]
        bed_file_single.save_track(name_file = "files_data")

.. parsed-literal::

    No path selected, files dump into path:  /Users/jespinosa/git/pergola
    File files_data.bed generated

