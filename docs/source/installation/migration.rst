
Migration
=========

To 1.2.0
-----

- Add the ``UserSyncMiddleware`` to ``MIDDLEWARE`` setting like so:

.. code-block:: python

    MIDDLEWARE = [
        ...
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.RemoteUserMiddleware',
        'windows_auth.middleware.UserSyncMiddleware',
        ...
    ]


