from typing import List, Union, Iterable, Optional, Dict

from ldap3 import Connection, Server, Reader, ObjectDef, AttrDef

from windows_auth import logger
from windows_auth.conf import LDAPSettings


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

        # preload definitions
        if self.settings.PRELOAD_DEFINITIONS:
            logger.info("Preloading LDAP Schema definitions for objects: {0}".format(
                ', '.join(map(
                    lambda d: d if isinstance(d, str) else d[0],
                    self.settings.PRELOAD_DEFINITIONS
                ))
            ))
            for definition in self.settings.PRELOAD_DEFINITIONS:
                if isinstance(definition, str):
                    self.get_definition(definition)
                else:
                    object_class, attributes = definition
                    self.get_definition(object_class, attributes=attributes)

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


def get_ldap_manager(domain: str, settings: Optional[LDAPSettings] = None) -> LDAPManager:
    if domain not in _ldap_connections:
        _ldap_connections[domain] = LDAPManager(domain, settings=settings)

    return _ldap_connections[domain]
