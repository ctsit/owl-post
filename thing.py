from VDO import VivoDomainObject

class Thing(object):
    def __init__(self, connection):
        #might have to swap type and category
        self.connection = connection
        self.type = "thing"

        self.n_number = None
        self.name = None
        self.category = None

        self.details = ['category']