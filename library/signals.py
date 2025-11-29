from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Book

@receiver(pre_save, sender=Book)
def set_available_copies(sender, instance, **kwargs):
    # If this is a new book (no pk yet), set available_copies to total_copies
    if not instance.pk:
        instance.available_copies = instance.total_copies