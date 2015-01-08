import pybedtools

#Example from the web
import pybedtools
a = pybedtools.example_bedtool('a.bed')
b = pybedtools.example_bedtool('b.bed')

# My own data
a = pybedtools.example_bedtool('/home/kadomu/git/pergola/tr_1_2_dt_food_sc.bed')
b = pybedtools.example_bedtool('/home/kadomu/git/pergola/tr_1_2_dt_water.bed')
c = a.intersect(b)
c.saveas("/home/kadomu/git/pergola/a_inter_b.bed")

#Intersections
(a-b-c).count()  # unique to a
(a+b-c).count()  # in a and b, not c
(a+b+c).count()  # common to all

#venn diagram script 
venn_mpl.py -a food.bed -b water.bed -c i.bed

# BEDTools examples

intersectBed -a tr_1_dt_food_sc.bed -b tr_1_dt_water.bed > food_sc_waterBedTools.bed
closestBed -a tr_1_dt_food_sc.bed -b tr_1_dt_water.bed > food_sc_waterBedToolsClosest.bed
