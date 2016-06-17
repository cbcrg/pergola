
.. pergola_container:

.. contents::
    
===================
Docker installation
===================

Docker can be easily installed following the `official documentation`_ on `linux`_,
`Mac OS X`_ and `Windows`_.

.. _official documentation: https://docs.docker.com/ 
.. _linux: https://docs.docker.com/engine/installation/linux/ 
.. _Mac OS X: https://docs.docker.com/engine/installation/mac/
.. _Windows: https://docs.docker.com/engine/installation/windows/

.. note::

	You can check all available Pergola images on Pergola oficial dockerhub repo

    In order to see all available options up you can simply type ``pergola_rules.py -h`` 


==================
Pull Pergola image 
==================

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
  
================
Image versioning 
================

=================
Run pergola image 
=================

 
  