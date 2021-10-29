from dataclasses import dataclass, field, asdict, MISSING, fields
from typing import Dict, Any, Optional, Iterable, Union, Tuple, List

from django.core.exceptions import ImproperlyConfigured

# domain name to use as a fallback setting for domain missing from WAUTH_DOMAINS
DEFAULT_DOMAIN_SETTING = "__default__"


def _get_group_list(value) -> List[str]:
    if value is None:
        return []
    elif isinstance(value, str):
        return [value]
    else:
        return value


@dataclass(frozen=True)
class LDAPSettings:
    # connection settings
    SERVER: str
    USERNAME: str
    PASSWORD: str = field(repr=False)
    SEARCH_BASE: str

    USE_SSL: bool = True
    READ_ONLY: bool = True
    COLLECT_METRICS: bool = False
    SERVER_OPTIONS: Dict[str, Any] = field(default_factory=dict)
    CONNECTION_OPTIONS: Dict[str, Any] = field(default_factory=dict)
    PRELOAD_DEFINITIONS: Optional[Iterable[Union[str, Tuple[str, Iterable[str]]]]] = (
        ("user", ("sAMAccountName",)),
        "group"
    )

    # user sync settings
    USER_FIELD_MAP: Dict[str, str] = field(default_factory=lambda: {
        "username": "sAMAccountName",
        "first_name": "givenName",
        "last_name": "sn",
        "email": "mail",
    })
    USER_QUERY_FIELD: str = "username"
    USER_QUERY_FILTER: Dict[str, str] = field(default_factory=lambda: {
        "objectCategory": "person",
    })

    # groups / permissions sync settings
    GROUP_ATTRS: Union[str, Iterable[str]] = "cn"
    SUPERUSER_GROUPS: Optional[Union[str, Iterable[str]]] = "Domain Admins"
    STAFF_GROUPS: Optional[Union[str, Iterable[str]]] = "Administrators"
    ACTIVE_GROUPS: Optional[Union[str, Iterable[str]]] = None
    PROPAGATE_GROUPS: bool = True
    GROUP_MAP: Dict[str, Union[str, Iterable[str]]] = field(default_factory=dict)
    FLAG_MAP: Dict[str, Union[str, Iterable[str]]] = field(default_factory=dict)

    @classmethod
    def for_domain(cls, domain: str):
        from windows_auth.conf import WAUTH_DOMAINS

        if domain not in WAUTH_DOMAINS and DEFAULT_DOMAIN_SETTING not in WAUTH_DOMAINS:
            raise ImproperlyConfigured(f"Domain {domain} settings could not be found in WAUTH_DOMAINS setting.")

        domain_settings = WAUTH_DOMAINS.get(domain, {})
        # when setting is an LDAPSetting object
        if isinstance(domain_settings, LDAPSettings):
            return domain_settings

        default_settings = WAUTH_DOMAINS.get(DEFAULT_DOMAIN_SETTING, {})
        # when domain setting
        if isinstance(default_settings, LDAPSettings):
            default_settings = asdict(default_settings)

        # merge default and domain settings
        merged_settings: Dict[str, Any] = {**default_settings, **domain_settings}

        # validate domain settings
        for setting in filter(lambda f: f.default == MISSING and f.default_factory == MISSING, fields(cls)):
            if setting.name not in merged_settings:
                raise ImproperlyConfigured(f"Domain {domain} settings is missing a required setting: {setting.name}")

        cls_fields = {f.name for f in fields(cls)}
        return cls(**{
           setting: value(domain) if callable(value) else value
           for setting, value in merged_settings.items()
           if setting in cls_fields
        })

    def get_superuser_groups(self):
        return _get_group_list(self.SUPERUSER_GROUPS)

    def get_staff_groups(self):
        if self.PROPAGATE_GROUPS:
            return list({*_get_group_list(self.STAFF_GROUPS), *self.get_superuser_groups()})
        else:
            return _get_group_list(self.STAFF_GROUPS)

    def get_active_groups(self):
        if self.PROPAGATE_GROUPS:
            return list({*_get_group_list(self.ACTIVE_GROUPS), *self.get_staff_groups()})
        else:
            return _get_group_list(self.ACTIVE_GROUPS)

    def get_flag_map(self):
        return {
            "is_superuser": self.get_superuser_groups(),
            "is_staff": self.get_staff_groups(),
            "is_active": self.get_active_groups(),
            **{
                k: _get_group_list(v)
                for k, v in self.FLAG_MAP.items()
            }
        }
