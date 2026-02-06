from rest_framework import serializers
from djoser.serializers import (
    UserCreateSerializer as UserCreateSerializerBase,
    UserSerializer as UserSerializerBase,
)
from django.db import transaction
from django.utils.crypto import get_random_string
from cashmoov_api.users.models import User


# class UserSerializer(serializers.ModelSerializer[User]):
#     class Meta:
#         model = User
#         fields = ['slug',"first_name", "last_name", "email"]



class UserCreateSerializer(UserCreateSerializerBase):
    password = serializers.CharField(
        write_only=True,
        required=False,
        help_text="Laisser ce champ vide pour qu'il soit generer  automatiquement",
    )

    class Meta(UserCreateSerializerBase.Meta):
        fields = UserCreateSerializerBase.Meta.fields + (
            "user_type",
            "address",
            "slug",
        )
        read_only_fields = ("slug",)


    def validate(self, data):
        if self.instance is None:
            data["password"] = get_random_string(length=13)
        validated_data = super().validate(data)
        return validated_data

    @transaction.atomic
    def create(self, validated_data):
        user = super().create(validated_data)
        return user



class UserDetailSerializer(UserSerializerBase):
    class Meta(UserSerializerBase.Meta):
        fields = UserSerializerBase.Meta.fields + (
            "first_name",
            "last_name",
            "address",
            "user_type"
            )
        read_only_fields = ("slug",)


class CurrentUserDetailSerializer(UserSerializerBase):
    class Meta:
        model = User
        fields = (
            "slug",
            "first_name",
            "last_name",
            "email",
            "address",
            "user_type",
            )
        read_only_fields = ('slug','email',)


class UserUpdateSerializer(UserSerializerBase):

    class Meta(UserSerializerBase.Meta):
        fields = UserSerializerBase.Meta.fields + ("phone","profile", "location", "agency", "picture","user_type",)
        read_only_fields = ("slug",)
        extra_kwargs = {
            "password": {"write_only": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, data):
        if self.instance.is_active and data.get("email") and data["email"] != self.instance.email:
            raise serializers.ValidationError("Vous ne pouvez pas changer l'email d'un utilisateur actif")
        return super().validate(data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def create(self, validated_data):
        raise NotImplementedError("Vous ne pouvez pas creer un utilisateur avec ce serializer")
