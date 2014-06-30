import sys
from lux import forms


__all__ = ['LoginForm', 'CreateUserForm', 'ChangePassword']


class LoginForm(forms.Form):
    '''The Standard login form'''
    error_message = 'Incorrect username or password'
    username = forms.CharField(max_length=30)
    password = forms.PasswordField(max_length=128)

    layout = forms.Layout(
        submits=forms.Submit('Login', classes='btn btn-primary btn-block'),
        labels=False,
        ngmodel=True,
        ngcontroller='userController')


class CreateUserForm(forms.Form):
    username = forms.CharField(min_length=6, max_length=30)
    email = forms.EmailField()
    password = forms.PasswordField(min_length=6, max_length=60)
    password_repeat = forms.PasswordField()

    layout = forms.Layout(
        submits=forms.Submit('Sign up', classes='btn btn-primary btn-block'),
        labels=False,
        ngmodel=True,
        ngcontroller='userController')


class ChangePassword(forms.Form):
    username = forms.HiddenField()
    old_password = forms.PasswordField(required=False)
    new_password = forms.PasswordField()
    confirm_new_password = forms.PasswordField()

    layout = forms.Layout(
        submits=forms.Submit('Update password',
                             classes='btn btn-primary'),
        labels=False,
        ngmodel=True,
        ngcontroller='userController')
