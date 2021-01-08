
Using Custom User Model Mappings
================================

Sometimes it is useful to modify the default Django User Model, to change field settings or to add extra fields.
When doing so, you may want to customize the LDAP synchronization to accommodate for the extra fields and changes.

For the sake of this tutorial, we will use the following custom User model as an example:

.. code-block:: python

    class CustomUser(AbstractBaseUser):
        telephone = models.CharField(max_length=32)
        country_code = models.PositiveSmallIntegerField()

        job_title = models.CharField(max_length=64)
        department = models.CharField(max_length=64)

        REQUIRED_FIELDS = ("telephone", "job_title", "department")

Usually the first thing to do is to change the ``USER_FIELD_MAP`` in the LDAP Setting for all domains.

You can configure it for each domain, for example:

.. code-block:: python

    WAUTH_DOMAINS = {
        "EXAMPLE": {
            "SERVER": "example.local",
            "SEARCH_BASE": "DC=example,DC=local",
            "USERNAME": EXAMPLE\\bind_account",
            "PASSWORD": "<super secret>",
            "USER_FILED_MAP": {
                "username": "sAMAccountName",
                "first_name": "givenName",
                "last_name": "sn",
                "email": "mail",

                "telephone": "telephoneNumber",
                "country_code": "countryCode",
                "job_title": "title",
                "department": "department",
            }
        },
    }

Or create a custom LDAP Settings with your defaults:

.. code-block:: python

    @dataclass()
    class MyLDAPSettings(LDAPSettings):
        USER_FIELD_MAP = {
            "username": "sAMAccountName",
            "first_name": "givenName",
            "last_name": "sn",
            "email": "mail",

            "telephone": "telephoneNumber",
            "country_code": "countryCode",
            "job_title": "title",
            "department": "department",
        }

    WAUTH_DOMAINS = {
        "EXAMPLE": MyLDAPSettings(
            SERVER="example.local",
            SEARCH_BASE="DC=example,DC=local",
            USERNAME="EXAMPLE\\bind_account",
            PASSWORD="<super secret>",
        ),
    }

.. seealso::
    Reference for ``USER_FIELD_MAP`` LDAP Setting at :doc:`../reference/ldap_settings`


.. TODO custom user model mapping