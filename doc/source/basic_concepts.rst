Basic concepts
==============

Pergola allows to explore and process longitudinal data using genomic tools.

Two main benefits derive from using pergola. 

Visualization and data processing mature genomic tools can be used.


-------------------------
Input
-------------------------

*****************
Input data
*****************

Pergola can process any sequence of temporal events contained in a character-separated file as in the example below:

::

  id	t_ini	t_end type	value	description
  1	137	156	type_x	0.06	"type x event"
  1	168	192	type_y	0.02    "type y event"
  1	250	281	type_x	0.07    "type x event"
  2	311	333	type_x	0.08 	"type x event"
  2	457	482	type_y	0.02 	"type y event"
  2	569	601	type_z	0.03    "type z event"
  ...

The minimal input file must contain at least two columns. One of these columns should 
correspond to time points and the second one to any value assigned to each of the time points.

.. Mappings 
  
*****************
Pergola ontology
*****************

In order to specify to pergola the content of each of the fields of the input data,
user has to map the input fields to a set of defined terms or pergola ontology. 

The **pergola ontology** consists on a set of controlled terms or vocabulary to define
the content of each of the input fields inside the input data.

Pergola ontology terms are shown in the table below: 

.. =============== ============		=================
.. Term            Mandatory       	Definition
.. =============== ============      	=================
.. chrom_start	    yes	           		Refers to start time points of each interval of the original data. If “chrom_end” is not set all “chrom_start” should be equidistant and intervals will be set to the delta between time points.
.. data_values		yes					Refers to associated values consider for the representation of data.
.. chrom_end		no					Refers to the end of each time interval.
.. track	    	no					Refers to each of the experimental entities present in the file.
.. data_types		no					Refers to each of the different features annotated in the file.
.. chrom	    	no					Refers to different phases of the experiment.
.. dummy	    	no					All additional fields in the original input data not used by pergola
.. =============== ============      	=================

=============== =================
Term            Definition
=============== =================
start	        Refers to start time points of each interval of the original data. If “chrom_end” is not set all “chrom_start” should be equidistant and intervals will be set to the delta between time points (**mandatory**). 
data_value		Refers to associated values consider for the representation of data (**mandatory**).
end		        Refers to the end of each time interval.
track	    	Refers to each of the experimental entities present in the file.
data_types		Refers to each of the different features annotated in the file.
chrom	    	Refers to different phases of the experiment.
dummy	    	All additional fields in the original input data not used by pergola
=============== =================
  
To see how to create a mapping file using pergola ontology to set the equivalence between input terms in 
the original data and Pergola output terms, read next section.

*************
Mapping file
*************

The mapping file sets the correspondence between the input data and the terms used by pergola.
It is thus the way pergola knows what is encoded in each of the fields of the input data.
Provided we have an input file as the show in the `Data input`_ section, a mapping file looks like the following example:

::

  ! Mapping of behavioural fields into pergola ontology terms
  !
  ! Any test starting with an exclamation mark is a comment

  input_file:id > pergola:track 
  input_file:t_ini > pergola:start
  input_file:t_end > pergola:end 
  input_file:type > pergola:data_types
  input_file:value > pergola:data_value
  input_file:description > pergola:dummy

Mapping file uses `the external mapping file format <http://geneontology.org/page/external-mapping-file-format>`_
from the `Gene Ontology Consortium <http://geneontology.org/>`_ to set the correspondence 
between the input data and the pergola ontology.

.. note::
  The reserved term input_file is arbitrary and just to follow the convention of the external mapping 
  file format. You can use whatever you want provided it is follow by a colon sign. 
  This might be changed in following pergola versions.
  
.. comment
.. `GFF <http://genome.ucsc.edu/FAQ/FAQformat.html#format3>`_

Pergola can be download from `Github`_ and compiled (`Installation from github`_). 
However, we strongly recommend to use pergola in its containerized version 
(`Pergola docker container`_).

.. _Github: https://www.github.com/

In this section you will find the details of how to download Pergola source code
from Github and how to compile. Prerequisites that pergola require installed in 
your system are also listed in this section.
 
.. toctree::
   :maxdepth: 2
   
   install/installing_pergola

-------------------------
Output
-------------------------

Pergola adapted several of the more commonly used formats of the genomics community to
encode longitudinal data. The idea is very simple, both types of data are sequential
and thus, it is relatively easy to adapt the scaffold thought to encode genomic data to 
encode a temporal sequence of events. In this section we present the formats we adapted and 
for which purpose they can be used.

****************
Discrete data
****************

Longitudinal data many times presents the form of a sequence of irregular discrete events or time 
intervals with a series of associated data such as the type of event or the magnitude.
Genomics provides formats that are specially suitable to encode this type of data such as
the `BED <https://genome.ucsc.edu/FAQ/FAQformat.html#format1>`_ (Browser Extensible Format) 
or the `GFF <https://genome.ucsc.edu/FAQ/FAQformat.html#format3>`_ (General Feature Format) 
formats. These two file formats designed to encode information such as genomic features or 
genomic annotations can be adapted to encode discrete temporal events by regarding at chromosome
positions in a genome as analogous to time points in a behavioral trajectory.


****************
Continuous data
****************

Pergola enables the calculation of parameters such as accumulated or mean values of a quantifiable 
measure over user-defined time windows. The `BedGraph <https://genome.ucsc.edu/FAQ/FAQformat.html#format1.8>`_ 
file format used in genomics to store continuous-valued data such as probability scores or transcriptome data, 
provides a perfect structure for Pergola calculations or for whatever type of scores derived from the analysis 
of your input data.

****************
Reference data
****************

Some types of genomics tools, such as several genome browsers, need a reference sequence in order to align the 
data sequences to this reference (genome).
For this reason we adapted the `FASTA <https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGE_TYPE=BlastDocs&DOC_TYPE=BlastHelp>`_ file format  
to enable the use of these type of tools with pergola processed data.

.. TODO mention the cytoband file used for display periods of time relevant for 
.. whatever reason, maybe the more intituitive example (signal) might be days and
.. nights in data that could follow a circadian rhythm. 
.. provide a way to define irregular intervals and associated values. Users can select these formats
..  to encode the duration of behavioral bouts (for example, feeding, grooming or activity) and also their magnitude, 
..  or to store additional environmental information (for example, contextual cues or light-dark cycles). 
.. So for instance if we take again the file as the show in the `Data input`_ section 
 
File formats adapted as pergola output are summarized in the following table:

+--------------+----------------------------------------------------------------------------------------------------+
| Type of data | Format                                                                                             |
+==============+====================================================================================================+
| Discrete     | `BED <https://genome.ucsc.edu/FAQ/FAQformat.html#format1>`_                                        |        
+              +----------------------------------------------------------------------------------------------------+
|              | `GFF <https://genome.ucsc.edu/FAQ/FAQformat.html#format3>`_                                        |
+--------------+----------------------------------------------------------------------------------------------------+
| Continuous   | `BedGraph <https://genome.ucsc.edu/FAQ/FAQformat.html#format1.8>`_                                 |
+--------------+----------------------------------------------------------------------------------------------------+
| Reference    | `FASTA <https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGE_TYPE=BlastDocs&DOC_TYPE=BlastHelp>`_ |
+--------------+----------------------------------------------------------------------------------------------------+

.. note::
  You can go to the specifications of each of these data file formats clicking on the file names in the table.

.. -------------------------
.. Operations
.. -------------------------
