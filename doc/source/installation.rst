.. _installation: 

Installation
============

``pergola`` is a Python package that works either as a command line tool or a library. Pergola installation involves its
compilation from the downloaded source code via `Github`_, installing a stable release via `PyPI`_ or to pull the last
Docker image. We strongly recommend this last option (`Pergola docker image`_) since it provides a ready-to-use,
portable version of pergola.

.. _Github: https://www.github.com/
.. _PyPI: https://pypi.python.org/pypi

-------------------------
Installation from Github
-------------------------

In this section you will find the details of how to download ``pergola`` source code via
Github and how to compile it. Prerequisites that pergola require installed in
your system are also listed in this section.
 
.. toctree::
   :maxdepth: 2
   
   install/installing_github

-------------------------
Installation via PyPI
-------------------------

pergola can be installed using ``pip`` following the instructions described here.

.. toctree::
   :maxdepth: 2

   install/installing_pypi

-------------------------
Pergola Docker image
-------------------------

`Docker`_ allows to sandbox an application with all the requirements it needs to run
(operating system, software, libraries and dependencies) in a container.
Besides avoiding the tedious process of installing all dependencies,
the use of ``pergola`` docker images provides the extra benefit of guarantee
the reproducibility of your results. Regardless your operating system
and the software installed in your machine, you can always run your computation
under the same environment and the same version of Pergola using the image tag.
Released images are available at pergola Docker Hub `repository`_.

.. _Docker: https://www.docker.com/

.. _repository: https://hub.docker.com/r/pergola/pergola/

.. toctree::
   :maxdepth: 2

   install/pergola_container

.. note::
    Installation may require admin rights in some cases. In case you don't have them, it might be a good idea to
    work under a virtual environment. Virtual environments allow you to recreate an isolated environment with all its
    dependencies without admin rights. You can use several tools to create Python environments as for
    instance this `one`_.

.. _one: https://github.com/pyenv/pyenv
