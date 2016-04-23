from lux.forms import Layout, Fieldset, Submit, formreg

from . import forms


formreg['reset-password'] = Layout(
    forms.PasswordForm,
    Fieldset('password',
             'password_repeat'),
    Submit('Change password',
           classes='btn btn-success')
)


formreg['change-password'] = Layout(
    forms.ChangePasswordForm,
    Fieldset('old_password',
             'password',
             'password_repeat'),
    Submit('Change password',
           classes='btn btn-success')
)


formreg['new-token'] = Layout(
    forms.NewTokenForm,
    Fieldset(all=True),
    Submit('Create token', classes='btn btn-success'),
    resultHandler='responseHandler'
)


formreg['login'] = Layout(
    forms.LoginForm,
    Fieldset(all=True),
    Submit('Login', disabled="form.$invalid"),
    model='login',
    showLabels=False,
    resultHandler='login'
)


formreg['signup'] = Layout(
    forms.CreateUserForm,
    Fieldset('username',
             'email',
             'password',
             'password_repeat'),
    Submit('Sign up', disabled="form.$invalid"),
    showLabels=False,
    directive='user-form',
    resultHandler='signUp'
)


formreg['password-recovery'] = Layout(
    forms.EmailForm,
    Fieldset(all=True),
    Submit('Submit'),
    showLabels=False,
    resultHandler='passwordRecovery'
)


formreg['mailing-list'] = Layout(
    forms.EmailForm,
    Fieldset(all=True),
    Submit('Get notified'),
    showLabels=False
)
