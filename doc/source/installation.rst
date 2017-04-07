.. _installation:

Installation
============

Pergola can be download from `Github`_ and compiled (`Installation from github`_). 
However, we strongly recommend to use Pergola in its containerized version 
(`Pergola docker container`_).

.. _Github: https://www.github.com/

-------------------------
Installation from Github
-------------------------

In this section you will find the details of how to download Pergola source code
from Github and how to compile. Prerequisites that pergola require installed in 
your system are also listed in this section.
 
.. toctree::
   :maxdepth: 2
   
   install/installing_pergola

-------------------------
Pergola Docker container
-------------------------

`Docker`_ allows to sandbox an application with all the requirements it needs to run 
(operating system, software, libraries and dependencies) in a container. 
Besides avoiding the tedious process of installing all dependencies, 
the use of Pergola docker images provides the extra benefit of guarantee 
the reproducibility of your results. Regardless your operating system 
and the software installed in your machine, you can always run your computation
under the same environment and the same version of Pergola using the tag of 
the image.  

.. _Docker: https://www.docker.com/

.. toctree::
   :maxdepth: 2
   
   install/pergola_container
