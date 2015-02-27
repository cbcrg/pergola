#!/bin/bash

cd /users/cn/pprieto/projects/kinetoplastids/Ldonovani/plotting/circos/polycistrons/data

# Get chromosome coordinates definition
grep "^chr" ~/projects/kinetoplastids/prod-circos/data/karyotype.ldonovani.txt > karyotype/karyotype.txt

# Get the polycistron tile data
grep -w polycistron ~/public_html/LDonovani/JBrowse/sample_data/leishmania/LDBPK.gff3 | sed 's/^\(\S\+\)|\S\+/\1/' | awk '$7=="+"{print "ld"$1,$4,$5}' | sort -k 1,1 -k 2,2 > tracks/forward_polycistrons.txt
grep -w polycistron ~/public_html/LDonovani/JBrowse/sample_data/leishmania/LDBPK.gff3 | sed 's/^\(\S\+\)|\S\+/\1/' | awk '$7=="-"{print "ld"$1,$4,$5}' | sort -k 1,1 -k 2,2 > tracks/reverse_polycistrons.txt

# Get the protein coding gene tile data
grep -w CRG_last ~/public_html/LDonovani/JBrowse/sample_data/leishmania/LDBPK.gff3 | sed 's/^\(\S\+\)|\S\+/\1/' | awk '{print "ld"$1,$4,$5}' | sort -k 1,1 -k 2,2 > tracks/lncrnas.txt

# Get the lncrna tile data
grep -w CDS ~/public_html/LDonovani/JBrowse/sample_data/leishmania/LDBPK.gff3 | sed 's/^\(\S\+\)|\S\+/\1/' | awk '{print "ld"$1,$4,$5}' | sort -k 1,1 -k 2,2 > tracks/cds.txt

