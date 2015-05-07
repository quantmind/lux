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


class PasswordForm(forms.Form):
    password = forms.PasswordField(required=True, minlength=6, maxlength=128)
    password_repeat = forms.PasswordField(
        label='confirm password',
        data_check_repeat='password')


class CreateUserForm(PasswordForm):
    username = forms.CharField(required=True, minlength=6, maxlength=30)
    email = forms.EmailField(required=True)


class ChangePasswordForm(PasswordForm):
    old_password = forms.PasswordField()


class EmailForm(forms.Form):
    email = forms.EmailField(label='Enter your email address')
