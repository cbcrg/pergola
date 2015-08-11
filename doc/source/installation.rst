
Installing Pergola
==================

.. contents::

.. note::

    At the moment the installation has been tested only under Ubuntu-linux and MacOS.
    

**Pergola requires python >= 2.6 as well as several dependencies that are
listed below.**

-----------------------------
Dependencies
-----------------------------

Python libraries
~~~~~~~~~~~~~~~~

**Required:**

.. code-block:: bash

  $ pip install numpy
  $ pip install numpy argparse
  $ pip install csv
  $ pip install biopy-isatab


.. note:: **You might need to install** first `pip`_  if your python version is not 2.7.9 or later

.. _pip: https://pip.pypa.io/en/latest/installing.html

-----------------------------
Download and installation
-----------------------------

Download Pergola tarball from github, unpack and install it:

.. code-block:: bash
  
  $ curl -L  http://github.com/cbcrg/pergola/archive/master.zip -o "pergola.zip"
  $ unzip pergola.zip
  $ cd pergola-master
  $ sudo python setup.py install

or, you can download the code a a ``.zip`` file from Github website and follow the three last instructions above.

.. image:: images/github_zip_red.png

-----------------------------
Development versions
-----------------------------

The source code of pergola can be found in `GitHub`_. There you will find the last 
development version. If you want to modify, contribute or just run the last version 
of the code just clone the repository:

.. _GitHub: https://github.com/cbcrg/pergola

.. code-block:: bash
  
  git clone https://github.com/cbcrg/pergola.git

-----------------------------
Testing installation
-----------------------------

Finally, if you want to check that your installation completed succesfully, move to test directory and run as in the example:

.. code-block:: bash
  
  $ cd test
  $ python test_pergola.py