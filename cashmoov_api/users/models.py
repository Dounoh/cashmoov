import uuid
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db.models import EmailField
from django.db import models
from django.utils.translation import gettext_lazy as _

from cashmoov_api.common.models import Base
from .managers import UserManager



class User(AbstractUser,Base):
    """
    Default custom user model for Oil Transport.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    id = models.BigAutoField(primary_key=True)
    email = EmailField(_("email address"), unique=True)
    username = None  
    # picture = models.ImageField(
    #     upload_to=Base.change_file_name,
    #     blank=True,null=True,verbose_name="user picture",
    #     )
    address = models.CharField(max_length=50, null=True, blank=True)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name']

