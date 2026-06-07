#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.

This script is the entry point for all Django management commands.
It allows you to interact with your project in various ways.

Common commands:
- python manage.py runserver          : Start development server
- python manage.py makemigrations     : Create database migrations
- python manage.py migrate            : Apply database migrations
- python manage.py createsuperuser    : Create admin user
- python manage.py collectstatic      : Collect static files
- python manage.py shell              : Open Python shell with Django
- python manage.py test               : Run tests
"""

import os
import sys


def main():
    """
    Run administrative tasks.
    This is the main entry point for Django management commands.
    """
    # Set the default Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maternalmate.settings')
    
    try:
        # Import Django's command-line utility
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Raise error if Django is not installed
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Execute the command passed via command line
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()


# ============================================================================
# USEFUL MANAGEMENT COMMANDS FOR MATERNALMATE:
# ============================================================================
#
# DATABASE MANAGEMENT:
# --------------------
# python manage.py makemigrations        # Create new migrations
# python manage.py migrate               # Apply migrations to database
# python manage.py showmigrations        # Show migration status
# python manage.py sqlmigrate core 0001  # Show SQL for migration
# python manage.py dbshell               # Open database shell
#
# USER MANAGEMENT:
# ----------------
# python manage.py createsuperuser       # Create admin user
# python manage.py changepassword <user> # Change user password
#
# DEVELOPMENT:
# ------------
# python manage.py runserver             # Start dev server (port 8000)
# python manage.py runserver 8080        # Start dev server (port 8080)
# python manage.py runserver 0.0.0.0:8000 # Allow external connections
# python manage.py shell                 # Interactive Python shell
# python manage.py shell_plus            # Enhanced shell (if installed)
#
# STATIC FILES:
# -------------
# python manage.py collectstatic         # Collect static files
# python manage.py findstatic <file>     # Find static file location
#
# TESTING & DEBUGGING:
# --------------------
# python manage.py test                  # Run all tests
# python manage.py test core             # Run tests for 'core' app
# python manage.py check                 # Check for project issues
# python manage.py validate              # Validate models
#
# DATA MANAGEMENT:
# ----------------
# python manage.py dumpdata              # Export database to JSON
# python manage.py loaddata <file>       # Import data from JSON
# python manage.py flush                 # Clear database (CAUTION!)
#
# CUSTOM COMMANDS (if you create them):
# --------------------------------------
# python manage.py train_model           # Train AI model (if implemented)
# python manage.py send_alerts           # Send health alerts (if implemented)
#
# ============================================================================