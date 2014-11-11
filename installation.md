---
layout: default
title: Installation
weight: 2
---

## Installation

### Dependencies

#### Python libraries

**Required:**

	numpy, argparse, csv
 
#### Download and installation

Download Pergola tarball from [github](http://github.com/cbcrg/pergola/ "Github"), unpack and install it:
 
{% highlight bash %}
wget http://github.com/cbcrg/pergola/tarball/master -O master.tar.gz
tar xzvf master.tar.gz
cd cbcrg-pergola-master
sudo python setup.py install
{% endhighlight bash %}

#### Testing installation

Finally, if you want to check that your installation completed succesfully, move to test directory and run as in the example:

 
{% highlight bash %}
cd test
python test_pergola.py
{% endhighlight bash %}
