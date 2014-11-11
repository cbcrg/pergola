---
layout: default
title: Examples
weight: 3
---


## General usage:
 
Once you install pergola in your computer you can use in two different ways:

##### 1. Calling *pergola_rules.py* a pergola script that is intalled with Pergola.

##### 2. Directly write your own python scripts


## 1. pergola_rules.py

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

#### Simplest call

The input of pergola is a csv file (*input.int*) like this one:

{% highlight bash %}
CAGE	StartT	EndT	Nature	Value	Phase
2	1335958961	1335958977	water	0.02	habituation
2	1335959483	1335959577	food_sc	0.04	habituation
2	1335960277	1335960363	food_sc	0.02	habituation
1	1335958961	1335958977	water	0.02	habituation
1	1335959483	1335959577	food_sc	0.04	habituation
{% endhighlight bash %}

You also need and ontology file (*ontology.txt*) that sets the relationship between the fields in *input.int* and the genome browser grammar, like the following:

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

You can call *pergola_rules.py* as follow:

{% highlight bash %}
pergola_rules.py -i "/path2file/input.int" -o  "/path2file/ontology.txt"
{% endhighlight bash %}

This call will generate a bed file, with the format described on the UCSC Genome Bioinformatics web site: [http://genome.ucsc.edu/FAQ/FAQformat](http://genome.ucsc.edu/FAQ/FAQformat "Bed format").
Following our example above this will be the result:

{% highlight bash %}
track type=bed name="1_food_sc" "description=1 food_sc" visibility=2 itemRgb="On" priority=20
chr1	522	616	food_sc	0.04	+	522	616	178,254,178
chr1	1316	1402	food_sc	0.02	+	1316	1402	203,254,203
chr1	1817	1845	food_sc	0.02	+	1817	1845	203,254,203
chr1	8540	8851	food_sc	0.1	+	8540	8851	152,254,152
chr1	8862	8914	food_sc	0.02	+	8862	8914	203,254,203
chr1	13760	14054	food_sc	0.1	+	13760	14054	152,254,152
chr1	18121	18511	food_sc	0.1	+	18121	18511	152,254,152
chr1	18526	18805	food_sc	0.08	+	18526	18805	152,254,152
chr1	18859	18942	food_sc	0.02	+	18859	18942	203,254,203
{% endhighlight bash %} 

In addition *pergola_rules.py* will generate a fasta file, simulating a chromosome. This file will be use to load our experiment in the genome browser of our choice as a genome so that we can map the generated tracks into it.
Each position of this file corresponds to the time unit we are using,  in our example seconds, i.e. a single nucleotid will correspond to a second of our experiment.

**NOTE:**

	By default your file will be separated in as many tracks as different values are in field tracks and in field dataTypes. In our example for instance 4 files bed files will be generated as we have two tracks values (1 ,2) and two dataTypes (water, food_sc), thus generated files will be (tr_1_dt_food_sc.bed, tr_1_dt_water.bed, tr_2_food_sc.bed and tr_2_water.bed) 

#### Additional parameters




#### Using additional parameters

##### tracks
```
--tracks/-t track_i track_j
```

You can set which tracks you want to read from your file if you set a tracks field in your ontology, and tracks field has more than one value (track_1, track_2)   

```
--list/-l track_i track_j
```
A list of all the tracks that you want to join in a single file.

```
--range/-r i j
```

If your tracks field holds numerical values (int) you can set the range of them to be joined in a single file
 
```
--a/-track_actions [split_all,join_all,join_odd,join_even,join_list]
```

Set the rule among the list to follow to join tracks in a single file. For instance join_all with join all of them, 


**Note:**

	This option is not compatible with --range/r or with --list/-l 

```
-f FORMAT, --format [bed, bedGraph]
```

Sets the format of the output file (bed, bedGraph)


```
-e/--relative_coord
```

Sets first timepoint to 0 and make all the others relative to this timepoint

```
-n, --intervals_gen  
```

If your file has only timepoints and not intervals, this option allows you to generate the intervals from them (the field containing timepoints must be set to startChrom in the ontology file)

```
-m, --multiply_factor n  
```

Genome browsers only allow you to use you integers value to map, for this reason if time points for example are expressed as decimals (0.001 *s*) you can transform them to ms using *-m 1000*

An example of a complete command line with all the options (not mutually exclusive) set is:

{% highlight bash %}
pergola_rules.py -i "/path2file/input.int" -o "/path2file/ontology.txt" -t track_1 track_2 track_3 -a join_all -f bedGraph -e -n -m 1000 
{% endhighlight bash %}



