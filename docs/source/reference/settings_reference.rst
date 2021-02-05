
Settings
--------

WAUTH_USE_SPN
~~~~~~~~~~~~~

| Type ``bool``; Default to ``False``; Not Required.
| Expect the REMOTE_USER header value to be in Windows SPN username scheme.

By default, IIS will present the authenticated user by it's `Down-Level Logon Name <https://docs.microsoft.com/en-us/windows/win32/secauthn/user-name-formats#down-level-logon-name>`_, for example "EXAMPLE\\username".
Setting this value to ``True`` will will expect the authenticated user to be presented by it's `User Principal Name <https://docs.microsoft.com/en-us/windows/win32/secauthn/user-name-formats#user-principal-name>`_, for example "username@example.local".

.. note::
    When using ``SPN`` the domain of the authenticated user will be detected by the **Domain's FQDN** instead of it's **NetBIOS Name**!

    This means that you will need to configure ``WAUTH_DOMAINS`` by created with the FQDN of their domain, and not their NetBIOS Name.
    This is also means all new LDAPUser domain values will be FQDNs and not NetBIOS Names

    If you are planning to migrate between using Down-Level to SPN, first of all **don't**.
    In case you still need to switch between them, you can either **manually replace** the LDAPUser's domain values from the old NetBIOS Names to the new FQDNs, or just **delete** all LDAPUsers and let them be created again when a user login again after change.

WAUTH_DOMAINS (Required)
~~~~~~~~~~~~~~~~~~~~~~~~

| Type ``dict``; Default to ``None``; Required.
| LDAP Settings for each domain.

Dictionary of domain NetBIOS Names and their settings for LDAP connection.
Domain LDAP Settings can be written as a dictionary with the settings in UPPERCASE and their values, or as an ``LDAPSettings`` object.

A default domain settings can be used as a fallback settings for requested domains that are missing from ``WAUTH_DOMAINS`` by using **"__default__"** as the domain name.
When using only the default domain settings, you may want to specify manually the ``WAUTH_PRELOAD_DOMAINS`` setting.

Each of the domain settings can be configured as a **function** that will be used as callback when accessing the setting and be called with the **domain as it first argument**.
This can be used with ``lambda`` functions for lazy setting values.

.. seealso:: More information about domain LDAP Settings can be found at :doc:`ldap_settings` reference.


WAUTH_RESYNC_DELTA
~~~~~~~~~~~~~~~~~~

| Type ``timedelta``, ``str``, ``int`` or ``None``; Default to ``timedelta(days=1)``; Not Required.
| Minimum time (seconds) until automatic re-sync user's fields and permissions against LDAP.

Configure when to **automatically synchronize** the user's fields and groups (and permissions) against Active Directory via LDAP.
On each request the user makes, if the user **haven't synchronized** in the time specified, the ``WindowsAuthBackend`` attempt to perform synchronization again on the user.
This is used to make sure the user permissions and properties match those in Active Directory.

The value is used as **number of seconds** in ``int``, ``str`` or any other object that can be casted to ``int``.
The value can also be a ``django.utils.timezone.timedelta`` object.

| In case you need to synchronize the user on every request, you can configure the setting to ``0``.
| To disable automatic synchronizations via LDAP, you can remove the ``UserSyncMiddleware`` or configure the setting to ``None`` or ``False``.

.. note::
    Synchronizing user via LDAP can delay the Request / Response processing by only few ms, but your experience may vary.
    You can debug your setup using :doc:`../howto/debug_toolbar`.

WAUTH_USE_CACHE
~~~~~~~~~~~~~~~

| Type ``boot``; Default to ``DEBUG``, otherwise ``False``; Not Required.
| Use cache backend instead of DB for determining user re-sync.

When using user automatic synchronization, the check whether user requires a re-sync is verified against the ``LDAPUser`` model and it requires an SQL Query.

To avoid this query and allow for better performance, this setting can allow you to use `Django's cache framework <https://docs.djangoproject.com/en/3.1/topics/cache/>`_ instead of the default model verification against the DB.
This will require you to setup your cache backend in setting ``CACHES``.

In production, it is advised to use the cache setting instead of the default model based verification.

WAUTH_REQUIRE_RESYNC
~~~~~~~~~~~~~~~~~~~~

| Type ``boot``; Default to ``False``; Not Required.
| Raise exception and return Error 500 when user failed to synced to domain.

When using user automatic synchronization, propagate any exception raised during synchronization.
This will result with the user receiving a **Error 500** when they fail to synchronize properly.

This is useful for security sake, when **requiring** users to have the most updated fields and permissions.
While developing in debug, it is usually useful to **receive information** about the synchronization exception.

In any case, the synchronization exception **will be logged** as error with the exception information included.
If you have setup logging and email reporting for server admins, you can also **receive the exception details by email**.

.. note::
    You can configure this per view with the ``ldap_sync_required`` decorator.
    See the reference at :doc:`decorators`

WAUTH_ERROR_RESPONSE
~~~~~~~~~~~~~~~~~~~~

| Type ``int`` or ``Callable``; Default to ``None``; Not Required.
| Configure custom HTTP Response for Errors while User automatic LDAP Synchronization.

When a user synchronization fails, you can define a **custom HTTP Response** to send to clients.

This can be configured as a ``int``, it is used as the **Response Code** for response with the default text ``Authorization Failed``.
This also can be a **function** that receive the ``request`` and ``exception`` as first and second arguments, and returning a Django ``HttpResponse`` object.

When configured to ``None`` the exception is propagated, and usually results in a **Error 500** for clients.

.. note::
    This setting is only relevant when ``WAUTH_REQUIRE_SYNC`` is set to ``True``, otherwise the **exception will be ignored**.


WAUTH_LOWERCASE_USERNAME
~~~~~~~~~~~~~~~~~~~~~~~~

| Type ``boot``; Default to ``True``; Not Required.
| Lowercase the username to mimic non-case sensitive LDAP backends like Active Directory.

Windows systems, like Active Directory are **non-case sensitive**.
While python, Django, and most Databases are **case sensitive**, you can lower case every username to **mimic** the non-case sensitive behavior of the Windows system.

WAUTH_IGNORE_SETTING_WARNINGS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

| Type ``boot``; Default to ``True``; Not Required.
| Skip verification of domain settings on server startup.

By default, on every startup of you Django project the settings are validated.

This setting can be used to ignore the warnings raised by detecting users with domains missing from settings in ``WAUTH_DOMAINS``, and **Unknown Settings** detected in domain LDAP Settings.

WAUTH_PRELOAD_DOMAINS
~~~~~~~~~~~~~~~~~~~~~

| Type ``tuple`` or ``bool``; Default to ``None``; Not Required.
| List of domains to preload and connect during Django project startup

LDAP Connections are **cached in process memory** to retain connections for multiple request / response cycles.
This setting lists the domains to preload, connection and bind during you **Django project startup**.
This way, the first request for a process will not have wait extra time for the LDAP connection to load and connect.

When the setting is configured to ``None`` or ``True``, all the domains configured in ``WAUTH_DOMAINS`` settings are **preloaded**.
In case you use only the **default domain settings** in the ``WAUTH_DOMAINS`` setting, it is advised to **manually** configure this setting to preload the relevant domains.

To enable LDAP Connection **lazy loading**, you can set this setting to ``False``.

.. note::
    When using ``runserver`` command, due to the server first **validating models** before loading the project, it may seam like **multiple connections** get initiated for the same domains.

    By setting this setting, it may cause **multiple LDAP connections** to be established and terminate quickly for each domain.

    You should **not be warned** by this behavior as this is behaves like a **quick connection test** to your LDAP server, and this is should only happened during **development phase**.
    In case you would like to **avoid this behavior** anyway, you can use the ``runserver --noreload`` parameter, or modifying the ``WAUTH_PRELOAD_DOMAINS`` setting to ``False`` when debugging.
