import sys
from lux import forms


__all__ = ['LoginForm', 'CreateUserForm', 'ChangePassword',
           'ForgotPasswordForm']


class LoginForm(forms.Form):
    '''The Standard login form'''
    error_message = 'Incorrect username or password'
    username = forms.CharField(maxlength=30)
    password = forms.PasswordField(maxlength=128)

    layout = forms.Layout(
        forms.Fieldset(all=True),
        forms.Submit(
            'Login',
            classes='btn btn-primary btn-block',
            disabled="form.$invalid"),
        showLabels=False)


class CreateUserForm(forms.Form):
    username = forms.CharField(minlength=6, maxlength=30,
                               helpText='between 6 and 30 characters')
    email = forms.EmailField()
    password = forms.PasswordField(minlength=6, maxlength=60)
    password_repeat = forms.PasswordField(label='confirm password',
        data_check_repeat='password')

    layout = forms.Layout(
        forms.Fieldset(all=True),
        forms.Submit(
            'Sign up',
            classes='btn btn-primary btn-block',
            disabled="form.$invalid"),
        showLabels=False,
        directive='user-form')


class ChangePassword(forms.Form):
    username = forms.HiddenField()
    old_password = forms.PasswordField(required=False)
    password = forms.PasswordField(label='New password',
                                   min_length=6, max_length=60)
    password_repeat = forms.PasswordField(
        label='Confirm new password',
        data_check_repeat='ChangePassword.password')

    layout = forms.Layout(
        forms.Fieldset(all=True),
        forms.Submit('Update password', classes='btn btn-primary'),
        showLabels=False)


class ChangePassword2(forms.Form):
    password = forms.PasswordField(label='New password',
                                   min_length=6, max_length=60)
    password_repeat = forms.PasswordField(label='Confirm new password')

    layout = forms.Layout(
        forms.Fieldset(all=True),
        forms.Submit('Reset password', classes='btn btn-primary'),
        showLabels=False)


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()

    layout = forms.Layout(
        forms.Fieldset(all=True),
        forms.Submit('Submit', classes='btn btn-primary'),
        showLabels=False)
