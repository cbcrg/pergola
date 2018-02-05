.. _scripts-page: 

Ready-to-use scripts
======================

Pergola provides a series of scripts that are available in your system after its installation
:ref:`installation<installation>`.

These scripts try to wrap up the most common functionalities of Pergola library.

.. contents::

.. _scripts-pergola_rules:

-----------------
pergola
-----------------

``pergola`` enables the user to execute many of the main pergola functionalities.

If you prefer to code your own scripts you can see some examples at the :ref:`tutorials<library>` section.

.. tip::
	To reproduce all ``pergola`` commands shown in this section you can download the following data set:

	.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.838237.svg
	    :target: https://doi.org/10.5281/zenodo.838237

	The data consists of a series of recordings corresponding to three weeks of the feeding behavior of C57BL/6 mice fed either with a high-fat or a standard chow.
	To download and uncompress the data you can use the following commands:

	.. code-block:: bash

	  mkdir data
	  wget -O- https://zenodo.org/record/838237/files/C57BL6_mice_HF.tar.gz | tar xz -C data

*******************
General usage:
*******************
.. Script options :

Pergola options allow the user to use the main features of Pergola library in a ready-to-use script.

We divided in the five following sections the available arguments:

* `Data input`_
* `File formats`_
* `Filtering`_
* `Temporal arguments`_
* `Data output`_

.. note::

  All the command line examples can be reproduce using the files found in the C57BL6_mice_HF.tar.gz tarball file.

Data input
----------

Available data input parameters are listed on the table below:

======================= ======= =============================================   ==============================================
Argument                short   Description                                     Example
======================= ======= =============================================   ==============================================
``--input``             ``-i``  Path of input data file                         ``-i /foo/feedingBehavior_HF_mice.csv.csv``
``--mapping_file``      ``-m``  Path of mapping file                            ``-m /foo/my_mappings.txt``
``--field_separator``   ``-fs`` Field separator of mapping file                 ``-fs " "``
``--no_header``         ``-nh`` The input file has not header (column names)    ``-nh``
``--fields_read``       ``-s``  List of columns name (used in mappping file)    ``-s 'CAGE' 'EndT' 'Nature' 'StartT' 'Value'``
======================= ======= =============================================   ==============================================

Only two of the data input arguments are mandatory to run pergola_rules.py:
The ``-i``, ``--input`` argument specifies the csv file the user wants to convert and `the `-m``, ``--mapping_file``
argument contains the mappings between the input file and the fields inside the pergola ontology terms.

In this manner, the minimal command to run ``pergola_rules.py`` provided that the input and mappings file are correctly formated
would be:

.. code-block:: bash

  pergola -i ./data/feedingBehavior_HF_mice.csv -m ./data/b2p.txt

.. following examples shows how to convert the ``feedingBehavior_HF_mice.csv`` from C57BL6_mice_HF data set.

.. note::

  The format of the mapping file consists in a text file containing in each line the correspondence between a field in
  the input data field and the pergola ontology. For more details, refer to the
  :ref:`pergola ontology<pergola-ontology>` section and to the example of a :ref:`mapping file<mapping-file>`.

.. tip::

  Any field on the input data that should not be used by pergola must be set to ``dummy`` term in the mapping file.

The rest of arguments are optional and enable the user to provide additional information about the input data in the
cases it does not entirely fits the default pergola :ref:`input data<input-data>` format.

For instance, the ``-fs``, ``--field_separator`` sets the delimiter that separates fields inside the input data file
when it is not set to tabs (default). As an example if fields are delimited by ``,``, you can specify it as shown below:

.. code-block:: bash

  pergola -i ./data/feedingBehavior_HF_mice_commas.csv -m ./data/b2p.txt -fs ","

Pergola needs that input files columns are mapped into pergola ontology terms and thus, if the input file has not header you should provide an ordered
list with the corresponding fields of your file as in the example below, using the ``-nh``, ``--no_header`` argument together with the ``-s``, ``--fields_read``:

.. code-block:: bash

  pergola -i ./data/feedingBehavior_HF_mice_no_header.csv -m ./data/b2p.txt -nh -s 'CAGE' 'EndT' 'Nature' 'StartT' 'Value'


File formats
------------
Pergola can convert your data to several genomic file formats. The `BED <https://genome.ucsc.edu/FAQ/FAQformat#format1>`_ (default option)
and `GFF <http://genome.ucsc.edu/FAQ/FAQformat.html#format3>`_ file formats provide the perfect scaffold to encode events in the form of
discrete time intervals such as for instance a meal. In the other hand, `BedGraph format <https://genome.ucsc.edu/goldenPath/help/bedgraph.html>`_
provides a perfect structure to store continuous data such as for instance any behavioral feature measure continuously along time
(speed along a trajectory), or any score derived from the original data (cumulative values applying a binning or statitiscal parameter).

+----------------------+--------+----------+----------------------------------+----------------------------+
| Argument             | short  | Options  | Description                      | Example                    |
+======================+========+==========+==================================+============================+
| ``--format``         | ``-f`` | bed      | Converts data to BED format      | ``-f bed``                 |
+                      +        +----------+----------------------------------+----------------------------+
|                      |        | gff      | Converts data to BedGraph format | ``-f gff``                 |
+                      +        +----------+----------------------------------+----------------------------+
|                      |        | bedGraph | Converts data to  format         | ``-f bedGraph``            |
+----------------------+--------+----------+----------------------------------+----------------------------+

Following our previous example the command line to convert our data to BedGraph format will be:

.. code-block:: bash

  pergola -i ./data/feedingBehavior_HF_mice.csv -m ./data/b2p.txt -f bedGraph

.. note::

  Pergola converts data by default to BED file format. Refer to the :ref:`mapping file<mapping-file>` section
  to see pergola's adapted genomic formats.

Filtering
---------

Filtering arguments allow you to select a part of your input data based on pergola assigned fields.

======================== ======= ================================================= =====================================================
Argument                 short   Description                                       Example
======================== ======= ================================================= =====================================================
``--tracks``             ``-t``  List of tracks to keep                            ``-t track_id_1 track_id_2``
``--range``        		 ``-r``  Track range to keep (numerical)                   ``-r 1 10``
``--track_actions``      ``-a``  Action to perform on selected tracks              ``-t track_id_1 track_id_2 -a split_all``
``--data_types_list``    ``-dl`` List of data types to keep                        ``-dl data_type_one data_type_2``
``--data_types_actions`` ``-d``  Action to perform on selected data types          ``-dl data_type_one data_type_2 -d one_per_channel``
======================== ======= ================================================= =====================================================

.. TODO primero como se hace para elegir solo tracks luego ademas data types

Pergola allows you to filter a subset of your data input based on the field set as ``track`` in your
:ref:`mapping file<mapping-file>`.

The example below shows how to get the data only from animal 1 4 7  (tracks):

.. code-block:: bash
	
  pergola -i ./data/feedingBehavior_HF_mice.csv -m ./data/b2p.txt -t 1 4  7 -dl food_sc food_fat

If you want to get all tracks from 1 to 4 you can then use the ``-r`` option provided your ``track`` field is numeric:

.. code-block:: bash
	
  pergola_rules.py -i ./data/feedingBehavior_HF_mice.csv -m ./data/b2p.txt -r 1-4
  
.. tip::
  By default tracks selected by ``-r`` option are joined together in a single output track. You can use ``-a`` option 
  to change this behavior.

The ``-a`` option allows to join together tracks in the same file. Available ``-a`` options are:

======================= ============================================= 
track_actions           Description                                     
======================= ============================================= 
split_all               Split all ``tracks`` into different files
join_all                Join all ``tracks`` in a single file
join_odd                Join only odd ``tracks`` in a single file
join_even               Join only even ``tracks`` in a single file
======================= ============================================= 

An example of how to join all tracks in the same file would be:

.. code-block:: bash
	
   pergola -i ./data/feedingBehavior_HF_mice.csv -m ./data/b2p.txt -a join_all
   
.. tip::
  You can combine ``-t`` or ``-r`` options with ``-a`` in order to filter tracks and join them as you prefer
  
.. code-block:: bash

   pergola_rules.py -i ./data/feedingBehavior_HF_mice.csv -m ./data/b2p.txt -t 1 2 3 -a join_all
    
It is possible to provide pergola with a list of the field assigned to ``data_type`` pergola ontology term to be kept using ``-dl`` argument.
For instance, in the code below only events assigned to "food_fat" ``data_type`` term are kept:

.. code-block:: bash

  pergola -i ./data/feedingBehavior_HF_mice.csv -m ./data/b2p.txt -dl food_fat

Besides ``-d`` option allows to combine all data types into a single output file or split them in different files:

======================= ============================================= 
track_actions           Description                                     
======================= ============================================= 
all                     Join all ``data_type`` into a single file
one_per_channel         Split each ``data_type`` into different files
======================= ============================================= 

Both ``-dl`` and ``-d`` options can be combine into a single command:

.. code-block:: bash
	
  pergola_rules.py -i ./data/feedingBehavior_HF_mice.csv -m ./data/b2p.txt -dl food_sc food_fat -d one_per_channel


Temporal arguments
------------------
Given the prominent temporal nature of longitudinal data, pergola provides several arguments to obtain time-based features or to process time intervals.

+--------------------------+----------+----------+-----------------------------------+----------------------------+
| Argument                 | short    | Options  | Description                       | Example                    |
+==========================+==========+==========+===================================+============================+
| ``--relative_coord``     | ``-e``   |          | Time relative to first time point | ``-e``                     |
+--------------------------+----------+----------+-----------------------------------+----------------------------+
| ``--window_size``        | ``-w``   | integer  | Bins the data in time windows of  | ``-w 300``                 |    
|                          |          |          | the selected size                 |                            |
+--------------------------+----------+----------+-----------------------------------+----------------------------+
| ``--window_mean``        | ``-wm``  |          | Averages by the window size       | ``-wm``                    |
+--------------------------+----------+----------+-----------------------------------+----------------------------+
| ``--value_mean``         | ``-vm``  |          | Averages by the data items within | ``-vm``                    |
|                          |          |          | the window                        |                            |
+--------------------------+----------+----------+-----------------------------------+----------------------------+
| ``--min_time``           | ``-min`` | integer  | Min time point from which data    | ``-min 10``                |
|                          |          |          | will be processed                 |                            |
+--------------------------+----------+----------+-----------------------------------+----------------------------+
| ``--max_time``           | ``-max`` | integer  | Max time point from which data    | ``-max 1000``              |
|                          |          |          | will be processed                 |                            |
+--------------------------+----------+----------+-----------------------------------+----------------------------+
| ``--intervals_gen``      | ``-n``   |	         | Creates two time points from an   | ``-n``                     | 
|                          |          |          | original input with a single one  |                            |
+--------------------------+----------+----------+-----------------------------------+----------------------------+
| ``--interval_step``      | ``-ns``  |	         | Sets the step to create end time  | ``-ns 100``                |
|                          |          |          | points when -n option is set      |                            |
+--------------------------+----------+----------+-----------------------------------+----------------------------+
| ``--multiply_intervals`` | ``-mi``  |	integer	 | Multiple time points by the       | ``-mi 1000``               | 
|                          |          |          | selected value                    |                            |
+--------------------------+----------+----------+-----------------------------------+----------------------------+

It is possible that input files do not start at time 0. The ``relative_coord`` transforms the time points relative to the first
time point inside the file.

For instance, if time inside the file is expressed as `epoch time <https://en.wikipedia.org/wiki/Unix_time/>`_ as in the example 
below:

::

  CAGE	StartT	    EndT        Value Nature
  1     1335986151  1335986261  0.06  food_sc
  1     1335986275  1335986330	0.02  food_sc
  1     1335986341  1335986427	0.02  food_sc


Applying the ``-e`` it will result into the time coordinates below:

.. code-block:: bash

  pergola -i ./data/file.csv -m data/b2p.txt -e

::

  0	110	
  124	179
  190	276

Pergola enables the user to bin the data using equidistant time windows when formatting data to BedGraph files. The ``-w`` arguments sets the size of these windows.

For example:

.. code-block:: bash
	
  pergola -i ./data/feedingBehavior_HF_mice.csv -m ./data/b2p.txt -f bedGraph -w 300

.. note::

  The ``-w`` argument can be only used together with ``-f bedGraph`` option

The ``-wm`` argument calculates the mean value inside each of the window of time. 

.. code-block:: bash
	
  pergola_rules.py -i ./data/feedingBehavior_HF_mice.csv -m ./data/b2p.txt -f bedGraph -w 300 -wm

The ``-min`` and ``-max`` arguments set which is the first and the last time point to be present in pergola output file.
This can be used for instance to unify the beginning (example below) or end of files:

file_1.csv

::
    
    CAGE    StartT  EndT    Value Nature
    1       20      30      0.02  food_sc
    1	    50      60      0.02  food_fat

.. code-block:: bash

  pergola -i ./data/file_1.csv -m ./data/b2p.txt -f bedGraph -w 10 -min 0

.. note::
  The time points inserted at the beginning of the file using ``-min`` and ``-max`` will be set to zero value. In the example above
  the beginning of the output file will then look as follows:

  ::

    chr1	0	10	0
    chr1	10	20	0.0
    chr1	20	30	0.02

If the input file has only a single time point, pergola can process it using the ``-n`` argument. This situation is common
in files encoding data that are in equidistant time points, as the following one:

::

  id	time value
  1     1    8
  1     2    13  
  1     3    21

In this case the ``-n`` argument generates an interval for each of the items of the file:

.. code-block:: bash

  pergola -i ./data/file_2.csv -m ./data/file_2_to_p.txt -f bedGraph -n
  
.. This command will result in the following output file:

In the case were the input file encodes time as decimal values (for instance tenth of seconds). 

::

    time  value
    1     -30.98
    2     -5.19
    3     23.96
    4     -2.75

It is possible to multiply the time stamp inside this input file by a given factor using the ``-mi`` argument 
and for instance getting the time stamps in milliseconds:
.. in the following way:

.. code-block:: bash

  pergola -i ./data/file_3.csv -m ./data/file_2_to_p.txt -n -mi 1000 -f bedGraph

As a result two time point intervals will be returned in output file:

::

    chr1	0	9	-30.98
    chr1	10	19	-5.19
    chr1	20	29	23.96
    chr1	30	31	-2.75
    
.. note::
  This last argument is useful because provided that genomic tools are always expressed as integer values, if our time points are 
  expressed as decimals sometimes it will be necessary to convert them to integer values.

Data output
-----------
There are several arguments related to optional fields inside the genomic file formats. These arguments
are related to the data visualization in genomic tools.

+------------------------+----------+----------+------------------------------------------+----------------------------+
| Argument               | short    | Options  | Description                              | Example                    |
+========================+==========+==========+==========================================+============================+
| ``--no_track_line``    | ``-nt``  |          | When set bed file does not include       | ``-nt``                    |
|                        |          |          | a track line (Browser configuration)     |                            |        
+------------------------+----------+----------+------------------------------------------+----------------------------+
| ``--bed_label``        | ``-bl``  |          | BED files include labels describing      | ``-bl``                    |    
|                        |          |          | each interval (data type)                |                            |
+------------------------+----------+----------+------------------------------------------+----------------------------+
| ``--color_file``       | ``-c``   |          | Path to a file setting a color for       | ``-c /your_path/color.txt``|
|                        |          |          | the different data types to be displayed |                            |
+------------------------+----------+----------+------------------------------------------+----------------------------+

Some genomic software as for example genome browsers use the track line to get parameters about the visualization of 
the data. To avoid the track line you can use the ``-nt`` option.

.. code-block:: bash
	
  pergola -i ./data/feedingBehavior_HF_mice.csv -m ./data/b2p.txt -nt

The name field of the BED file enables to display a label for each record encoded inside the file. Pergola uses this field 
to display the data_type of each file line when the option is set:

.. code-block:: bash
	
  pergola -i ./data/feedingBehavior_HF_mice.csv -m ./data/b2p.txt -bl

::

    track name="1_food_sc" description="1 food_sc" visibility=2 itemRgb="On" priority=20
    chr1	1335986151	1335986261	food_sc	0.06	+	1335986151	1335986261	113,113,113
    chr1	1335986275	1335986330	food_sc	0.02	+	1335986275	1335986330	170,170,170

To choose which color will be use to display each of the data types inside the file, it is possible to provide 
pergola with a file coding the colors to be used. The file will consists:

::

    food_sc	orange
    food_fat	blue

How to use it is shown in the following example:

.. code-block:: bash
	
  pergola -i ./data/feedingBehavior_HF_mice.csv -m ./data/b2p.txt -c ./data/color_code.txt
                        
.. tip::

    In order to see all available options up you can simply type ``pergola_rules.py -h`` 

*******************
Command examples :
*******************

.. note::

    Data used in these examples can be found in: ``/your_path_to_pergola/sample_data/feeding behavior``

TODO: Explain what the data contains.

Generate raw intervals in bed format:

.. code-block:: bash
	
  $ pergola -i /your_path_to_pergola/sample_data/feeding_behavior/feedingBehavior_HF_mice.csv -m /your_path_to_pergola/sample_data/feeding_behavior/b2g.txt -e

.. _scripts-jaaba_to_pergola:

---------------------
jaaba_to_pergola
---------------------

`Jaaba <http://jaaba.sourceforge.net/>`_ annotates behavior using video recordings of animals. *jaaba_to_pergola* is 
available in your system after you installed pergola. This script allows user to adapt Jaaba data using Pergola 
for its visualization and analysis. 

The available jaaba_to_pergola modes allow to deal with two types of jaaba data:
    
* `Jaaba features`_
* `Jaaba scores`_

.. note::

    In order to see all available options up you can simply type ``jaaba_to_pergola -h`` 

.. _scripts-jaaba-features:

**************
Jaaba features
**************

Jaaba uses a series of features or variables derived from the video-based trajectories of behaving animals to annotate behavior.
Pergola allows to obtain these features. 

Pergola allows to obtain these features as csv files using the ``fc`` mode. Users can also directly process them using pergola_rules.py 
by using the ``fp`` mode.

Available arguments are:

======================= ======= ============================
Argument                short   Description
======================= ======= ============================
``--input``             ``-i``  Directory where jaaba features files are placed
``--jaaba_features``    ``-jf`` Features to extract
``--dumping_directory`` ``-dd`` Directory for dumping csv files
======================= ======= ============================

For example it is possible to obtain JAABA features formatted as CSV files using ``fc`` mode::

    $jaaba_to_pergola fc -i "/jaaba_data/perframe/" -jf velmag dtheta -dd "/output_dir/"

.. note::

    The above example shows how to obtain ``velmag`` and ``dtheta`` features from the perframe folder where
    jaaba MAT features files are stored and dump them in a directory ``output_dir``.

The ``fp`` mode makes it possible to convert the selected features into bed or bedgraph files and perform any of the pergola_rules.py see `pergola`_
options::

	$jaaba_to_pergola fp -i "/jaaba_data/perframe/" -jf velmag dtheta -dd "/output_dir/" -m "jaaba2pergola_mapping.txt" -f bedGraph -w 300	
 
.. _scripts-jaaba-scores:

************
Jaaba scores
************

Pergola can convert Jaaba annotations of animal behavior for its visualization and analysis. Jaaba predicts the periods of time within which animals
are having a given behavior along a trajectory. These `predictions <http://jaaba.sourceforge.net/SavingAndLoading.html#SavingPredictions>`_ can be dumped into a 
`MAT-file format <http://es.mathworks.com/help/matlab/import_export/supported-file-formats.html>`_ that contain both the behavioral events predicted and the scores 
of the reliability of each event.

Jaaba predictions can be also stored in CSV files or process to bed or bedGraph files applying any `pergola`_ option. To choose between these two options
users can set the ``sc`` or the ``sp`` mode respectively.

The possible arguments for this modes are:

======================= ======= ============================
Argument                short   Description
======================= ======= ============================
``--input``             ``-i``  Path to jaaba scores file
======================= ======= ============================

Hence, the command line to process a scores Jaaba file into a CSV formatted file using ``sc`` mode will be::

  $jaaba_to_pergola sc -i predicted_behavior.mat

In the case of ``sp`` mode, besides we can use any `pergola`_ option::
  
	$jaaba_to_pergola sc -i predicted_behavior.mat -m jaaba_scores2pergola_mapping.txt -f bed  


  