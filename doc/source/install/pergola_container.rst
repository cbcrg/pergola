.. \_Pergola\_Docker\_Container:
================================

.. pergola_container:

`Docker`_ allows to sandbox an application with all the requirements it needs to 
run (operating system, software, libraries and dependencies) in a container. 
Besides avoiding the tedious process of installing all dependencies, the use of 
Pergola docker images provides the extra benefit of guarantee the reproducibility 
of your results. Regardless your operating system and the software installed in 
your machine, you can always run your computation under the same environment and 
the same version of Pergola using the tag of the image.

.. _Docker: https://www.docker.com/

.. contents::

Docker installation
**************************

Docker can be easily installed following the `official documentation`_ on `linux`_,
`Mac OS X`_ and `Windows`_.

.. _official documentation: https://docs.docker.com/ 
.. _linux: https://docs.docker.com/engine/installation/linux/ 
.. _Mac OS X: https://docs.docker.com/engine/installation/mac/
.. _Windows: https://docs.docker.com/engine/installation/windows/


Pull Pergola image 
*******************

Docker images are tagged and thus at any time you will be able to retrieve the 
exactly same version of the Pergola using the tag corresponding to the version. 
You can pull the latest Pergola image from `Docker Hub`_:

.. _Docker Hub: https://hub.docker.com/

.. code-block:: bash

  docker pull pergola/pergola:latest 

.. Note::

	All Pergola images are available on `Pergola Docker Hub repository`_ 

.. _Pergola Docker Hub repository: https://hub.docker.com/u/pergola 
    

Pergola Docker execution example
*********************************
You can run Pergola on a container created from the downloaded image interatively
with the following command:

.. code-block:: bash

	docker run -ti pergola/pergola bash

You can also mount your fields in the container as shown below:

.. code-block:: bash	

	docker run --rm -it -v /local_path_to_files:/container_path -w /container_path pergola/pergola bash

For a more complete example go to tutorials section.

