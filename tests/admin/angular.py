from . import app


class AngularAdminTest(app.AdminTest):
    config_params = {'HTML5_NAVIGATION': True}
