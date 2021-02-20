
Change Log
=============

1.4.0
-----

Release date: Feb. 20, 2021

- **ADDED**: LDAPUserManager for manually creating users from LDAP.
- **ADDED**: ``createtask`` management command for creating Task Scheduler jobs.
- **ADDED**: ``ldap_user_sync`` signal.
- **IMPROVED**: LDAP Settings for Group Membership check propagate to one another.
- **MODIFIED**: Increased the default ``WAUTH_RESYNC_DELTA`` to every 1 day.

1.3.2
-----

Release date: Jan 26, 2021

- **FIXED**: ``ProgrammingError`` Exception before first migration
- **FIXED**: Packaging configuration missing templates

1.3.1
-----

Release date: Jan 15, 2021

- **MODIFIED**: Remove requirement for ``WAUTH_DOMAIN`` setting
- **FIXED**: ``OperationalError`` Exception before first migration
- **FIXED**: Incorrect packaging configuration

1.3.0
-----

Release date: Jan 10, 2021

- **ADDED**: LDAP Metrics collection to Database
- **ADDED**: LDAP Panel for ``django-debug-toolbar``
- **ADDED**: LDAP Setting ``COLLECT_METRICS``
- **ADDED**: Auto-close all LDAP connection on before process exit
- **ADDED**: View decorators ``domain_required`` and ``ldap_sync_required``
- **ADDED**: ``--https`` parameter for ``createwebconfig`` for HTTPS Redirection

1.2.0
-----

Release date: Dec 19, 2020

- **ADDED**: Setting ``WAUTH_ERROR_RESPONSE`` for custom sync error responses
- **ADDED**: Moved automatic sync login from Authentication Backend ``WindowsAuthBackend`` to a new Middleware ``UserSyncMiddleware``.

1.1
---

Release date: Dec 17, 2020

- First published version