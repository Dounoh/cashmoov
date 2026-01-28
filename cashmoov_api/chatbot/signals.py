from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Document
from .tasks import save_embedding


@receiver(post_save, sender=Document)
def document_saved(sender, instance, created, **kwargs):
    """
    Le signal django qui se declanche quand une nouvelle information est sauvegarder
    en base de donnee.
    Elle se declanche automatiquement des qu'une info est sauvegarder en db et à son tour il
    delegue une tache celery pour faire le calcule du embedding et enregistrer en db
    """
    if created:
        save_embedding.delay(instance.slug)


# @receiver(post_delete, sender=Document)
# def remove_document_from_faiss(sender, instance, **kwargs):
#     """
#     Signal qui se déclenche après la suppression d'un document.
#     Il envoie le document.id à la tâche Celery pour le retirer de FAISS.
#     """
#     delete_from_faiss.delay(instance.id)
