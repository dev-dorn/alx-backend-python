# messaging_app/settings.py
"""
Django settings for messaging_app project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ... other existing settings ...

# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Added this line
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [  # Added this section
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ]
}

# ... other existing settings ...

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # Make sure this is included
    'chats',
]

# ... other existing settings ...

AUTH_USER_MODEL = 'chats.User'  # Make sure this is set