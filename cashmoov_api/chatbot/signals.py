from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Document

@receiver(post_save, sender=Document)
def document_saved(sender, instance, created, **kwargs):
    if created:
        from .tasks import save_embedding
        save_embedding.delay(instance.slug)