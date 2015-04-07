from .. import views


class CRUD(views.CRUD):
    '''CRUD Router for SQL models
    '''
    def collection(self, request, limit, offset, text):
        odm = request.app.odm('sql')
        with odm.begin() as session:
            query = session.query(odm[self.model])
            data = query.limit(limit).offset(offset).all()
            return self.serialise(request, data)


