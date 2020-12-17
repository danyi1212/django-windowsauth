
Models
======

LDAPUser
--------

Used to same user's domain information and perform domain related actions.

Fields:
    * **user** - One to one relation for user model using ``get_user_model`` function.
    * **domain** - User's domain name (usually) as NetBIOS Name.

Methods:
    * **get_ldap_manager()** - Get ``LDAPManager`` for user's domain.
    * **get_ldap_attr(attribute, as_list)** - Get LDAP attribute of the related LDAP user.
    * **get_ldap_user()** - Get related LDAP user as ldap3 ``Entry`` object.
    * **get_ldap_groups()** - get LDAP Reader for all groups the user is a member of.
    * **sync()** - Synchronize Django user to related LDAP User.

The ``LDAPUser`` for a Django User can be accessed via ``user.ldap``.
For example, you can trigger sync with ``request.user.ldap.sync()``, or display the user's Windows Logon Name with ``request.user.ldap``.

.. note::
    The ``LDAPUser`` is represented by the **Down-level Logon Name** or **SPN** determined by the ``WAUTH_USE_SPN`` setting.
    More on that in the :doc:`./settings_reference`.