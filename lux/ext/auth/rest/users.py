from lux.extensions.rest import CRUD

from .user import UserModel


class UserCRUD(CRUD):
    """CRUD views for users
    """
    model = UserModel.create(
        updateform='user'
    )
