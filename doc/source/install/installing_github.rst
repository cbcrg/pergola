
.. \_Installation\_from\_Github:
=================================

In this section you will find the details of how to download Pergola source code 
from Github and how to compile it. Prerequisites that Pergola requires installed in
your system are also listed in this section.

.. .. contents::

|
.. warning::
    Pergola requires python >= 2.6 as well as several dependencies that are listed :ref:`below<required_libraries>`.

.. note::
    At the moment the installation has been tested only under Ubuntu-linux and MacOS.
    
.. _required_libraries:

Required Python libraries
**************************

Pergola requires some Python libraries installed in your system, to install them you can use ``pip``:

.. code-block:: bash

  $ pip install numpy argparse biopy-isatab scipy pandas pybedtools

.. warning:: **You might need to install** first `pip`_  if your python version is not 2.7.9 or later

.. _pip: https://pip.pypa.io/en/latest/installing.html

.. warning:: Under Ubuntu **you might need to install** `python-dev`_  in order to be able to install packages belonging
    to the `SciPy Stack`_ such as numpy and scipy using pip.  Alternatively you can also use:
    ``sudo apt-get install python-numpy python-scipy``.

.. _python-dev:  http://packages.ubuntu.com/precise/python-dev
.. _SciPy Stack: http://www.scipy.org/install.html


Download and installation
**************************

Download Pergola tarball from github, unpack and install it:

.. code-block:: bash
  
  $ curl -L  http://github.com/cbcrg/pergola/archive/master.zip -o "pergola.zip"
  $ unzip pergola.zip
  $ cd pergola-master
  $ sudo python setup.py install

or, you can download the code as a ``.zip`` file from Github website and follow the three last instructions above.

.. image:: /images/github_zip_red.png


Development versions
**********************

The source code of pergola can be found in |github| ``pergola`` repository. There you
will find the last development version. If you want to modify, contribute or just run the last version of the code just
clone the repository:

.. |github| raw:: html

   <a href="https://github.com/cbcrg/pergola" target="_blank">GitHub</a>

.. code-block:: bash
  
  git clone https://github.com/cbcrg/pergola.git



Testing installation
**********************

Finally, if you want to check that your installation completed successfully, move to test directory and run as in the example:

.. code-block:: bash
  
  $ cd pergola/test
  $ python test_all.py