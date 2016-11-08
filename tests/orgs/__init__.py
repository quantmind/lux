from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, cast

from lux import forms
from lux.core import LuxExtension
from lux.utils import test
from lux.extensions import odm
from lux.extensions.rest import CRUD
from lux.extensions.organisations import ownership


class Extension(LuxExtension):

    def api_sections(self, app):
        yield ownership.owned_model(
            app, ProjectCrud(), 'name', cast_id=cast_int
        )


Model = odm.model_base('orgtest')


class Project(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    subject = Column(String(250))
    deadline = Column(String(250))
    outcome = Column(String(250))
    created = Column(DateTime, default=datetime.utcnow)


class CreateProject(forms.Form):
    name = forms.SlugField(min_length=2, max_length=32,
                           validator=ownership.UniqueField('projects'))
    subject = forms.CharField(max_length=250, required=False)
    private = forms.BooleanField()


def cast_int(value):
    return cast(value, Integer)


class ProjectCrud(CRUD):
    model = odm.RestModel(
        'project',
        CreateProject
    )


class AppTestCase(test.AppTestCase):
    config_file = 'tests.orgs.config'

    @classmethod
    def create_admin_jwt(cls):
        return cls.client.run_command('master_app')

    @classmethod
    async def beforeAll(cls):
        request = await cls.client.post(
            cls.api_url('authorizations'),
            json=dict(username='testuser', password='testuser'),
            jwt=cls.admin_jwt
        )
        cls.super_token = cls._test.json(request.response, 201)['id']

    @test.green
    def _test_entity(self, username, type):
        odm = self.app.odm()
        with odm.begin() as session:
            entity = session.query(odm.entity).filter_by(username=username)
            self.assertEqual(entity.one().type, type)
