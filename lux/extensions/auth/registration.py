
email_templates = {
    "subject": {
        1: "registration/activation_email_subject.txt",
        2: "registration/password_email_subject.txt"
    },
    "message": {
        1: "registration/activation_email.txt",
        2: "registration/password_email.txt"
    }
}


def send_email_confirmation(request, token, reg,
                            email_subject=None, email_message=None):
    """Send an email to user
    """
    user = reg.user
    if not user.email:
        return
    app = request.app
    site = token.url
    reg_url = token.registration_url
    psw_url = token.password_reset_url
    ctx = {'auth_key': reg.id,
           'register_url': reg_url,
           'reset_password_url': psw_url,
           'expiration_days': app.config['ACCOUNT_ACTIVATION_DAYS'],
           'email': user.email,
           'site_uri': site}

    email_subject = email_subject or email_templates['subject'][reg.type]
    email_message = email_message or email_templates['message'][reg.type]

    subject = app.render_template(email_subject, ctx)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = app.render_template(email_message, ctx)
    user.email_user(app, subject, body)
