
LDAP Settings
=============

LDAP Settings are the settings used to configure **LDAP connection** to domains.
They are configured inside the ``WAUTH_DOMAINS`` setting of your Django project settings file, as the **value** for each domain key.

Configuring
-----------

LDAP Settings can be represented as a regular **Python Dictionary**, like this:

.. code-block:: python

    WAUTH_DOMAINS = {
        "EXAMPLE": {
            "SERVER": "example.local",
            "SEARCH_BASE": "DC=example,DC=local",
            "USERNAME": "EXAMPLE\\bind_account",
            "PASSWORD": "*********",
        }
    }

Or as an LDAPSettings object, like this:

.. code-block:: python

    WAUTH_DOMAINS = {
        "EXAMPLE": LDAPSettings(
            SERVER="example.local",
            SEARCH_BASE="DC=example,DC=local",
            USERNAME="EXAMPLE\\bind_account",
            PASSWORD="*********",
        ),
    }


When using a **Python Dictionary**, each setting can be configured to a **callback function** that will be called with the specified domain as first and only argument.
For example:

.. code-block:: python

    WAUTH_DOMAINS = {
        "EXAMPLE": {
            "USERNAME": lambda domain: f"{domain}\\bind_account",
        }
    }

Using defaults
--------------
Sometimes when using multiple domains it is easier to configure settings **globally** or to **specify defaults** for unanticipated domains.

When configuring LDAP Settings as a **Python Dictionary**, this can be done by using the ``"__default__"`` key in ``WAUTH_DOMAINS`` settings.
Every setting configured in the ``"__default__"``, and are **not configured explicitly** for the domain, in will propagate.
For example:

.. code-block:: python
    :emphasize-lines: 3, 10

    WAUTH_DOMAINS = {
        "__default__": {
            "USE_SSL": True,
        },
        "EXAMPLE1": {
            "SERVER": "example.local",
            "SEARCH_BASE": "DC=example,DC=local",
            "USERNAME": "EXAMPLE\\bind_account",
            "PASSWORD": "*********",
            "USE_SSL": False,
        },
        "EXAMPLE2": {
            "SERVER": "example.local",
            "SEARCH_BASE": "DC=example,DC=local",
            "USERNAME": "EXAMPLE\\bind_account",
            "PASSWORD": "*********",
        }
    }

In this case, ``EXAMPLE1`` will have ``USE_SSL = False`` and ``EXAMPLE2`` will have ``USE_SSL = True``.

When using ``LDAPSettings`` objects, this can be done by inheriting and creating a custom ``LDAPSettings`` class.
For example:

.. code-block:: python
    :emphasize-lines: 7

    @dataclass()
    class MyLDAPSettings(LDAPSettings):
        USE_SSL: bool = False


    WAUTH_DOMAINS = {
        "EXAMPLE": MyLDAPSettings(
            SERVER="example.local",
            SEARCH_BASE="DC=example,DC=local",
            USERNAME="EXAMPLE\\bind_account",
            PASSWORD="*********",
        ),
    }

Extending LDAP Settings
--------------------

Sometimes it is useful to have some **extra LDAP Settings** for use with the LDAP Manager.

It is possible to create a custom ``LDAPSettings`` class and use it to configure the LDAP Settings for domains.
Those extra setting will be available in the **settings attribute** of ``LDAPManager`` objects, and can be used **throughout your code**.
Those settings should not affect the existing settings used by ``django-windowsauth`` for User synchronization or any other uses.

Custom LDAP Settings objects can be created by inheriting from the ``LDAPSettings`` dataclass, like so:

.. code-block:: python
    :emphasize-lines: 7

    @dataclass()
    class MyLDAPSettings(LDAPSettings):
        EXTRA_SETTING: str = "Hello, world!"


    WAUTH_DOMAINS = {
        "EXAMPLE": MyLDAPSettings(
            SERVER="example.local",
            SEARCH_BASE="DC=example,DC=local",
            USERNAME="EXAMPLE\\bind_account",
            PASSWORD="*********",
        ),
    }

Then the setting could be accessed from ``LDAPManager`` object:

.. code-block:: python

    >>> from windows_auth.ldap import get_ldap_manager
    >>> manager = get_ldap_manager("EXAMPLE")
    >>> manager.settings.EXTRA_SETTING
    "Hello, world!"


Base Settings
-------------

SERVER
~~~~~~

| Type ``bool``; **Required**.
| FQDN, IP, or URL of the LDAP Server.

The Fully Qualified Domain Name, IP Address or complete URL in the scheme ``scheme://hostname:hostport`` of the LDAP Server.
This setting will be used as ``host`` property for ldap3's `Server <https://ldap3.readthedocs.io/en/latest/server.html>`_ object.

When using Active Directory, this address should direct to a DC Server (Domain Controller) for the domain.
By default, the FQDN of the domain itself will be resolved into your current configured DC Server.
That way, in case you have multiple DC servers in your domain, you will be dynamically changing the server you are accessing.

.. seealso:: From the Microsoft Docs https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/plan/domain-controller-location

USERNAME
~~~~~~~~

| Type ``str``; **Required**.
| The account to be used when binding to the LDAP Server.

The username in one of the `Credentials Manager API's formats (Down-Level or SPN) <https://docs.microsoft.com/en-us/windows/win32/secauthn/user-name-formats#user-principal-name>`_ of a user with the permissions needed for your application.
By default, **read-only permissions** for the user accounts that are able to authenticate via IIS Windows Authentication to **your website** is needed.

If you are planing to use **NTLM authentication** to your LDAP Server, the username must be in the Down-Level Logon Name format (DOMAIN\\username).

In production, it is advised to use a **dedicated Service Account** to authorize your application in your Active Directory domain.

PASSWORD
~~~~~~~~

| Type ``str``; **Required**.
| Password of the user to be used when binding to the LDAP Server.

The password for the user used to authenticate to the LDAP Server.

.. warning::
    It is highly advised not to store sensitive secrets like password in your code.
    You should use a safe and secure place to store the password. See the tutorial :doc:`manage_secrets`


SEARCH_BASE
~~~~~~~~~~~~

| Type ``str``; **Required**.
| The DN of the container used as starting point for LDAP searches.

When querying LDAP Directories, it is required to specify the **root container** to start the search from.
Then, depending on the search scope, the objects are searched **directly or indirectly** in respect to the search base container.

For searches throughout all the domain's containers, the search base DN is usually in the format ``DC=<domain name>,DC=<parent domain>``.

.. seealso:: Microsoft docs about search bases https://docs.microsoft.com/en-us/windows/win32/ad/binding-to-a-search-start-point


USE_SSL
~~~~~~~

| Type ``bool``; Default to ``True``; Not Required.
| Connect to LDAP over secure port, usually 636.

This setting is used as the ``use_ssl`` parameter for the ldap3 ``Server`` object.

.. seealso:: ldap3 Server object docs https://ldap3.readthedocs.io/en/latest/server.html

READ_ONLY
~~~~~~~~~

| Type ``bool``; Default to ``True``; Not Required.
| Prevent modify, delete, add and modifyDn (move) operations.

Connect to the LDAP Server with a read only protection.
This can farther minimize risks and vulnerabilities from unwanted operations against the LDAP Server.

This setting is used as the ``read_only`` parameter for the ldap3 ``Connection`` object.

.. warning::
    This is not guaranteed to be a risk / vulnerabilities free connection, **make sure to minimize the bind account's permissions**

SERVER_OPTIONS
~~~~~~~~~~~~~~

| Type ``dict``; Default to ``{}``; Not Required.
| Extra parameters for the ldap3 ``Server`` object.

A dictionary of extra keyword arguments to pass when creating the ldap3 ``Server`` object.

.. seealso:: For more information, see ldap3 docs https://ldap3.readthedocs.io/en/latest/server.html

CONNECTION_OPTIONS
~~~~~~~~~~~~~~

| Type ``dict``; Default to ``{}``; Not Required.
| Extra parameters for the ldap3 ``Connection`` object.

A dictionary of extra keyword arguments to pass when creating the ldap3 ``Connection`` object.

.. seealso:: For more information, see ldap3 docs https://ldap3.readthedocs.io/en/latest/connection.html

PRELOAD_DEFINITIONS
~~~~~~~~~~~~~~~~~~~

| Type ``tuple``; Default is shown below; Not Required.
| Preload LDAP schema for defining LDAP objects in Python.

A list of LDAP Object definitions to **preload** while connecting to the LDAP Server.
This **caches** ldap3 ``ObjectDef`` objects on the ``LDAPManager`` object for each defined object class.
The object definitions are later get used for **parsing the objects** received from querying the LDAP Directory.
Preloading the object definitions can **minimize the extra delay** for first query for an object.

The definitions can be listed as a **simple string** referring to an LDAP object class, or a **2 valued tuple** with the LDAP object class string on the first value, and a list of **extra attributes** on the second value.
For example:

.. code-block:: python

    {
        "PRELOAD_DEFINITIONS": (
            ("user", ["sAMAccountName"]),
            "group"
        ),
    }

The configuration above is the actual default configuration for this setting.

USER_FIELD_MAP
~~~~~~~~~~~~~~

| Type ``dict``; Default is shown below; Not Required.
| Translate User Model fields to LDAP User object attributes.

Provide a mapping for your **Django User Model fields** to the **LDAP User object attributes**.
Those mappings are used when synchronizing Django Users to their related LDAP Users.

In case you using a **Custom User Model** in your Django project, you also will be able to map them to LDAP Attributes.
This is mentioned in the tutorial :doc:`../howto/custom_user_fields`.

.. note:: Make sure to specify the needed attributes when **preloading definitions** for non-default attributes.

.. code-block:: python

    {
        "USER_FIELD_MAP": {
            "username": "sAMAccountName",
            "first_name": "givenName",
            "last_name": "sn",
            "email": "mail",
        }
    }

The configuration above is the actual default configuration for this setting.

USER_QUERY_FIELD
~~~~~~~~~~~~~~~~

| Type ``str``; Default to ``username``; Not Required.
| The User Model field used for searching the related LDAP User object.

When synchronizing users to LDAP, they are first need to be searched.
This setting can allow you to specify the **Django User Model field** that will be compared to the related **LDAP Attribute** using the ``USER_FIELD_MAP`` setting when searching for the related user.

This setting may be useful when using a **Custom User Model** in your Django project.
This is mentioned in the tutorial :doc:`../howto/custom_user_fields`.

.. note::
    Make sure to use a unique field, that is unique at the **LDAP side** too.
    If multiple objects are found, the synchronization will fail.

.. TODO test that ^

GROUP_ATTRS
~~~~~~~~~~~

| Type ``str`` or ``tuple``; Default to ``cn``; Not Required.
| The LDAP group attributes to search when matching to Django groups.

When synchronizing users against LDAP, you can **replicate group memberships**.
When used, you may want to specify what **LDAP attributes** are used when comparing the **Django Group's names** to LDAP Groups.

This setting can be a **single string** for comparing a single attribute, or a **tuple** for comparing multiple attributes.
When comparing multiple attributes, if one of them matches the Django Group's name, the user is added to that group.

.. warning::
    The comparing is done on the **Python side** by the ldap3 library.
    Using many attributes to search groups may result in **longer synchronization times**.

SUPERUSER_GROUPS
~~~~~~~~~~~~~~~~

| Type ``tuple`` or ``str``; Default to ``Domain Admins``; Not Required.
| LDAP Groups to check membership for setting Django User's "is_superuser" flag.

When synchronizing users against LDAP, you can specify a **list of LDAP Groups** to match for setting the Django User's ``is_superuser`` flag.
If the user is member in **one** of the listed LDAP groups, the ``is_superuser`` flag will be set to ``True``, otherwise it is set to ``False``.

| Configuring this setting to ``None`` will set the ``is_superuser`` flag for all synced users to ``False``.
| Configuring this setting to a **string** is equal to a **single length tuple**.

The group membership is checked by comparing the **groups listed in this setting** to the **LDAP Group Attributes** listed in ``GROUP_ATTRS`` setting.

STAFF_GROUPS
~~~~~~~~~~~~~~~~

| Type ``tuple`` or ``str``; Default to ``Administrators``; Not Required.
| LDAP Groups to check membership for setting Django User's "is_staff" flag.

When synchronizing users against LDAP, you can specify a **list of LDAP Groups** to match for setting the Django User's ``is_staff`` flag.
If the user is member in **one** of the listed LDAP groups, the ``is_staff`` flag will be set to ``True``, otherwise it is set to ``False``.

| Configuring this setting to ``None`` will set the ``is_staff`` flag for all synced users to ``False``.
| Configuring this setting to a **string** is equal to a **single length tuple**.

The group membership is checked by comparing the **groups listed in this setting** to the **LDAP Group Attributes** listed in ``GROUP_ATTRS`` setting.

ACTIVE_GROUPS
~~~~~~~~~~~~~~~~

| Type ``tuple`` or ``str``; Default to ``None``; Not Required.
| LDAP Groups to check membership for setting Django User's "is_active" flag.

When synchronizing users against LDAP, you can specify a **list of LDAP Groups** to match for setting the Django User's ``is_active`` flag.
If the user is member in **one** of the listed LDAP groups, the ``is_active`` flag will be set to ``True``, otherwise it is set to ``False``.

| Configuring this setting to ``None`` will set the ``is_active`` flag for all synced users to ``True``.
| Configuring this setting to a **string** is equal to a **single length tuple**.

The group membership is checked by comparing the **groups listed in this setting** to the **LDAP Group Attributes** listed in ``GROUP_ATTRS`` setting.


GROUP_MAP
~~~~~~~~~

| Type ``dict``; Default is ``{}``; Not Required.
| Map one or more LDAP Groups membership to Django Group membership.

When synchronizing users against LDAP, you can specify a mapping of LDAP Groups to Django Groups.
If the user is member in **one** of the listed LDAP groups, it will be added to the respective Django Group.

The setting is configured as a dictionary where the **keys are Django Groups names** and the value is **a string or a list of LDAP Groups**.
The LDAP Groups are compared using the attributes listed in the ``GROUP_ATTRS`` setting.
