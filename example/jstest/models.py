from stdnet import odm


class Todo2(odm.StdModel):
    title = odm.SymbolField(index=False)
    description = odm.CharField()
    when = odm.DateTimeField(required=False)

    def __unicode__(self):
        return self.title


class Todo3(Todo2):
    pass
