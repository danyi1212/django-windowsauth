from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django.utils import timezone

if not hasattr(settings, "WAUTH_DOMAINS"):
    raise ImproperlyConfigured("The required setting WAUTH_DOMAINS is missing.")

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
# List of domains to preload and connect during process startup
WAUTH_PRELOAD_DOMAINS = getattr(settings, "WAUTH_PRELOAD_DOMAINS", None)
