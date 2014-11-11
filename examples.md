---
layout: default
title: Examples
weight: 2
---

## Examples

### Using pergola_rules.py
Pergola provides an script to run the module by the command line *pergola_rules.py*

This script uses a series of flags to set its parameters:

{% highlight bash %}

foo@bar$ pergola_rules.py

  -h, --help            show this help message and exit
  -i PATH, --input PATH
                        Input file path
  -o ONTOLOGY_FILE, --ontology_file ONTOLOGY_FILE
                        File with the ontology between fields in behavioral
                        fileand genome browser grammar
  -t TRACKS [TRACKS ...], --tracks TRACKS [TRACKS ...]
                        List of selected tracks
  -l LIST_OF_TRACKS [LIST_OF_TRACKS ...], --list LIST_OF_TRACKS [LIST_OF_TRACKS ...]
                        Numeric list of tracks to be joined in a single
                        genomic like file
  -r RANGE, --range RANGE
                        Numeric range of tracks to be joined in a single
                        genomic like file
  -a {split_all,join_all,join_odd,join_even,join_list}, --track_actions {split_all,join_all,join_odd,join_even,join_list}
                        Option of action with tracks selected, split_all,
                        join_all, join_odd, join_even, join_range or join_list
  -d {all,one_per_channel}, --dataTypes_actions {all,one_per_channel}
                        Unique values of dataTypes field should be dumped on
                        different data structures or not
  -f FORMAT, --format FORMAT
                        Write file output format (bed or bedGraph)
  -e, --relative_coord  Sets first timepoint to 0 and make all the others
                        relative to this timepoint
  -n, --intervals_gen   Set startChrom and endChrom from just a timepoint in
                        the fileusing field set as startChrom
  -m N, --multiply_factor N
                        Multiplies value in dataValue by the given value
  -s FIELDS2READ [FIELDS2READ ...], --fields_read FIELDS2READ [FIELDS2READ ...]
                        List of fields to read from input file
{% endhighlight bash %}



The input of pergola is a csv file (*input.int*) like this one:

{% highlight bash %}
CAGE	StartT	EndT	Nature	Value	Phase
2	1335958961	1335958977	water	0.02	habituation
2	1335959483	1335959577	food_sc	0.04	habituation
2	1335960277	1335960363	food_sc	0.02	habituation
1	1335958961	1335958977	water	0.02	habituation
1	1335959483	1335959577	food_sc	0.04	habituation
{% endhighlight bash %}

You also need and ontology file (*ontology.txt*) that sets the relationship between the fields in *input.int* and the grammar of the genomebrowser, like the following:

{% highlight bash %}
! Mapping of behavioural fields into genome browser fields
!
behavioural_file:CAGE > genome_file:track
behavioural_file:StartT > genome_file:chromStart
behavioural_file:EndT > genome_file:chromEnd
behavioural_file:Nature > genome_file:dataTypes
behavioural_file:Value > genome_file:dataValue
behavioural_file:Phase > genome_file:chrom
{% endhighlight bash %} 

{% highlight python linenos %}
#!/usr/bin/env python
import int2browser, operator, csv, argparse

{% endhighlight %}