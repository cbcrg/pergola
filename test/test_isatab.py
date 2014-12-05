# easy_install biopy-isatab

from bcbio import isatab

rec = isatab.parse("/Users/jespinosa/software/isaTabTools/ISAcreator-1.7.7/isatab files/test2_int2GB")
rec = isatab.parse("/home/kadomu/Dropbox/isaTabTools/ISAcreator-1.7.7/isatab files/test2_int2GB")
study = rec.studies[0]
assay = rec.studies[0].assays[0]

# List of all files inside an assay
for node in assay.nodes: print node


node=study.nodes["CRG.Group-1.Subject-1"]



assay.metadata['Study Assay Technology Platform'] 

rec = isatab.parse("/Users/jespinosa/software/isaTabTools/ISAcreator-1.7.7/isatab files/BII-I-1")
study= rec.studies[0]
print study.nodes.keys()

##Number of studies
len(rec.studies)

for i in rec.studies:
    print i
    
node=study.nodes["CRG.Group-1.Subject-1"]
node.metadata["Organism"]



### Old code of pergola_isatab
rec = isatab.parse(args.input)
study= rec.studies[0]
#     print study.nodes.keys() 

#Sample name are the key shared by both study and assay

for i in rec.studies:
#         print "studies are", i
    
    for j in i.assays:
        #print "assays are:", j
        for file in j.nodes.keys():
            print "file to process is ------------------",file


# parse_isatab_assays(isatab_dir) function with all prints            
def parse_isatab_assays (isatab_dir):
    """ 
    Read all files contained in isatab format to be processed by pergola
    
    :param isatab_dir: :py:func:`str` containing the path to isatab data folder
    
    :return: :py:func:`dict` of files to be processed by pergola
     
    """
    dict_files = {}
    
    if not path.isdir(isatab_dir):
        raise ValueError ("Argument input must be a folder containning data in isatab format")
    
    rec = isatab.parse(isatab_dir)
    
    #Sample name are the key shared by both study and assay
    for i in rec.studies:
#         print "studies are", i
#         print "..................",i.assays
#         print i.assays.node['metadata']
        for j in i.assays:
            print "assays are:", j
#             print "-----------", j.nodes
            for file in j.nodes.keys():
                print j.nodes[file].metadata['Sample Name']
                dict_files[j.nodes[file].metadata['Sample Name']] = file
                pass
#                 print "file to process is ------------------",file
    return dict_files            
