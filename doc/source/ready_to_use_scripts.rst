.. _scripts-page:

Ready-to-use scripts
======================

Pergola provides a series of scripts that are available in your system after you installed 
pergola. 
These scripts try to wrap up the most common functionalities of Pergola library.

.. contents::

.. _scripts-pergola_rules:

-----------------
pergola_rules.py
-----------------

*pergola_rules.py* is available in your system after you installed pergola.


.. tip:: 
	To reproduce all the commands on this tutorial you can download the following data set:
	
	.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.439439.svg
	    :target: https://doi.org/10.5281/zenodo.439439 
	\
    
	The data consists of a series of recordings corresponding to three weeks of the feeding behavior of C57BL/6 fed either with a high-fat or a standard chow.
	To download and uncompress the data you can use the following commands:
	
	.. code-block:: bash
	
	  mkdir data
	  wget -O- https://zenodo.org/record/439439/files/C57BL6_mice_HF.tar.gz | tar xz -C data


***************
General usage:
***************
 


*******************
Script options :
*******************

Pergola options allow the user to use the main features of Pergola library in a ready-to-use script.

.. note::
  
  All the command line examples can be reproduce using the files found in the C57BL6_mice_HF.tar.gz tarball file.

* `Data input`_
* `File formats`_
* `Filtering`_
* `Filtering`_
* `Temporal arguments`_
* `Data output`_

Data input
----------
Two of the data input arguments are the only two mandatory arguments of pergola_rules.py: 
The ``-i``, ``--input`` argument specifies the csv file the user wants to convert and `the `-m``, ``--mapping_file`` 
argument contains the mappings between the input file and the fields inside the pergola ontology terms.
The ``-fs``, ``--field_separator`` sets the delimiter that separates fields inside the input data file. By default set to 
tabs.
TODO mention mapping file should have set to dummy any of the not used fiels from input file
======================= ======= =============================================   =========================================
Argument                short   Description                                     Example
======================= ======= =============================================   =========================================
``--input``             ``-i``  Path of input data file                         -i /foo/feedingBehavior_HF_mice.csv.csv
``--mapping_file``      ``-m``  Path of mapping file                            -m /foo/my_mappings.txt
``--field_separator``   ``-fs`` Field separator of mapping file                 -fs " "
``--no_header``         ``-nh`` The input file has not header (column names)    -nh
``--fields_read``       ``-s``  List of columns name (used in mappping file)    -s 'CAGE' 'EndT' 'Nature' 'Value'
======================= ======= =============================================   =========================================

.. note::

  The format of the mapping file consists in a text file containing in each line the correspondence between a field in the input data field
  and the pergola ontology. TODO make a basic Concepts section with mapping files input etc
	
  .. code-block:: bash
	
    
	   
                    
The following examples shows how to convert the ``feedingBehavior_HF_mice.csv`` from C57BL6_mice_HF data set.

.. code-block:: bash
	
  pergola_rules.py -i ./data/feedingBehavior_HF_mice.csv -m ./data/b2p.txt

.. note::

  Pergola converts data by default to BED file format.

 
If your input file is delimited by commas you can specify it as shown below:

.. code-block:: bash
  
  pergola_rules.py -i /your_data/your_comma_separated_file.csv -m /your_data/b2p.txt -fs ','

Pergola needs that input files columns are mapped into pergola ontology terms and thus, if the input file has not header you should provide an ordered
list with the corresponding fields of your file as in the example below:

.. code-block:: bash
  
  pergola_rules.py -i /your_data/your_comma_separated_file.csv -m /your_data/b2p.txt -nh -s 'CAGE' 'EndT' 'Nature' 'Value'
  
File formats 
------------
Pergola can convert your data to several genomic file formats. The `BED <https://genome.ucsc.edu/FAQ/FAQformat#format1>`_ (default option) 
and `GFF <http://genome.ucsc.edu/FAQ/FAQformat.html#format3>`_ file formats provide the perfect scaffold to encode events in the form of 
discrete time intervals such as for instance a meal. In the other hand, `BedGraph format <https://genome.ucsc.edu/goldenPath/help/bedgraph.html>`_ 
provides a perfect structure to store continuous data such as for instance any behavioral feature measure continuously along time (speed along a trajectory),
or any score derived from the original data (cumulative values applying a binning or statitiscal parameter).  

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
	
  pergola_rules.py -i ./data/feedingBehavior_HF_mice.csv -m /data/b2p.txt -f bedGraph
   
Filtering
---------
Filtering arguments allow you to select a part of your input data based on pergola assigned fields.
 
 -t --tracks  List of selected tracks  
 -dl --data_types_list List of selected data types

======================== ======= ==========================================           =========================================
Argument                 short   Description                                          Example
======================== ======= ==========================================           =========================================
``--tracks``             ``-t``  List of tracks to keep                               ``-t track_id_1 track_id_2``
``--range``        		 ``-r``  Range of tracks to keep if id are numerical          ``-r 1 10``
``--track_actions``      ``-a``  Action to perform on selected tracks              	  ``-t track_id_1 track_id_2 -a split_all``         
``--data_types_list``    ``-dl`` List of data types to keep                           ``-dl data_type_one data_type_2``
``--data_types_actions`` ``-d``  Action to perform on selected data types             ``-dl data_type_one data_type_2 -d``
======================== ======= ========================================             =========================================


all,one_per_channel

The example below shows how to get the data only from animal 1 and 2 (tracks) and only from the food channels (data types):

.. code-block:: bash
	
  pergola_rules.py -i ./data/feedingBehavior_HF_mice.csv -m ./data/b2p.txt -f bedGraph -t 1 2 -dl food_sc food_fat


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
| ``--min_time``           | ``-min`` | integer  | Min time point from which data    | ``-min 10``                |
|                          |          |          | will be processed                 |                            |
+--------------------------+----------+----------+-----------------------------------+----------------------------+
| ``--max_time``           | ``-max`` | integer  | Max time point from which data    | ``-max 1000``              |
|                          |          |          | will be processed                 |                            |
+--------------------------+----------+----------+-----------------------------------+----------------------------+
| ``--intervals_gen``      | ``-n``   |	integer	 | Multiple time points by the       | ``-n``                     | 
|                          |          |          | selected value                    |                            |
+--------------------------+----------+----------+-----------------------------------+----------------------------+
| ``--multiply_intervals`` | ``-mi``  |	integer	 | Creates two time points from an   | ``-mi 1000``               | 
|                          |          |          | original input with a single one  |                            |
+--------------------------+----------+----------+-----------------------------------+----------------------------+

The ``relative_coord`` option 

Data output
-----------
There are several options related to optional fields inside the genomic file formats.

+------------------------+----------+----------+--------------------------------------+----------------------------+
| Argument               | short    | Options  | Description                          | Example                    |
+========================+==========+==========+======================================+============================+
| ``--no_track_line``    | ``-nt``  |          | When set bed file does not include   | ``-nt``                    |
|                        |          |          | a track line (Browser configuration) |                            |        
+------------------------+----------+----------+--------------------------------------+----------------------------+
| ``--bed_label``        | ``-bl``  |          | BED files include labels describing  | ``-bl``                    |    
|                        |          |          | each interval (data type)            |                            |
+------------------------+----------+----------+--------------------------------------+----------------------------+
| ``--color_file``       | ``-c``   |          | Path to file setting color of the    | ``-c /your_path/color.txt``|
|                        |          |          | different data types to be displayed |                            |
+------------------------+----------+----------+--------------------------------------+----------------------------+

Path to file setting color to disa

-nt, --no_track_line  Track line no included in the bed file
-bl, --bed_label      Show data_types as name field in bed file
-c PATH_COLOR_FILE, --color_file PATH_COLOR_FILE
current path  /Users/jespinosa/2017_tests_pergola_paper/test_documentation/data/color_code.txt

                        Dictionary assigning colors of data_types path


                        
.. note::

    In order to see all available options up you can simply type ``pergola_rules.py -h`` 

.. this is a comment ?


*******************
Command examples :
*******************

.. note::

    Data used in these examples can be found in: ``/your_path_to_pergola/sample_data/feeding behavior``

TODO: Explain what the data contains.

Generate raw intervals in bed format:

.. code-block:: bash
	
  $ pergola_rules.py -i /your_path_to_pergola/sample_data/feeding_behavior/feedingBehavior_HF_mice.csv -m /your_path_to_pergola/sample_data/feeding_behavior/b2g.txt -e

Combine only intervals corresponding to meals in a single file:

.. code-block:: bash
	
  $ pergola_rules.py -i /your_path_to_pergola/sample_data/feeding_behavior/feedingBehavior_HF_mice.csv -m /your_path_to_pergola/sample_data/feeding_behavior/b2g.txt -e -f bedGraph -dl food_sc food_fat -d all

Generate windows of accumulated values in bedgraph format:

.. code-block:: bash

  $ pergola_rules.py -i /your_path_to_pergola/sample_data/feeding_behavior/feedingBehavior_HF_mice.csv -m /your_path_to_pergola/sample_data/feeding_behavior/b2g.txt -f bedGraph -e

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

::

The above example shows how to obtain ``velmag`` and ``dtheta`` features from the perframe folder where
jaaba MAT features files are stored and dump them in a directory ``output_dir``.

The ``fp`` mode makes it possible to convert the selected features into bed or bedgraph files and perform any of the pergola_rules.py see `pergola_rules.py`_.
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

Jaaba predictions can be also stored in CSV files or process to bed or bedGraph files applying any `pergola_rules.py`_ option. To choose between these two options 
users can set the ``sc`` or the ``sp`` mode respectively.

The possible arguments for this modes are:

======================= ======= ============================
Argument                short   Description
======================= ======= ============================
``--input``             ``-i``  Path to jaaba scores file
======================= ======= ============================

Hence, the command line to process a scores Jaaba file into a CSV formatted file using ``sc`` mode will be::

  $jaaba_to_pergola sc -i predicted_behavior.mat

In the case of ``sp`` mode, besides we can use any `pergola_rules.py`_ option::
  
	$jaaba_to_pergola sc -i predicted_behavior.mat -m jaaba_scores2pergola_mapping.txt -f bed  


  