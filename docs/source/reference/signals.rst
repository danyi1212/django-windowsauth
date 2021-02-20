
Signals
=======

ldap_user_sync
--------------

Whenever a user is synced against LDAP, pre-saving.

Arguments:
    * **sender** The LDAPUser instance that is being synced.
    * **ldap_user** The ``ldap3`` Entry instance received from LDAP server of the user being synced
    * **group_reader** Reader cursor for all the user's groups, already queried.

Example:

.. code-block:: python

    from django.dispatch import receiver
    from ldap3 import Entry, Reader

    from windows_auth.models import LDAPUser
    from windows_auth.signals import ldap_user_sync


    @receiver(ldap_user_sync)
    def on_ldap_sync(sender: LDAPUser, ldap_user: Entry = None, group_reader: Reader = None):
        # do something...
        pass

.. warning::
    Any unhandled exception raised during the signal will terminate the sync process.
