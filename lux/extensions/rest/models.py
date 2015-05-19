

class RestModel:

    def __init__(self, addform=None, editform=None):
        self.addform = addform
        self.editform = editform or addform

    def columns(self, app):
        '''Return a list fields describing the entries for a given model
        instance'''
        raise NotImplementedError
