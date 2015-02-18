import odm


class Page(odm.Model):
    url = odm.CharField()
    title = odm.CharField()
    description = odm.TextField()
    body = odm.TextField()
    template = odm.CharField(default='home.html')
