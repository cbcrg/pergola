## Urgent
- [ ] Create the first stable Pergola release

## Pending
- [ ] Eliminate files not used
- [ ] Modify tag for pergola ontology file. Now is genome_file:term, for pergola: Pergola paper
- [ ] Modify the name of pergola_rules by pergola_convert
- [ ] Create a -genome option allowing to choose the user whether to generate the genome files or not
- [ ] Borrar archivos temporales
- [ ] Make write chromosome an option (generate genome file)
- [ ] Window and window mean only reachable when bedgraph option is set, control for this. should only be reachable?
- [ ] Move jaaba files to examples folder or similar
- [ ] Modify tracks create_pybedtools documentation it has the docs of a different class
- [ ] Create first release github

## Currently working
- [ ] make the package available by pypi
- [ ] add dependencies for pypi installation
- [ ] Upload C.elegans files

## Solved
- [X] Clean all code annotations
- [X] Add jaaba_to_pergola to test_all.py
- [X] loadmat function makes library scipy a dependency of the whole package by importing parsers, separate in a different
- [X] Converting jaaba features folder to csv or pergola objects  
- [X] Add to unitest the test of the scripts
- [X] Adding pergola_rules to test, for this transform scripts into console_scripts
- [X] Checkings of the code using travis or similar tools
- [X] Create a script for jaaba wrapping all jaaba options
- [X] Implement mean of bedgraph window
- [X] Use file format conventions of bed and gff files (0, 1 etc)
- [X] Read files from ctrax
- [X] Filter by data type
- [X] bedGraph window by default should by 1 or otherwise give an option just to transform bed to bedgraph without window
- [X] Add to test the checking of the creation of bedGraph files with and without binning.
- [X] Create pergola ontology and add it to the website documentation