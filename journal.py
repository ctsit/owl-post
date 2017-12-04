from VDO import VivoDomainObject

class Journal(VivoDomainObject):
    def __init__(self, connection):
        self.connection = connection
        self.type = "journal"
        self.category = "venue"
        
        self.n_number = None
        self.name = None
        self.details = []