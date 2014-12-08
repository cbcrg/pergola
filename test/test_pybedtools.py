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