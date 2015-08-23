#!/usr/bin/env python

from distutils.core import setup
from os import path

PATH = path.abspath(path.split(path.realpath(__file__))[0])

setup(name='pergola',
      version='0.0.1',
      description='A library to analyze and visualize behavioral data by unlocking genomic tools ',
      long_description= open('README.md').read(),
      url='http://github.com/cbcrg/pergola',
      author='Jose Espinosa-Carrasco',
      author_email='espinosacarrascoj@gmail.com',
      license='GNU General Public License 3.0',
      package_dir = {'pergola': PATH + '/pergola'},
      package_data={'mypkg': ['data/sample_data/*.csv']},
      packages=['pergola'],      
      scripts = ['scripts/pergola_rules.py', 'scripts/pergola_isatab.py'],
      zip_safe=False)

# mandatory package to add are argparse