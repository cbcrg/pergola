---
layout: default
title: Documentation
weight: 2
---

## Documentation

Pergola documentation

#### Reading a file with only time points

Input files should have two columns one with the start point of the interval and second one with the end.
In case you have only a column with time points you can set flag intervals=False and this column will be 
automatically transform into intervals

{% highlight python linenos %}

# intervals=False 
# otherwise you need in your data 2 colums one with the start and a second with the end of each interval
intData = int2browser.intData(path, ontology_dict=configFileDict.correspondence, intervals=False)

{% endhighlight %}


#### Fields option

This option is used to set the fields to be read from your file  

{% highlight python linenos %}
# fields=['list', 'of', 'fields']

{% endhighlight %}

Tip: if your file does not have header 