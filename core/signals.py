# core/signals.py
"""
Django signals for automatic UserProfile creation
Automatically creates a UserProfile when a new User is created
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a new User is created
    
    Args:
        sender: The User model class
        instance: The actual User instance being saved
        created: Boolean indicating if this is a new user
        **kwargs: Additional keyword arguments
    """
    if created:
        # Only create profile for new users, not updates
        UserProfile.objects.create(user=instance)
        print(f"✓ UserProfile created for user: {instance.username}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the UserProfile whenever the User is saved
    Ensures profile stays in sync with user
    
    Args:
        sender: The User model class
        instance: The actual User instance being saved
        **kwargs: Additional keyword arguments
    """
    # Check if profile exists, create if not (safety check)
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()
        print(f"✓ UserProfile saved for user: {instance.username}")