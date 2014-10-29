class IntData: 
    """
    Generic class for data
    Possible thinks to implement
    
    .. attribute:: path
    .. attribute:: delimiter
    .. attribute:: header
    .. attribute:: fieldsB
    .. attribute:: fieldsG
    .. attribute:: data
    .. attribute:: min
    .. attribute:: max
    .. attribute:: dataTypes
    .. attribute:: tracks
    
    list with the behavioral fields corresponding each column in the original file
     
    """
    def __init__(self, path, ontology_dict, **kwargs):
        self.path = check_path(path)