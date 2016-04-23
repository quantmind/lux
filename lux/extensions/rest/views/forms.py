from lux import forms


class LoginForm(forms.Form):
    '''The Standard login form'''
    error_message = 'Incorrect username or password'
    username = forms.SlugField(maxlength=30)
    password = forms.PasswordField(maxlength=128)


class PasswordForm(forms.Form):
    password = forms.PasswordField(maxlength=128)
    password_repeat = forms.PasswordField(
        label='Confirm password',
        data_check_repeat='password')

    def clean(self):
        password = self.cleaned_data['password']
        password_repeat = self.cleaned_data['password_repeat']
        if password != password_repeat:
            raise forms.ValidationError('Passwords did not match')


class CreateUserForm(PasswordForm):
    username = forms.SlugField(maxlength=30)
    email = forms.EmailField()


class ChangePasswordForm(PasswordForm):
    old_password = forms.PasswordField(maxlength=128)


class EmailForm(forms.Form):
    email = forms.EmailField(label='Your email address')


class NewTokenForm(forms.Form):
    """Form to create tokens for the current user"""
    description = forms.TextField(maxlength=256)
