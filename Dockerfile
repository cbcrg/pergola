#  Copyright (c) 2014-2016, Centre for Genomic Regulation (CRG).
#  Copyright (c) 2014-2016, Jose Espinosa-Carrasco and the respective authors.
#
#  This file is part of Pergola.
#
#  Pergola is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pergola is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Pergola.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################
# Dockerfile to build Pergola with all its dependencies
# Based on debian wheezy
############################################################

# Set the base image to debian wheezy
# wheezy is small only 30 m smaller than ubuntu
FROM debian:wheezy

# R base already has the OS if I install it then comment wheezy
# FROM rocker/r-base

MAINTAINER Jose Espinosa-Carrasco <espinosacarrascoj@gmail.com>

#
# Install Python and Basic Python Tools
#
# Update always before download
# single command save space, becuase each run generates a folder layer
RUN apt-get update && \
apt-get install -y python python-dev python-distribute python-pip gfortran bedtools

# Copying pergola
COPY pergola /pergola/pergola
COPY scripts /pergola/scripts
COPY requirements.txt /pergola/
COPY setup.py /pergola/	
COPY README.md /pergola/ 
 
# TODO add requirements.txt file to pergola
RUN pip install -r /pergola/requirements.txt && \
apt-get install -y python-scipy && \
cd pergola && python setup.py install