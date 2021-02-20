.. django-windowsauth documentation master file, created by
   sphinx-quickstart on Sun Dec 13 18:33:22 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

django-windowsauth
==================

**Easy integration and deployment of Django projects into Windows Environments.**

Features
--------
- Deploy to Microsoft IIS quickly using `wfastcgi <https://pypi.org/project/wfastcgi/>`_ and ``createwebconfig`` command
- Authenticate via `IIS's Windows Authentication <https://docs.microsoft.com/en-us/iis/configuration/system.webserver/security/authentication/windowsauthentication/#:~:text=You%20can%20use%20Windows%20authentication,Windows%20accounts%20to%20identify%20users.&text=When%20you%20install%20and%20enable,the%20default%20protocol%20is%20Kerberos.>`_
- Authorize against Active Directory using `ldap3 <https://ldap3.readthedocs.io/en/latest/>`_ package
- Manage LDAP connections for easy integrations
- Debug using `django-debug-toolbar <https://django-debug-toolbar.readthedocs.io/en/latest/>`_
- **NEW** Create Task Schedulers for Django management commands

.. toctree::
   :maxdepth: 1
   :caption: Installation and Setup

   installation/quick_start
   installation/installation
   installation/publish
   installation/migration

.. toctree::
   :maxdepth: 1
   :caption: How-to Guides

   howto/serve_static
   howto/create_tasks
   howto/custom_user_fields
   howto/using_ldap_manager
   howto/manage_secrets
   howto/securing_ldap
   howto/custom_error_pages
   howto/debug_toolbar
   howto/collect_metrics

.. toctree::
   :maxdepth: 1
   :caption: Reference

   reference/settings_reference
   reference/ldap_settings
   reference/decorators
   reference/signals
   reference/models
   reference/management_commands
   reference/change_log
