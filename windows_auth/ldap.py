from typing import List, Union, Iterable, Optional, Dict

from ldap3 import Connection, Server, Reader, ObjectDef, AttrDef

from windows_auth import logger
from windows_auth.conf import LDAPSettings


# TODO keep connection active for multiple syncs
# TODO pre load / lazy load connections setting


class LDAPManager:

    def __init__(self, domain: str, settings: Optional[LDAPSettings] = None):
        self.domain = domain
        self.settings = settings if settings else LDAPSettings(domain)
        # create server
        self.server = self.create_server()
        # bind connection
        self._conn = self.create_connection()
        logger.info(f"LDAP Connection Info: {self.connection}")
        # load definitions
        # TODO preload definitions
        self.definitions: Dict[str, ObjectDef] = {}
        # save manager to process context
        _ldap_connections[domain] = self

    @property
    def connection(self) -> Connection:
        if not self._conn.bound:
            self._conn.rebind()
        return self._conn

    def create_server(self) -> Server:
        return Server(
            host=self.settings.SERVER,
            use_ssl=self.settings.USE_SSL,
            **self.settings.SERVER_OPTIONS
        )

    def create_connection(self) -> Connection:
        return Connection(
            self.server,
            user=self.settings.USERNAME,
            password=self.settings.PASSWORD,
            auto_bind=True,
            **self.settings.CONNECTION_OPTIONS,
        )

    def get_definition(self, object_class: Union[str, List[str]], attributes: Iterable[str] = None) -> ObjectDef:
        # create definition if missing
        if object_class not in self.definitions:
            self.definitions[object_class] = ObjectDef(object_class, self.connection)

        # add missing attributes
        if attributes:
            for attr in attributes:
                if attr not in self.definitions[object_class]:
                    self.definitions[object_class] += AttrDef(attr)

        return self.definitions[object_class]

    def get_reader(self, object_class: Union[str, List[str]], query: str = None, attributes: Iterable[str] = None) -> Reader:
        """

        :rtype: object
        """
        return Reader(
            self.connection,
            self.get_definition(object_class, attributes=attributes),
            self.settings.SEARCH_SCOPE,
            query,
            attributes=attributes
        )


_ldap_connections: Dict[str, LDAPManager] = {}
# TODO preload domain connections


def get_ldap_manager(domain: str, settings: Optional[LDAPSettings] = None) -> LDAPManager:
    if domain in _ldap_connections:
        return _ldap_connections[domain]
    else:
        return LDAPManager(domain, settings=settings)
