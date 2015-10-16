from .base import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

INSTALLED_APPS += (
    'django_nose',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True
}