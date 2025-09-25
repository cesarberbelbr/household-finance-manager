from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Custom user model inheriting from AbstractUser.
    This allows for future customization of user fields.
    Pass is used as we don't need additional fields yet.
    """
    pass