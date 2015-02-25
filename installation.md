---
layout: default
title: Installation
weight: 2
---

## Installation

### Dependencies

#### Python libraries

**Required:**

	numpy, biopy-isatab, argparse, csv
 
#### Download and installation

Download Pergola tarball from [github](http://github.com/cbcrg/pergola/ "Github"), unpack and install it:
 
{% highlight bash %}
curl -L  http://github.com/cbcrg/pergola/archive/master.zip -o "pergola.zip"
unzip pergola.zip
cd pergola-master
sudo python setup.py install
{% endhighlight bash %}

#### Testing installation

Finally, if you want to check that your installation completed succesfully, move to test directory and run as in the example:

 
{% highlight bash %}
cd test
python test_pergola.py
{% endhighlight bash %}
