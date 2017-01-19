
.. ready_to_use_scripts:
================================
..
Ready-to-use scripts
====================
..

.. contents::
    
================
pergola_rules.py
================

*pergola_rules.py* is available in your system after you installed pergola

--------------
General usage:
--------------
 
.. note::

    In order to see all available options up you can simply type ``pergola_rules.py -h`` 

------------------
Command examples :
------------------

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
  
 
  