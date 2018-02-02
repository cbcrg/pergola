.. _visualization:

Visualization
===============

One of the main benefits of using Pergola is that it allows you to easily visualize longitudinal behavioral data using
ready-to-use genomic tools. Here you will find some examples of how to use these tools.

--------------
Shiny-pergola
--------------

Using several `Bioconductor`_ packages (Gviz, rtracklayer and GenomicRanges) and `Shiny`_ we created an ad-hoc browser
to visualize data. The code of this interactive web app can be found in our `GitHub repository`_.
We distributed Shiny-pergola as a `Docker image`_ to make easier its use. Read the following sections to learn
how to use Shiny-pergola Docker image.

.. _Bioconductor: https://www.bioconductor.org/
.. _Shiny: https://shiny.rstudio.com/
.. _GitHub repository: https://github.com/JoseEspinosa/shiny-pergola-docker
.. _docker image:

*************
Requirements
*************

Shiny-pergola needs Docker to be installed in your system. If you don't have Docker installed in your system you can
follow the instructions in :ref:`Docker-installation` section.

**********************
Get a sample data set
**********************

Besides, you need a data set to be displayed on the browser. If you want to give Shiny-pergola a try, you may want to
use our sample data set that consists in longitudinal behavioral recordings of mice feeding behavior processed with
Pergola. The data is host in Zenodo and can be download with the following command:

.. code-block:: bash

    mkdir data
    wget -O- https://zenodo.org/record/1162230/files/mouse__viz_shiny_pergola_sample_data.tar.gz | tar xz -C data
    cd data

*************
Pull image
*************

First thing you have to do is to pull Shiny-pergola Docker image from Pergola Docker Hub:

.. code-block:: bash

    docker pull pergola/shiny-pergola:0.1.1

*************
Run image
*************

Once you have downloaded the Shiny-pergola image you can launch it by executing:
You should be in the folder where you have untar the sample data.

.. code-block:: bash

    docker run --rm -p 3600:80 -v "$(pwd)":/pergola_data pergola/shiny-pergola:0.1.1 &

.. note::

    "$(pwd)" can be substitute by where you have untar the downloaded data


To visualize the data you just need to go to your web browser and type in your address bar the ip address returned
by the following command e.g. http://0.0.0.0:3600

***************
Visualize data
***************

.. image:: ./images/snapshot_pergola_shiny.png

----
IGV
----

The `Integrative Genomics Viewer <http://software.broadinstitute.org/software/igv/>`_ (IGV )is a widely-used, powerful
genomic desktop browser. You can use IGV to visualize longitudinal behavioral after converting the data to genomic
formats such ad BED and BedGraph.

*************************
Get IGV official version
*************************

You can download IGV from `here <http://software.broadinstitute.org/software/igv/download>`_.

*************************
Get IGV adapted version
*************************

We adapted IGV to display time units instead of base pairs. This version of IGV is available for its download
`here <https://github.com/JoseEspinosa/IBB>`_ with detailed instructions of how to compile it.



Shiny-pergola needs Docker to be installed in your system. If you don't have Docker installed in your system you can
follow the instructions in :ref:`Docker-installation` section.

-----------------------
Bioconductor libraries
-----------------------
