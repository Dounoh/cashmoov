
import string
import uuid

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string
from django.utils.text import slugify


def get_unique_slug(instance):
    """Génère un slug unique pour un modèle donné en s'assurant qu'il n'existe pas déjà dans la base de données."""
    klass = instance.__class__
    unique = False
    while not unique:
        new_slug = get_random_string(40, allowed_chars=string.ascii_letters + string.digits)
        unique = not klass.objects.filter(slug=new_slug).exists()  # Vérifie si le slug existe déjà
    return new_slug


class Base(models.Model):
    id = models.UUIDField(editable=False, primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(editable=False, unique=True, default=None, max_length=255)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        abstract = True

    @staticmethod
    def is_valid_uuid(v):
        try:
            uuid.UUID(v)
            return True
        except ValueError:
            return False

    def change_file_name(instance, filename):
        extension = filename[filename.find('.'):]
        name = slugify(instance.slug) + '' + extension

        app_model = ContentType.objects.get_for_model(instance)
        return "{0}/{1}/{2}".format(app_model.app_label, app_model.model, name)

    def delete(self):
        # self.deleted_at = timezone.now()
        # self.save()
        return super().delete()

    @classmethod
    def normalize_email(cls, email):
        """
        Normalize the email address by lowercasing the domain part of it.
        """
        email = email or ""
        try:
            email_name, domain_part = email.strip().rsplit("@", 1)
        except ValueError:
            pass
        else:
            email = email_name + "@" + domain_part.lower()
        return email


class EmailNullField(models.EmailField):
    description = "EmailField that stores NULL and its value must be unique"

    def get_db_prep_value(self, value, connection=None, prepared=False):
        value = super().get_db_prep_value(value, connection, prepared)
        if value == "":
            return None
        else:
            return value


class PhoneField(models.CharField):
    description = "Representes a field that can handle phone numbers"

    def get_db_prep_value(self, value, connection=None, prepared=False):
        value = super().get_db_prep_value(value, connection, prepared)
        if value == "":
            return None
        else:
            return value
