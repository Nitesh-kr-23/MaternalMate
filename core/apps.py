# core/apps.py
"""
Application configuration for the core app
Defines the app name and configuration settings
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuration class for the 'core' application
    """
    # Use BigAutoField for primary keys (Django 3.2+)
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Application name (must match the folder name)
    name = 'core'
    
    # Human-readable name for the admin interface
    verbose_name = 'MaternalMate Core'
    
    def ready(self):
        """
        Called when Django starts
        Import signals to enable automatic UserProfile creation
        """
        # Import signals to register them
        import core.signals