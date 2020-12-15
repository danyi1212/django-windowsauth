from dataclasses import dataclass, field, asdict, MISSING, fields
from typing import Dict, Any, Optional, Iterable, Union, Tuple

from django.core.exceptions import ImproperlyConfigured

from windows_auth import logger

# domain name to use as a fallback setting for domain missing from WAUTH_DOMAINS
DEFAULT_DOMAIN_SETTING = "__default__"


@dataclass()
class LDAPSettings:
    # connection settings
    SERVER: str
    USERNAME: str
    PASSWORD: str
    SEARCH_SCOPE: str

    USE_SSL: bool = True
    SERVER_OPTIONS: Dict[str, Any] = field(default_factory=dict)
    CONNECTION_OPTIONS: Dict[str, Any] = field(default_factory=dict)  # TODO document ntlm auth
    PRELOAD_DEFINITIONS: Optional[Iterable[Union[str, Tuple[str, Iterable[str]]]]] = (
        ("user", ("sAMAccountName",)),
        "group"
    )

    # user sync settings
    FIELD_MAP: Dict[str, str] = field(default_factory=lambda: {
        "username": "sAMAccountName",
        "first_name": "givenName",
        "last_name": "sn",
        "email": "mail",
    })
    QUERY_FIELD: str = "username"

    # groups / permissions sync settings
    GROUP_ATTRS: Union[str, Iterable[str]] = "cn"
    SUPERUSER_GROUPS: Optional[Union[str, Iterable[str]]] = "Domain Admins"
    STAFF_GROUPS: Optional[Union[str, Iterable[str]]] = "Administrators"
    ACTIVE_GROUPS: Optional[Union[str, Iterable[str]]] = None
    GROUP_MAP: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def for_domain(cls, domain: str):
        from django.conf import settings as django_settings
        from windows_auth.conf import WAUTH_IGNORE_SETTING_WARNINGS

        if not hasattr(django_settings, "WAUTH_DOMAINS"):
            raise ImproperlyConfigured("The required setting WAUTH_DOMAINS is missing.")

        if domain not in django_settings.WAUTH_DOMAINS and DEFAULT_DOMAIN_SETTING not in django_settings.WAUTH_DOMAINS:
            raise ImproperlyConfigured(f"Domain {domain} settings could not be found in WAUTH_DOMAINS setting.")

        domain_settings = django_settings.WAUTH_DOMAINS.get(domain, {})
        # when setting is an LDAPSetting object
        if isinstance(domain_settings, LDAPSettings):
            return domain_settings

        default_settings = django_settings.WAUTH_DOMAINS.get(DEFAULT_DOMAIN_SETTING, {})
        # when domain setting
        if isinstance(default_settings, LDAPSettings):
            return asdict(default_settings)

        # merge default and domain settings
        merged_settings: Dict[str, Any] = {**default_settings, **domain_settings}

        # validate domain settings
        for setting in filter(lambda f: f.default == MISSING and f.default_factory == MISSING, fields(cls)):
            if setting.name not in merged_settings:
                raise ImproperlyConfigured(f"Domain {domain} settings is missing a required setting: {setting.name}")

        cls_fields = set(f.name for f in fields(cls))
        for setting, value in merged_settings.items():
            # if field exists in this LDAP Settings
            if setting in cls_fields:
                if callable(value):
                    value = value(domain)

                # perform clean callable with value
                clean_callback = f"clean_{setting.lower()}"
                if hasattr(cls, clean_callback) and callable(getattr(cls, clean_callback)):
                    value = getattr(cls, clean_callback)(value)

                merged_settings[setting] = value
            elif WAUTH_IGNORE_SETTING_WARNINGS:
                logger.warn(f"Unknown setting {setting} in WAUTH_DOMAINS {domain}")

        return cls(**merged_settings)