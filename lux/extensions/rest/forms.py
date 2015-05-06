import sys
from lux import forms


__all__ = ['LoginForm',
           'CreateUserForm',
           'ChangePasswordForm',
           'EmailForm']


class LoginForm(forms.Form):
    '''The Standard login form'''
    error_message = 'Incorrect username or password'
    username = forms.CharField(required=True, minlength=6, maxlength=30)
    password = forms.PasswordField(required=True, minlength=6, maxlength=128)

    layout = forms.Layout(
        forms.Fieldset(all=True),
        forms.Submit(
            'Login',
            disabled="form.$invalid"),
        showLabels=False)


class PasswordForm(forms.Form):
    password = forms.PasswordField(required=True, minlength=6, maxlength=128)
    password_repeat = forms.PasswordField(
        label='confirm password',
        data_check_repeat='password')

    layout = forms.Layout(
        forms.Fieldset('password', 'password_repeat'),
        forms.Submit('Reset password'),
        showLabels=False)


class CreateUserForm(PasswordForm):
    username = forms.CharField(required=True, minlength=6, maxlength=30)
    email = forms.EmailField(required=True)

    layout = forms.Layout(
        forms.Fieldset('username', 'email', 'password', 'password_repeat'),
        forms.Submit(
            'Sign up',
            classes='btn btn-primary btn-block',
            disabled="form.$invalid"),
        showLabels=False,
        directive='user-form')


class ChangePasswordForm(PasswordForm):
    old_password = forms.PasswordField()

    layout = forms.Layout(
        forms.Fieldset('old_password', 'password', 'password_repeat'),
        forms.Submit('Update password', classes='btn btn-primary'),
        showLabels=False)


class EmailForm(forms.Form):
    email = forms.EmailField(label='Enter your email address')

    layout = forms.Layout(
        forms.Fieldset(all=True),
        forms.Submit('Submit', classes='btn btn-primary'),
        showLabels=False)
