from lux.models import registry, html
from . import schema


registry['reset-password'] = html.Layout(
    schema.PasswordSchema(),
    html.Fieldset('password', 'password_repeat'),
    html.Submit('Change password', classes='btn btn-success')
)


registry['change-password'] = html.Layout(
    schema.ChangePasswordSchema(),
    html.Fieldset('old_password', 'password', 'password_repeat'),
    html.Submit('Change password', classes='btn btn-success')
)


registry['new-token'] = html.Layout(
    schema.NewTokenSchema(),
    html.Fieldset(all=True),
    html.Submit('Create token', classes='btn btn-success'),
    resultHandler='responseHandler'
)


registry['signup'] = html.Layout(
    schema.CreateUserSchema(),
    html.Fieldset('username', 'email', 'password', 'password_repeat'),
    html.Submit('Sign up', disabled="form.$invalid"),
    showLabels=False,
    directive='user-form',
    resultHandler='signUp'
)


registry['password-recovery'] = html.Layout(
    schema.EmailSchema(),
    html.Fieldset(all=True),
    html.Submit('Submit'),
    showLabels=False,
    resultHandler='passwordRecovery'
)
