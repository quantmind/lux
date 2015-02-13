import odm


class User(odm.Model):
    username = ndb.CharField()
    password = ndb.CharField()
    name = ndb.CharField()
    surname = ndb.CharField()
    email = ndb.CharField()
    active = ndb.BooleanField(default=False)
    superuser = ndb.BooleanField(default=False)
    company = ndb.CharField()
    joined = ndb.DateTimeField(auto_now_add=True)
    #
    #oauths = ndb.StructuredProperty(Oauth, repeated=True)
    #messages = ndb.StructuredProperty(Message, repeated=True)
