from dataclasses import dataclass

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from ldap3 import Connection, Server


@dataclass
class LDAPSettings:
    SERVER = None
    USERNAME = None
    PASSWORD = None
    USE_SSL = True

    def __init__(self, domain: str):
        try:
            domain_settings = settings.WAUTH_DOMAINS[domain]
        except KeyError:
            raise ImproperlyConfigured(f"Domain {domain} settings could not be found in WAUTH_DOMAINS setting.")
        super(LDAPSettings, self).__init__(**domain_settings)


class LDAPManager:

    def __init__(self, domain: str):
        self.domain = domain
        self.settings = LDAPSettings(domain)

    def get_server_host(self):
        return ""

    def get_server(self) -> Server:
        return Server(
            host=self.get_server_host(),
            use_ssl=settings.WAUTH_LDAP_USE_SSL
        )

    def get_connection(self) -> Connection:
        return Connection(self.get_server(), )