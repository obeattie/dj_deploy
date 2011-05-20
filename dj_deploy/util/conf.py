"""Tools for working with django.conf.settings."""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

def get_setting(name, default=None):
    """Fetches the attribute with the passed name from settings.conf, either
       raising ImproperlyConfigured if no default was passed, or retuning the
       default if it was."""
    try:
        return getattr(settings, name)
    except AttributeError:
        if default:
            return default
        raise ImproperlyConfigured, 'You must set the setting %r' % name
