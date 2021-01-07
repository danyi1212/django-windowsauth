
Debug with django-debug-toolbar
===============================

When using LDAP throughout your project, it is useful to see what operations did perform on the server side.
This can be done using the ``django-debug-toolbar`` with the `LDAP Panel`` provided with this module.

This panel shows you the metrics for each domain (if you have configured them to collect metrics),
and every operation the server perform against the LDAP server, including the LDAP filter and every each entry it responded with.

Installation
------------

In order to view the LDAP Panel to the debug toolbar, you will need to install the ``django-debug-toolbar`` package:

$ pip install django-debug-toolbar

And follow the installation guide on ``django-debug-toolbar`` docs https://django-debug-toolbar.readthedocs.io/en/latest/installation.html

Then to add the LDAP Panel, insert it to the `DEBUG_TOOLBAR_PANELS setting <https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-panels>`_ like so:

.. code-block:: python

    DEBUG_TOOLBAR_PANELS = [
        # ...
        'windows_auth.panels.LDAPPanel',
        # ...
    ]

To enable all of the LDAP Panel feature, you may want to enable metrics collection for all your domains:

.. code-block:: python
    :emphasize-lines: 7, 14

    WAUTH_DOMAINS = {
        "EXAMPLE1": LDAPSettings(
            SERVER="example.local",
            SEARCH_BASE="DC=example,DC=local",
            USERNAME="EXAMPLE\\bind_account",
            PASSWORD="<super secret>",
            COLLECT_METRICS=True,
        ),
        "EXAMPLE2": {
            "SERVER": "example.local",
            "SEARCH_BASE": "DC=example,DC=local",
            "USERNAME": "EXAMPLE\\bind_account",
            "PASSWORD": "<super secret>",
            "COLLECT_METRICS": True,
        },
    }
