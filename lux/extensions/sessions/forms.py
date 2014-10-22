import sys
from lux import forms


__all__ = ['LoginForm', 'CreateUserForm', 'ChangePassword',
           'ForgotPasswordForm']


class LoginForm(forms.Form):
    '''The Standard login form'''
    error_message = 'Incorrect username or password'
    username = forms.CharField(max_length=30)
    password = forms.PasswordField(max_length=128)

    layout = forms.Layout(
        forms.Submit('Login', classes='btn btn-primary btn-block'),
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
    password = forms.PasswordField(label='New password',
                                   min_length=6, max_length=60)
    password_repeat = forms.PasswordField(label='Confirm new password')

    layout = forms.Layout(
        submits=forms.Submit('Update password',
                             classes='btn btn-primary'),
        labels=False,
        ngmodel=True,
        ngcontroller='userController')


class ChangePassword2(forms.Form):
    password = forms.PasswordField(label='New password',
                                   min_length=6, max_length=60)
    password_repeat = forms.PasswordField(label='Confirm new password')

    layout = forms.Layout(
        submits=forms.Submit('Reset password',
                             classes='btn btn-primary'),
        labels=False,
        ngmodel=True,
        ngcontroller='userController')


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()

    layout = forms.Layout(
        submits=forms.Submit('Submit', classes='btn btn-primary'),
        labels=False,
        ngmodel=True,
        ngcontroller='userController')
