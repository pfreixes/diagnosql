# Pau Freixes, pfreixes@gmail.com
# 2012-12

class data_type:
    pass

class DocModel(dict):
    """
    DocModel helps you to create a kind of data that it belongs
    at your data store. 

    All defined atributos of class will be serialized into one field
    at every class instance where this field can be filled by one
    user or by one kind of distribution function
    >
    > import docmodel
    >
    > from distributions.incremental import Incremental
    > from distributions.equiprobable import Equiprobable
    > from distributions.normal import Normal 
    >
    > class DegreeValue(docmodel.DocModel):
    >     id = docmodel.int(Incremental)
    >     value = docmodel.float(Normal, 
    >                             from = -30, 
    >                             to = 50.0))
    >     timestamp = docmodel.string(Equiprobable,
    >                                 from = time.now(),
    >                                 to = time.now() + 8600 )
    >     description = docmodel.string()
    >
    > t = SensorValue()
    > t["description"] = "Filled by user"
    > print t
    """
    pass

