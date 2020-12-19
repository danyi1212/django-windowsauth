
Collect Metrics
===============

Sometimes collecting metrics and usage data can be very helpful in detecting mistakes and problems.
Using ``ldap3`` Connection Metrics system, you are able to get an inside look about the connections.

Installation
------------

First, you will need to add the ``ldap_metrics`` app to the ``INSTALLED_APPS`` setting:

.. code-block:: python
    :emphasize-lines: 4

    INSTALLED_APPS = [
        ...
        'windows_auth',
        'windows_auth.ldap_metrics',
        ...
    ]

Next you will need to migrate to create the LDAP Usage table::

$ py manage.py migrate ldap_metrics

Usage
-----

In order to start collecting usage metrics, you will configure the ``COLLECT_METRICS`` LDAP Setting for each domain.
For example:

.. code-block:: python
    :emphasize-lines: 7

    WAUTH_DOMAINS = {
        "EXAMPLE": LDAPSettings(
            SERVER="example.local",
            SEARCH_BASE="DC=example,DC=local",
            USERNAME="EXAMPLE\\bind_account",
            PASSWORD="*********",
            COLLECT_METRICS=True,
        ),
    }

Now, every time a Django process exists, the LDAP Connection usage metrics will be saved.
The connection metrics can be viewed in your Django project's admin site.

.. note::
    In case you want to collect metrics only when developing, you can set this setting to ``DEBUG``.
