
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Document, Page

@receiver(pre_delete, sender=Document)
def delete_document_files(sender, instance, **kwargs):
    """Delete associated files when a Document is deleted"""
    if instance.thumbnail:
        instance.thumbnail.delete(save=False)

@receiver(pre_delete, sender=Page)
def delete_page_files(sender, instance, **kwargs):
    """Delete associated files when a Page is deleted"""
    if instance.image:
        instance.image.delete(save=False)
    if instance.thumbnail:
        instance.thumbnail.delete(save=False)