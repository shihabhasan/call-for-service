# Code adapted from https://github.com/ojii/django-load

from django.conf import settings
from importlib import import_module


def plugin_list():
    return settings.PLUGINS


def get_module(app, modname, verbose, failfast):
    """
    Internal function to load a module from a single app.
    """
    module_name = '%s.%s' % (app, modname)
    try:
        module = import_module(module_name)
    except ImportError as e:
        if failfast:
            raise e
        elif verbose:
            print("Could not load %r from %r: %s" % (modname, app, e))
        return None
    if verbose:
        print("Loaded %r from %r" % (modname, app))
    return module


def load(modname, verbose=False, failfast=False):
    """
    Loads all modules with name 'modname' from all installed apps.

    If verbose is True, debug information will be printed to stdout.

    If failfast is True, import errors will not be surpressed.
    """
    for app in plugin_list():
        get_module(app, modname, verbose, failfast)


def iterload(modname, verbose=False, failfast=False):
    """
    Loads all modules with name 'modname' from all installed apps and returns
    and iterator of those modules.

    If verbose is True, debug information will be printed to stdout.

    If failfast is True, import errors will not be surpressed.
    """
    for app in plugin_list():
        module = get_module(app, modname, verbose, failfast)
        if module:
            yield module