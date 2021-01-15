from typing import Callable, Union, Optional, Iterable

from django.conf import settings
from django.http import HttpResponse

from django.utils import timezone

from windows_auth import logger

if not hasattr(settings, "WAUTH_DOMAINS"):
    logger.warn("The required setting WAUTH_DOMAINS is missing.")

# Settings for each domain
WAUTH_DOMAINS: dict = getattr(settings, "WAUTH_DOMAINS", {})

# Expect REMOTE_USER value to be in SPN scheme
WAUTH_USE_SPN: bool = getattr(settings, "WAUTH_USE_SPN", False)
# Minimum time until automatic re-sync
WAUTH_RESYNC_DELTA: Optional[Union[str, int, timezone.timedelta]] = getattr(settings, "WAUTH_RESYNC_DELTA",
                                                                            timezone.timedelta(minutes=10))
# Use cache instead of model for determining re-sync
WAUTH_USE_CACHE: bool = getattr(settings, "WAUTH_USE_CACHE", False)
# Raise exception and return Error 500 when user failed to synced to domain
WAUTH_REQUIRE_RESYNC: bool = getattr(settings, "WAUTH_REQUIRE_RESYNC", settings.DEBUG or False)
# Choose custom HTTP Response to send when LDAP Sync fails
WAUTH_ERROR_RESPONSE: Optional[Union[int, HttpResponse, Callable]] = getattr(settings, "WAUTH_ERROR_RESPONSE", None)
# Lowercase the username from the REMOTE_USER. Used for correct non-case sensitive LDAP backends.
WAUTH_LOWERCASE_USERNAME: bool = getattr(settings, "WAUTH_LOWERCASE_USERNAME", True)
# Skip verification of domain settings on server startup
WAUTH_IGNORE_SETTING_WARNINGS: bool = getattr(settings, "WAUTH_IGNORE_SETTING_WARNINGS", False)
# List of domains to preload and connect during process startup
WAUTH_PRELOAD_DOMAINS: Optional[Iterable[str]] = getattr(settings, "WAUTH_PRELOAD_DOMAINS", None)
