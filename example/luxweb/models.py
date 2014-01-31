from stdnet import odm


class Plugin(odm.StdModel):
    name = odm.SymbolField(unique=True)
    description = odm.CharField()
