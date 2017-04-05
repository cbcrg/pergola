Basic concepts
==============

Pergola is 


-------------------------
Data input
-------------------------

Pergola can process any sequence of temporal events contained in a character-separated file as in the example below:


.. code-block:: bash
	
  $ pergola_rules.py -i /your_path_to_pergola/sample_data/feeding_behavior/feedingBehavior_HF_mice.csv -m /your_path_to_pergola/sample_data/feeding_behavior/b2g.txt -e

::

  id	t_ini	t_end type	value
  1	137	156	type_x	0.06
  1	168	192	type_y	0.02
  1	250	281	type_x	0.07
  2	311	333	type_x	0.08
  2	457	482	type_y	0.02
  2	569	601	type_z	0.03
  ...


The minimal input file must contain at least two columns. One of these columns should 
correspond to time points and the second one to any value assigned to each of the time points.
  
-------------------------
Data mapping 
-------------------------  

In order to specify to pergola the content of each of the fields of the input data,
user has to map the input fields to a set of defined terms or pergola ontology. 

*TODO ONTOLOGY*

Mapping file uses `the external mapping file format <http://geneontology.org/page/external-mapping-file-format>`_
from the `Gene Ontology Consortium <http://geneontology.org/>`_ to set the correspondence between the input data and pergola ontology

.. comment
.. `GFF <http://genome.ucsc.edu/FAQ/FAQformat.html#format3>`_


mapping file

Pergola can be download from `Github`_ and compiled (`Installation from github`_). 
However, we strongly recommend to use Pergola in its containerized version 
(`Pergola docker container`_).

.. _Github: https://www.github.com/



In this section you will find the details of how to download Pergola source code
from Github and how to compile. Prerequisites that pergola require installed in 
your system are also listed in this section.
 
.. toctree::
   :maxdepth: 2
   
   install/installing_pergola

-------------------------
Output formats
-------------------------