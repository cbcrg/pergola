
.. \_Installation\_via\_PyPI:
================================


Stable pergola releases are available on ``PyPI``.
In this section you will find the details of how to download Pergola source code
from Github and how to compile it. Prerequisites that Pergola require installed in
your system are also listed in this section.

.. .. contents::

**Pergola requires python >= 2.6 as well as several dependencies that are listed below.**

.. note::

    At the moment the installation has been tested only under Ubuntu-linux and MacOS.
    

Required Python libraries
**************************

Pergola requires the following Python libraries installed in your system:

.. code-block:: bash

  $ pip install numpy argparse biopy-isatab scipy pandas pybedtools xlrd

.. warning:: **You might need to install** first `pip`_  if your python version is not 2.7.9 or later

.. _pip: https://pip.pypa.io/en/latest/installing.html

.. warning:: Under Ubuntu **you might need to install** `python-dev`_  in order to be able to install packages belonging
			to the `SciPy Stack`_ such as numpy and scipy using pip.  Alternatively you can also use:
			``sudo apt-get install python-numpy python-scipy``.

.. _python-dev:  http://packages.ubuntu.com/precise/python-dev
.. _SciPy Stack: http://www.scipy.org/install.html


Install latest release using pip
********************************

Use this command to install last released pergola version:

.. code-block:: bash
  
  $ pip install pergola

Testing installation
**********************

To check whether pergola has been correctly installed you can call pergola main script help option

.. code-block:: bash
  
  $ pergola -h
