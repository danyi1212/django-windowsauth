
Checks
======

.. glossary::

    wauth.E001
        Type: ``Error``

        Required setting ``WAUTH_DOMAINS`` is not configured. :ref:`WAUTH_DOMAINS (Required)`

.. glossary::

    wauth.W002
        Type: ``Warning``

        Found missing domain settings for LDAP users.

.. glossary::

    wauth.E003
        Type: ``Error``

        | Unable to load LDAPUser model.
        | Try running ``py manage.py migrate windows_auth``.

.. glossary::

    wauth.W004
        Type: ``Warning``

        | Unable to create LDAP connection with a configured domain.
        | Check your settings and the server.

.. glossary::

    wauth.E005
        Type: ``Error``

        | Error while creating LDAP connection with a configured domain
        | Check your settings and the server.

.. glossary::

    wauth.E006
        Type: ``Error``

        You have ``windows_auth.middleware.SimulateWindowsAuthMiddleware`` in your ``MIDDLEWARE``, but you have not configured ``WAUTH_SIMULATE_USER``. :ref:`WAUTH_SIMULATE_USER`

.. glossary::

    wauth.W010
        Type: ``Warning``, Deploy only

        You should not have ``windows_auth.middleware.SimulateWindowsAuthMiddleware`` in your middleware in production.
        :ref:`SimulateWindowsAuthMiddleware`

.. glossary::

    wauth.I011
        Type: ``Info``, Deploy only

        Using the database to check LDAP user last sync time is slow.
        If you can, you should use cache system instead.
        :ref:`WAUTH_USE_CACHE`

.. glossary::

    wauth.W012
        Type: ``Warning``, Deploy only

        ``USE_SSL`` is not set to True. It is recommended to use only secure LDAP connection.
        :ref:`USE_SSL`

.. glossary::

    wauth.W013
        Type: ``Warning``, Deploy only

        You should use a stronger authentication method for you LDAP connection.
        Configure ``authentication`` to SASL or NTLM in you ``CONNECTION_OPTIONS``.
        :doc:`../howto/securing_ldap`

.. glossary::

    wauth.W014
        Type: ``Warning``, Deploy only

        You should use a dedicated bind account with the minimum permissions needed.
        Your bind account has logged in to website.
        :ref:`USERNAME`

.. glossary::

    wauth.W015
        Type: ``Warning``, Deploy only

        You should use a dedicated connection for you write operations.
        Using a different connection, and even another bind account, is considered best-practice.
        :ref:`READ_ONLY`

.. glossary::

    wauth.I020
        Type: ``Info``, Deploy only

        You should keep your site and project files on a separate disk from the OS.
        :ref:`READ_ONLY`
