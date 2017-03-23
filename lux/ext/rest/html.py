from lux.models import html
from . import schema


html.reg['reset-password'] = html.Layout(
    schema.PasswordSchema(),
    html.Fieldset('password', 'password_repeat'),
    html.Submit('Change password', classes='btn btn-success')
)


html.reg['change-password'] = html.Layout(
    schema.ChangePasswordSchema(),
    html.Fieldset('old_password', 'password', 'password_repeat'),
    html.Submit('Change password', classes='btn btn-success')
)


html.reg['new-token'] = html.Layout(
    schema.NewTokenSchema(),
    html.Fieldset(all=True),
    html.Submit('Create token', classes='btn btn-success'),
    resultHandler='responseHandler'
)


html.reg['login'] = html.Layout(
    schema.LoginSchema(),
    html.Fieldset(all=True),
    html.Submit('Login'),
    showLabels=False,
    resultHandler='redirect',
    redirectTo=lambda form: form.request.config['POST_LOGIN_URL']
)


html.reg['signup'] = html.Layout(
    schema.CreateUserSchema(),
    html.Fieldset('username', 'email', 'password', 'password_repeat'),
    html.Submit('Sign up', disabled="form.$invalid"),
    showLabels=False,
    directive='user-form',
    resultHandler='signUp'
)


html.reg['password-recovery'] = html.Layout(
    schema.EmailSchema(),
    html.Fieldset(all=True),
    html.Submit('Submit'),
    showLabels=False,
    resultHandler='passwordRecovery'
)
