import uuid

import numpy as np
from django.db import models
from pgvector.django import VectorField

from cashmoov_api.common.models import Base


class Document(models.Model):
    training = "training"
    conversation = "conversation"

    source_type_choices = (
        (training, "training"),
        (conversation, "conversation"),
    )

    slug = models.SlugField(
        unique=True, default=lambda: str(uuid.uuid4()), max_length=255
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    # embedding = VectorField(dimensions=768, null=True)
    embedding = VectorField(dimensions=768, null=True)
    embedding_model = models.CharField(
        max_length=100, default="intfloat/multilingual-e5-base"
    )
    source_type = models.CharField(
        max_length=50, choices=source_type_choices, default=training
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Group(Base):
    name = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.name


class Chatbot(Base):
    username = models.CharField(max_length=250)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="chatbots", null=True
    )
    question = models.TextField()
    answers = models.TextField(null=True)
    used_for_training = models.BooleanField(default=False)
    validated_for_training = models.BooleanField(default=False)
    # assistant_answer = models.CharField(null=True)

    def __str__(self):
        return self.username
