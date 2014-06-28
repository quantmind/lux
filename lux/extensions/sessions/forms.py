import sys
from lux import forms


class LoginForm(forms.Form):
    '''The Standard login form'''
    error_message = 'Incorrect username or password'
    username = forms.CharField(max_length=30)
    password = forms.PasswordField(max_length=60)

    def clean(self):
        '''Process login'''
        request = self.request
        permissions = request.app.permissions
        username = self.cleaned_data['username']
        user = permissions.get_user(request, username=username)
        if not user:
            raise forms.ValidationError(self.error_message)
        password = self.cleaned_data['password']
        try:
            user = permissions.authenticate_and_login(
                request, user, password=password)
        except AuthenticationError:
            raise forms.ValidationError(self.error_message)
        except LoginError as e:
            raise forms.ValidationError(str(e))
        return user


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

