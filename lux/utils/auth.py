from pulsar import PermissionDenied, Http401


def ensure_authenticated(request):
    """
    Ensures the request is by an authenticated user; raises a 401 otherwise
    :param request:     request object
    :return:            user object
    """
    user = request.cache.user
    if not user or not user.is_authenticated():
        raise Http401('Token', 'Requires authentication')
    return user


def check_permission(request, resource, action):
    """
    Checks whether the current user has a permission
    :param request:     request object
    :param resource:    resource to check permission for
    :param action:      action/actions tio perform
    :return:            True
    :raise:             PermissionDenied if the user doesn't have the
                        permission checked
    """
    backend = request.cache.auth_backend
    if backend.has_permission(request, resource, action):
        return True
    raise PermissionDenied


def normalise_email(email):
    """
    Normalise the address by lowercasing the domain part of the email
    address.
    """
    if email:
        email_name, domain_part = email.strip().rsplit('@', 1)
        email = '@'.join([email_name, domain_part.lower()])
    return email
