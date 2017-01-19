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

*pergola_rules.py* is available in your system after you installed pergola

***************
General usage:
***************
 
.. note::

    In order to see all available options up you can simply type ``pergola_rules.py -h`` 

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


  