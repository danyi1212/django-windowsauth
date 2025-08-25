from dataclasses import dataclass, field, fields, Field
from typing import Callable, Union, Optional, Iterable, Dict, TYPE_CHECKING, Set

from django.conf import settings
from django.core.signals import setting_changed
from django.dispatch import receiver
from django.http import HttpResponse

from django.utils import timezone

if TYPE_CHECKING:
    from windows_auth.settings import LDAPSettings


@dataclass()
class WAUTHSettings:
    WAUTH_DOMAINS: Dict[str, Union["LDAPSettings"]] = field(default_factory=lambda: {})
    WAUTH_USE_SPN: bool = False
    WAUTH_RESYNC_DELTA: Optional[Union[str, int, timezone.timedelta]] = timezone.timedelta(days=1)
    WAUTH_USE_CACHE: bool = False
    # Raise exception and return Error 500 when user failed to synced to domain
    WAUTH_REQUIRE_RESYNC: bool = field(default_factory=lambda: settings.DEBUG)
    WAUTH_ERROR_RESPONSE: Optional[Union[int, HttpResponse, Callable]] = None
    # Lowercase the username from the REMOTE_USER. Used for connecting case-insensitive LDAP backends.
    WAUTH_LOWERCASE_USERNAME: bool = True
    # Skip verification of domain settings on server startup
    WAUTH_IGNORE_SETTING_WARNINGS: bool = False
    # List of domains to preload and connect during process startup
    WAUTH_PRELOAD_DOMAINS: Optional[Iterable[str]] = None
    # User to impersonate when using SimulateWindowsAuthMiddleware
    WAUTH_SIMULATE_USER: str = ""

    @classmethod
    def build_settings(cls):
        return cls(**{
            f.name: getattr(settings, f.name)
            for f in fields(cls)
            if hasattr(settings, f.name)
        })

    def update_setting(self, name: str, value) -> None:
        self.__setattr__(name, value)


if settings.configured:
    wauth_settings = WAUTHSettings.build_settings()


@receiver(setting_changed)
def _update_setting(sender=None, setting=None, value=None, enter=None, **kwargs):
    if not wauth_settings:
        return

    if setting in map(lambda f: f.name, fields(WAUTHSettings)):
        wauth_settings.update_setting(setting, value)

    # update bound settings
    if setting == "DEBUG" and not hasattr(settings, "WAUTH_REQUIRE_RESYNC"):
        wauth_settings.update_setting("WAUTH_REQUIRE_RESYNC", value)
