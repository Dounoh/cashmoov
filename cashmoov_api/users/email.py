from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.crypto import get_random_string

from djoser import utils
from djoser.conf import settings

from djoser.email import ActivationEmail, ConfirmationEmail


class UserCreatedEmail(ActivationEmail):
    template_name = "emails/user_created.html"

    def get_context_data(self):

        context = super().get_context_data()

        user = context.get("user")
        password = get_random_string(length=13)
        user.set_password(password)
        user.save()
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = settings.ACTIVATION_URL.format(**context)
        # print(user, user.email)
        
        context["password"] = password
        return context


class UserCreatedConfirmationEmail(ConfirmationEmail):
    template_name = "emails/user_created_confirmation.html"

    def get_context_data(self):
        context = super().get_context_data()

        user = context.get("user")
        password = get_random_string(length=13)
        user.set_password(password)
        user.save()
        context["password"] = password

        return context