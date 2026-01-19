from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Document
from .tasks import save_embedding


@receiver(post_save, sender=Document)
def document_saved(sender, instance, created, **kwargs):
    if created:
        save_embedding.delay(instance.slug)




@receiver(post_delete, sender=Document)
def remove_document_from_faiss(sender, instance, **kwargs):
    """
    Signal qui se déclenche après la suppression d'un document.
    Il envoie le document.id à la tâche Celery pour le retirer de FAISS.
    """
    delete_from_faiss.delay(instance.id)