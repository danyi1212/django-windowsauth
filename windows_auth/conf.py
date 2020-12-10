from typing import Dict, Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django.utils import timezone

from windows_auth import logger


# Expect REMOTE_USER value to be in SPN scheme
WAUTH_USE_SPN = getattr(settings, "WAUTH_USE_SPN", False)
# Minimum time until automatic re-sync
WAUTH_RESYNC_DELTA = getattr(settings, "WAUTH_RESYNC_DELTA", timezone.timedelta(minutes=10))
# Use cache instead of model for determining re-sync
WAUTH_USE_CACHE = getattr(settings, "WAUTH_USE_CACHE", False)
# Raise exception and return Error 500 when user failed to synced to domain
WAUTH_REQUIRE_RESYNC = getattr(settings, "WAUTH_REQUIRE_RESYNC", settings.DEBUG or False)
# Lowercase the username from the REMOTE_USER. Used for correct non-case sensitive LDAP backends.
WAUTH_LOWERCASE_USERNAME = getattr(settings, "WAUTH_LOWERCASE_USERNAME", True)
# Skip verification of domain settings on server startup
WAUTH_IGNORE_SETTING_WARNINGS = getattr(settings, "WAUTH_IGNORE_SETTING_WARNINGS", False)

# Required domain settings
_WAUTH_LDAP_REQUIRED_SETTINGS = (
    "SERVER",
    "USERNAME",
    "PASSWORD",
    "SEARCH_SCOPE"
)


class LDAPSettings:
    # connection settings
    SERVER = None
    USERNAME = None
    PASSWORD = None
    USE_SSL = True
    SERVER_OPTIONS = {}
    CONNECTION_OPTIONS = {}  # TODO document ntlm auth

    # user sync settings
    SEARCH_SCOPE = ""
    FIELD_MAP = {
        "username": "sAMAccountName",
        "first_name": "givenName",
        "last_name": "sn",
        "email": "mail",
    }
    QUERY_FIELD = "username"

    # groups / permissions sync settings
    GROUP_ATTRS = "cn"
    SUPERUSER_GROUPS = "Domain Admins"
    STAFF_GROUPS = "Administrators"
    ACTIVE_GROUPS = None
    GROUP_MAP = {}

    def __init__(self, domain: str):
        resultant_settings: Dict[str, Any] = {}

        # populate default domain settings
        if hasattr(settings, "WAUTH_DOMAINS"):
            resultant_settings.update(settings.WAUTH_DOMAINS.get("default", {}))

        # populate domain specific settings
        try:
            resultant_settings.update(settings.WAUTH_DOMAINS[domain])
        except KeyError:
            raise ImproperlyConfigured(f"Domain {domain} settings could not be found in WAUTH_DOMAINS setting.")

        # validate domain settings
        for setting in _WAUTH_LDAP_REQUIRED_SETTINGS:
            if setting not in resultant_settings:
                raise ImproperlyConfigured(f"Domain {domain} settings is missing a required setting: {setting}")

        for setting, value in resultant_settings.items():
            if hasattr(self, setting):
                # TODO document
                # check for callable values for dynamic configurations
                if callable(value):
                    value = value(domain)

                # perform clean callable with value
                clean_callback = f"clean_{setting.lower()}"
                if hasattr(self, clean_callback) and callable(getattr(self, clean_callback)):
                    value = getattr(self, clean_callback)(value)

                # set setting value
                setattr(self, setting, value)
            else:
                logger.warn(f"Unknown setting {setting} in WAUTH_DOMAINS {domain}")


if not hasattr(settings, "WAUTH_DOMAINS"):
    raise ImproperlyConfigured("The required setting WAUTH_DOMAINS is missing.")

