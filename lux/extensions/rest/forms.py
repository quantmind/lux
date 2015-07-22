from lux import forms


__all__ = ['LoginForm',
           'CreateUserForm',
           'ChangePasswordForm',
           'EmailForm']


class LoginForm(forms.Form):
    '''The Standard login form'''
    error_message = 'Incorrect username or password'
    username = forms.CharField(required=True, maxlength=30)
    password = forms.PasswordField(required=True, maxlength=128)


class PasswordForm(forms.Form):
    password = forms.PasswordField(required=True, maxlength=128)
    password_repeat = forms.PasswordField(
        label='Confirm password',
        data_check_repeat='password')

    def clean(self):
        password = self.cleaned_data['password']
        password_repeat = self.cleaned_data['password_repeat']
        if password != password_repeat:
            raise forms.ValidationError('Passwords did not match')


class CreateUserForm(PasswordForm):
    username = forms.CharField(required=True, maxlength=30)
    email = forms.EmailField(required=True)


class ChangePasswordForm(PasswordForm):
    pass


class EmailForm(forms.Form):
    email = forms.EmailField(label='Enter your email address')
