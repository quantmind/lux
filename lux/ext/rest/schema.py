from lux.models import Schema, fields


class PasswordSchema(Schema):
    password = fields.Password(maxlength=128)
    password_repeat = fields.Password(
        label='Confirm password',
        data_check_repeat='password'
    )

    def clean(self):
        password = self.cleaned_data['password']
        password_repeat = self.cleaned_data['password_repeat']
        if password != password_repeat:
            raise fields.ValidationError('Passwords did not match')


class CreateUserSchema(PasswordSchema):
    username = fields.Slug(maxlength=30)
    email = fields.Email()


class ChangePasswordSchema(PasswordSchema):
    old_password = fields.Password(maxlength=128)


class EmailSchema(Schema):
    email = fields.Email(label='Your email address')


class NewTokenSchema(Schema):
    """Schema to create tokens for the current user"""
    description = fields.String(maxlength=256, html_type='textarea')
