
.. \_getting_start:
===================

You can code your own scripts using ``pergola`` as a Python library.
Here we summarize some examples of how you can use it on your scripts.

.. raw:: html

   <div class="alert alert-block alert-info">

Tip: This page is available as a Jupyter Notebook on
/pergola/doc/notebooks under pergola GitHub repository. Should you want,
you can interactively execute the code using Jupyter.

.. raw:: html

   </div>

Input data
----------

The two basics data inputs ``pergola`` uses is a file with longitudinal
recordings (sequence of temporal events) in the form of a ``CSV`` or
``xlsx`` file and a mapping file containing the correspondence between
the fields in this previous file and the ``pergola`` ontology.

Sequence of temporal events
---------------------------

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

.. raw:: html

   <div class="alert alert-block alert-info">

Note: This example loads a sequence of eating and drinking events from a
experiment where mice were used to study feeding behavior.

.. raw:: html

   </div>

Mapping file
------------

Pergola needs that you set the equivalences between the fields of the
input data and a controled vocabular defined by Pergola ontology. The
format of the mapping file is `the external mapping file
format <http://geneontology.org/page/external-mapping-file-format>`__
from the Gene Ontology Consortium, you can see an example below:

::

    ! Mapping of behavioural fields into genome browser fields
    !
    behavioural_file:Animal > pergola:track
    behavioural_file:StartT > pergola:chromStart
    behavioural_file:EndT > pergola:chromEnd
    behavioural_file:Behavior > pergola:dataTypes
    behavioural_file:Value > pergola:dataValue

.. code:: ipython2

    # You might have to set the path to run this notebook directly from ipython notebook
    import sys

    my_path_to_modules = "/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/"
    sys.path.append(my_path_to_modules)

MappingInfo objects
-------------------

Mappings between the input data and pergola ontology are loaded in
MappingInfo objects:

.. code:: ipython2

    from pergola import mapping
    # load mapping file
    mapping_info = mapping.MappingInfo("../../sample_data/feeding_behavior/b2p.txt")

To view the mappings MappingInfo objects provide the
:func:``pergola.mapping.Mapping.write`` method

.. code:: ipython2

    mapping_info.write()


.. parsed-literal::

    EndT 	end
    Nature 	data_types
    Value 	data_value
    StartT 	start
    Phase 	chrom
    CAGE 	track


MappingInfo objects are needed to load data into IntData objects as it
will be explained in the lines below.

IntData objects
---------------

IntData objects load all the intervals of a file:

.. code:: ipython2

    from pergola import parsers
    from pergola import intervals


    # load the data into an IntData object that will store the sequence of events
    int_data = intervals.IntData("../../sample_data/feeding_behavior/feeding_behavior_HF_mice.csv", map_dict=mapping_info.correspondence)



.. parsed-literal::

    Input file format identified as csv


Intervals when loaded are stored in a list of tuples that can be
accessed by data attribute:

.. code:: ipython2

    #Displays first 10 tuples of data list
    int_data.data[:10]




.. parsed-literal::

    [('1', 1335985232, 'food_sc', 1335985200, '0.02'),
     ('1', 1335986427, 'food_sc', 1335986151, '0.1'),
     ('1', 1335986451, 'water', 1335986420, '0.08'),
     ('1', 1335986553, 'water', 1335986541, '0.02'),
     ('1', 1335986844, 'water', 1335986832, '0.02'),
     ('1', 1335986947, 'food_sc', 1335986845, '0.02'),
     ('1', 1335987059, 'water', 1335987044, '0.02'),
     ('1', 1335987223, 'food_sc', 1335987089, '0.02'),
     ('1', 1335987495, 'food_sc', 1335987424, '0.02'),
     ('1', 1335987574, 'water', 1335987546, '0.04')]



IntData objects also provide some other attributes like the set of
different tracks (term for IDs in pergola ontology) contained in the
data:

.. code:: ipython2

    int_data.data_types




.. parsed-literal::

    {'food_fat', 'food_sc', 'water'}



The minimun value present in the data:

.. code:: ipython2

    int_data.min




.. parsed-literal::

    1335985200



The maximun value:

.. code:: ipython2

    int_data.max




.. parsed-literal::

    1337799586



The set of different tracks present in the data (term for different IDs
in pergola ontology). In this case the different IDs for each mice:

.. code:: ipython2

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
     '7',
     '8',
     '9'}



And finally the dataTypes (term for different types of data in pergola
ontology) that can be used to encode for example different behaviours:

.. code:: ipython2

    mapping_info.write()


.. parsed-literal::

    EndT 	end
    Nature 	data_types
    Value 	data_value
    StartT 	start
    Phase 	chrom
    CAGE 	track


.. code:: ipython2

    mapping_info.correspondence['EndT']




.. parsed-literal::

    'end'



Data conversion:
----------------

GenomicContainer is a generic class from which three subclasses derive:

Track objects
-------------

Data can be loaded into a Track objects by read function. This function
allows to convert the intervals to relative values using the first time
point as 0:

.. code:: ipython2

    int_data_read = int_data.read(relative_coord=True)



.. parsed-literal::

    Relative coordinates set to: True


.. code:: ipython2

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
     '7',
     '8',
     '9'}



.. code:: ipython2

    int_data_read.range_values




.. parsed-literal::

    [0.02, 8.82]



.. code:: ipython2

    dict_bed = int_data_read.convert(mode='bed')

.. code:: ipython2

    #dict_bed = data_read.convert(mode='bed')
    for key in dict_bed:
        print "key.......: ",key#del
        bedSingle = dict_bed [key]
        print "::::::::::::::",bedSingle.data_types


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


.. code:: ipython2

    bed_12_food_sc = dict_bed[('2', 'food_sc')]

.. code:: ipython2

    bed_12_food_sc.range_values




.. parsed-literal::

    ['0.02', '0.540000000000001']



.. code:: ipython2

    type(bed_12_food_sc)




.. parsed-literal::

    pergola.tracks.Bed



.. code:: ipython2

    bed_12_food_sc.data

    # Code to print the data inside a bed object (generator object)
    #for row in bed_12_food_sc.data:
    #    print row




.. parsed-literal::

    <generator object track_convert2bed at 0x1077e5550>



.. code:: ipython2

    dict_bedGraph = int_data_read.convert(mode='bedGraph')

.. code:: ipython2

    for key in dict_bedGraph:
        print "key.......: ",key#del
        bedGraphSingle = dict_bedGraph [key]
        print "::::::::::::::",bedGraphSingle.data_types


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


.. code:: ipython2

    bedG_8_food_sc = dict_bedGraph[('8', 'food_sc')]

Track object
------------

.. code:: ipython2

    bedG_8_food_sc.data

    # Code to print the data inside a bed object (generator object)
    #for row in bedG_8_food_sc:
    #    print row




.. parsed-literal::

    <generator object track_convert2bedGraph at 0x1081f9690>



.. code:: ipython2

    type(int_data_read)




.. parsed-literal::

    pergola.tracks.Track



.. code:: ipython2

    type(int_data_read.data)




.. parsed-literal::

    list



.. code:: ipython2

    int_data_read.range_values




.. parsed-literal::

    [0.02, 8.82]



.. code:: ipython2

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
     '7',
     '8',
     '9'}



.. code:: ipython2

    int_data_read.data[-10]




.. parsed-literal::

    ('18', 1812042, 'food_fat', 1811948, '0.14')



.. code:: ipython2

    int_data_read.data_types




.. parsed-literal::

    {'food_fat', 'food_sc', 'water'}



.. code:: ipython2

    #data_read.convert(mode=write_format, tracks=sel_tracks, tracks_merge=tracks2merge,
    #                                 data_types=data_types_list, dataTypes_actions=dataTypes_act,
    #                                 window=window_size)

.. code:: ipython2

    mapping.write_chr (int_data_read)


.. parsed-literal::

    Chromosome fasta like file will be dump into "/Users/jespinosa/git/pergola/doc/notebooks" as it has not been set using path_w
    Genome fasta file created: /Users/jespinosa/git/pergola/doc/notebooks/chr1.fa


.. code:: ipython2

    # Generate a cytoband file and a bed file with phases
    mapping.write_cytoband(end = int_data.max - int_data.min, delta=43200, start_phase="dark", lab_bed=False)


.. parsed-literal::

    Cytoband like file will be dump into "/Users/jespinosa/git/pergola/doc/notebooks" as it has not been set using path_w
    Bed files with phases will be dump into "/Users/jespinosa/git/pergola/doc/notebooks" as it has not been set using path_w


.. code:: ipython2

    #data_read = intData.read(relative_coord=True, multiply_t=1)
    data_read = int_data.read(relative_coord=True)


.. parsed-literal::

    Relative coordinates set to: True


.. code:: ipython2

    #for i in data_read.data:
    #        print i

.. code:: ipython2

    data_type_col = {'food_sc': 'orange', 'food_fat':'blue'}

.. code:: ipython2

    bed_str = data_read.convert(mode="bed", data_types=["food_sc", "food_fat"], dataTypes_actions="all",
                                color_restrictions=data_type_col)


.. parsed-literal::

    Removed data types are: water


.. code:: ipython2

    for key in bed_str:
        bedSingle = bed_str[key]
        bedSingle.save_track()


.. parsed-literal::

    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_12_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_14_dt_food_fat.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_1_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_2_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_15_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_5_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_16_dt_food_fat.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_14_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_11_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_3_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_2_dt_food_fat.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_10_dt_food_fat.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_4_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_17_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_9_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_12_dt_food_fat.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_16_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_10_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_8_dt_food_fat.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_7_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_18_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_18_dt_food_fat.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_4_dt_food_fat.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_13_dt_food_sc.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_8_dt_food_sc.bed generated


Output data
-----------

``pergola`` allows the conversion to several genomic formats, here we
summarize some commands and operations as an example of ``pergola``
capabilities:

Bed file
--------

::

    track type=bed name="1_eat" description="1 eat" visibility=2 itemRgb="On" priority=20
    chr1    137.0   156.0   ""  0.06    +   137.0   156.0   51,254,51
    chr1    250.0   281.0   ""  0.07    +   250.0   281.0   0,254,0
    chr1    311.0   333.0   ""  0.08    +   311.0   333.0   25,115,25

::

    track type=bed name="1_eat" description="1 eat" visibility=2 itemRgb="On" priority=20
    chr1    0   19  ""  0.06    +   0   19  51,254,51
    chr1    113 144 ""  0.07    +   113 144 0,254,0
    chr1    174 196 ""  0.08    +   174 196 25,115,25

.. code:: ipython2

    data_type_col_bedGraph = {'food_sc':'orange', 'food_fat_food_sc':'blue'}

.. code:: ipython2

    bedGraph_str = data_read.convert(mode="bedGraph", window=1800, data_types=["food_sc", "food_fat"], dataTypes_actions="all", color_restrictions=data_type_col_bedGraph)


.. parsed-literal::

    Removed data types are: water


.. code:: ipython2

    for key in bedGraph_str:
        bedGraph_single = bedGraph_str[key]
        bedGraph_single.save_track()


.. parsed-literal::

    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_12_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_14_dt_food_fat.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_1_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_2_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_15_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_5_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_16_dt_food_fat.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_14_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_11_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_3_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_2_dt_food_fat.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_10_dt_food_fat.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_4_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_17_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_9_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_12_dt_food_fat.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_16_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_10_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_8_dt_food_fat.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_7_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_18_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_18_dt_food_fat.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_4_dt_food_fat.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_13_dt_food_sc.bedGraph generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File tr_8_dt_food_sc.bedGraph generated


bedGraph files
--------------

::

    track type=bedGraph name="1_eat" description="1_eat" visibility=full color=0,254,0 altColor=25,115,25 priority=20
    chr1    0   30  0.06
    chr1    30  60  0
    chr1    60  90  0
    chr1    90  120 0.0158064516129
    chr1    120 150 0.0541935483871
    chr1    150 180 0.0218181818182
    chr1    180 210 0.0581818181818
    chr1    210 240 0

.. code:: ipython2

    ## Bed file showing the files (recordings)
    # reading correspondence file
    mapping_file_data = mapping.MappingInfo("../../sample_data/feeding_behavior/f2g.txt")

.. code:: ipython2

    mapping_file_data.write()


.. parsed-literal::

    Value 	data_value
    EndT 	end
    StartT 	start
    File 	track
    NameFile 	data_types


.. code:: ipython2

    # Reading file info
    files_data = intervals.IntData("../../sample_data/feeding_behavior/files.csv", map_dict=mapping_file_data.correspondence)
    data_file_read = files_data.read(relative_coord=True)


.. parsed-literal::

    Input file format identified as csv
    Relative coordinates set to: True


.. code:: ipython2

    bed_file = data_file_read.convert(mode="bed", dataTypes_actions="all", tracks_merge=files_data.tracks)



.. parsed-literal::

    Tracks that will be merged are: 1 3 2 5 4 7 6 9 8


.. code:: ipython2

    for key in bed_file:
        bed_file_single = bed_file[key]
        bed_file_single.save_track(name_file = "files_data")


.. parsed-literal::

    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File files_data.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File files_data.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File files_data.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File files_data.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File files_data.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File files_data.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File files_data.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File files_data.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File files_data.bed generated


.. code:: ipython2

    # Reading phase info
    phase_data = intervals.IntData("../../sample_data/feeding_behavior/phases_exp.csv", map_dict=mapping_file_data.correspondence)
    data_phase_read = phase_data.read(relative_coord=True)


.. parsed-literal::

    Input file format identified as csv
    Relative coordinates set to: True


.. code:: ipython2

    bed_file = data_phase_read.convert(mode="bed", dataTypes_actions="all", tracks_merge=phase_data.tracks)


.. parsed-literal::

    Tracks that will be merged are: 1 2


.. code:: ipython2

    for key in bed_file:
        bed_file_single = bed_file[key]
        bed_file_single.save_track(name_file = "phase_exp")


.. parsed-literal::

    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File phase_exp.bed generated
    No path selected, files dump into path:  /Users/jespinosa/git/pergola/doc/notebooks
    File phase_exp.bed generated


means bed file to delete

::

    chr1    1   1801    ""  1000    +   0   1   0.06
    chr1    137171  138971  ""  1000    +   132936  137171  0
    chr1    397442  399242  ""  1000    +   391684  397442  0
    chr1    568633  570433  ""  1000    +   563646  568633  0.125714

intermeal to delete

::

    chr1    1   30  ""  1000    +   1   30  0
    chr1    183 345 ""  1000    +   183 345 0
    chr1    502 924 ""  1000    +   502 924 0
