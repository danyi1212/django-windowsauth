
Middleware
==========

UserSyncMiddleware
------------------

Sync users against LDAP when is needed.


| Sync interval configured by the ``WAUTH_RESYNC_DELTA`` setting.
| Last sync validation process can be configured by the ``WAUTH_USE_CACHE`` setting.

This middleware must be positioned after the ``AuthenticationMiddleware`` and ``RemoteUserMiddleware`` middleware.


.. code-block:: python

    MIDDLEWARE = [
        # ...
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.RemoteUserMiddleware',
        'windows_auth.middleware.UserSyncMiddleware',
        # ...
    ]


SimulateWindowsAuthMiddleware
-----------------------------

Simulate a remote user authenticated through Windows Authentication. This is useful for developing and testing without
actually deploying the Django project to IIS.

When no actual windows authentication information passed from the IIS, this middleware will inject the request
with the ``REMOTE_USER`` header, just like if ``WAUTH_SIMULATE_USER`` had logged in via Windows Authentication.

This middleware is bypassed when ``DEBUG`` setting is not ``True``.

.. warning::
    | This is a security risk, and allows the impersonation of any user.
    | It is intended for development / testing only and **should not be used on production**.

You must configure the setting ``WAUTH_SIMULATE_USER`` to specify the user to impersonate.

.. code-block:: python

    MIDDLEWARE = [
        'windows_auth.middleware.SimulateWindowsAuthMiddleware',
        # ...
    ]
    WAUTH_SIMULATE_USER = "EXAMPLE\\Administrator"

It should be positioned as high as possible in the middleware setting to allow for