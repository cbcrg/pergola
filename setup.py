#!/usr/bin/env python

from distutils.core import setup

setup(name='pergola',
      version='0.0.1',
      description='A library to visualize behavioral data in a genome browser',
      long_description= open('README.md').read(),
      url='http://github.com/cbcrg/pergola',
      author='Jose Espinosa-Carrasco',
      author_email='espinosacarrascoj@gmail.com',
      license='GNU General Public License 3.0',
      packages=['pergola'],
      scripts = ['scripts/pergola_rules.py', 'scripts/pergola_isatab.py'],
      zip_safe=False)

# mandatory package to add are argparse