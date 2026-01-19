from django.db import models
from cashmoov_api.common.models import Base
import numpy as np
import uuid
from pgvector.django import VectorField

class Document(models.Model):
    training ="training"
    conversation ="conversation"

    source_type_choices = (
        (training, "training"),
        (conversation, "conversation"),
    )
    
    slug = models.SlugField(unique=True, default=uuid.uuid4, max_length=255)
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    embedding = VectorField(dimensions=384, null=True)
    embedding_model = models.CharField(
        max_length=100,
        default="all-MiniLM-L6-v2"
    )
    source_type = models.CharField(
        max_length=50,
        choices=source_type_choices,
        default=training
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    







