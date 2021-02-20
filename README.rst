django-windowsauth
==================

.. image:: https://readthedocs.org/projects/django-windowsauth/badge/?version=latest
    :target: https://django-windowsauth.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
    
.. image:: https://img.shields.io/badge/Maintained-yes-green.svg
    :target: https://github.com/danyi1212/django-windowsauth/graphs/commit-activity
    :alt: Maintained
   
.. image:: https://static.pepy.tech/personalized-badge/django-windowsauth?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads&service=github
    :target: https://pepy.tech/project/django-windowsauth

**Easy integration and deployment of Django projects into Windows Environments.**

| Documentation is available at https://django-windowsauth.readthedocs.io/en/latest/
| PyPI Package at https://pypi.org/project/django-windowsauth/
| Django Packages at https://djangopackages.org/packages/p/django-windowsauth/

Requirements:

- Python (3.6, 3.7, 3.8, 3.9)
- Django (2.2, 3.0, 3.1)

Features
~~~~~~~~
- Deploy to **Microsoft IIS** quickly using `wfastcgi <https://pypi.org/project/wfastcgi/>`_
- Authenticate via `IIS's Windows Authentication <https://docs.microsoft.com/en-us/iis/configuration/system.webserver/security/authentication/windowsauthentication/#:~:text=You%20can%20use%20Windows%20authentication,Windows%20accounts%20to%20identify%20users.&text=When%20you%20install%20and%20enable,the%20default%20protocol%20is%20Kerberos>`_.
- Authorize against **Active Directory** using `ldap3 <https://ldap3.readthedocs.io/en/latest/>`_ package
- Manage **LDAP Connections** for easy integrations
- Debug using `django-debug-toolbar <https://django-debug-toolbar.readthedocs.io/en/latest/>`_
- **NEW** Create Task Schedulers for Django management commands

Quick Start
-----------
1. Install with `pip install django-windowsauth`
2. Run `py manage.py migrate windows_auth`
3. Add "fastcgi application" with `wfastcgi-enable`
4. Configure project settings

.. code-block::  python

    INSTALLED_APPS = [
        "windows_auth",
    ]

    MIDDLEWARE = [
        # ...
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.RemoteUserMiddleware',
        'windows_auth.middleware.UserSyncMiddleware',
        # ...
    ]

    AUTHENTICATION_BACKENDS = [
        "windows_auth.backends.WindowsAuthBackend",
        "django.contrib.auth.backends.ModelBackend",
    ]

    WAUTH_DOMAINS = {
        "<your domain's NetBIOS Name> (EXAMPLE)": {
            "SERVER": "<domain FQDN> (example.local)",
            "SEARCH_SCOPE": "<search scope> (DC=example,DC=local)",
            "USERNAME": "<bind account username>",
            "PASSWORD": "<bind account password>",
        }
    }

    # optional
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / "static"

    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / "media"

5. Generate **web.config** files with `py manage.py createwebconfig -s -m`
6. Create new IIS Website from the project files

For more details visit the docs for installation: https://django-windowsauth.readthedocs.io/en/latest/installation/installation.html

Getting help
------------

In case you have trouble while using this module, you may use the `GitHub Disccussion <https://github.com/danyi1212/django-windowsauth/discussions>`_.

For any bug or issue, open a `new GitHub Issue <https://github.com/danyi1212/django-windowsauth/issues>`_.

Contributing
------------
