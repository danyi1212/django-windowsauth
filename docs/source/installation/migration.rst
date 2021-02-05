
Migration
=========

From existing project
---------------------

This is a very quick how-to for integrating ``django-windowsauth`` into existing Django projects.

First of all you will need to check your Django User's username field.
In case it already matches their Active Directory logon name, you are good to go.

If that is not the case, you will probably need to change that.
The process can look like:

1. Export the Django user table from your DB, and load it to excel.
2. Export the Active Directory Users to excel.
3. Merge tables via excel.
4. Import new user table into you your Django users table in your DB.

Next, you will need to manually create a ``LDAPUser`` model entry for each relevant user.
This can be done via Django's shell::

$ py manage.py shell

>>> from django.contrib.auth.models import User
>>> from windows_auth.models import LDAPUser
>>> users = User.objects.filter().all()
>>> LDAPUser.objects.bulk_create(LDAPUser(domain="EXAMPLE", user=user) for user in users)

You may want to **modify the user queryset** to create LDAP Relations only for specific users.
In case you are using a **different Django User Model**, you will need to use it instead of the Django ``User`` or use ``get_user_model()`` method.

At this point, when a user first visit your site after migration, it **will be synchronized** against LDAP.
In case you would still want to **also** migrate all users now, you can do this via Django's shell like so::

>>> from windows_auth.models import LDAPUser
>>> for user in LDAPUsers.objects.all():
>>>     user.sync()

To 1.4.0
--------

- (optional) Remove duplicated groups between ``SUPERUSER_GROUPS``, ``STAFF_GROUPS`` and ``ACTIVE_GROUPS`` ldap settings, or set ``PROPAGATE_GROUPS`` to ``False``.

To 1.3.0
--------

No required changes for migration is needed.


To 1.2.0
--------

- Add the ``UserSyncMiddleware`` to ``MIDDLEWARE`` setting like so:

.. code-block:: python

    MIDDLEWARE = [
        ...
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.RemoteUserMiddleware',
        'windows_auth.middleware.UserSyncMiddleware',
        ...
    ]


