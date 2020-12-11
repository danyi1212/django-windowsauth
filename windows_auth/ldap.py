from typing import List, Union, Iterable, Optional, Dict

from ldap3 import Connection, Server, Reader, ObjectDef, AttrDef

from windows_auth import logger
from windows_auth.conf import LDAPSettings
from windows_auth.utils import LogExecutionTime


class LDAPManager:

    def __init__(self, domain: str, settings: Optional[LDAPSettings] = None):
        self.domain = domain
        self.settings = settings if settings else LDAPSettings(domain)
        # create server
        self.server = self._create_server()
        # bind connection
        with LogExecutionTime(f"Binding LDAP connection for domain {self.domain}"):
            self._conn = self._create_connection()
        logger.info(f"LDAP Connection Info: {self.connection}")

        self.definitions: Dict[str, ObjectDef] = {}

        # preload definitions
        if self.settings.PRELOAD_DEFINITIONS:
            for definition in self.settings.PRELOAD_DEFINITIONS:
                if isinstance(definition, str):
                    self.get_definition(definition)
                else:
                    object_class, attributes = definition
                    self.get_definition(object_class, attributes=attributes)

        # save manager to process context
        _ldap_connections[domain] = self

    def _create_server(self) -> Server:
        return Server(
            host=self.settings.SERVER,
            use_ssl=self.settings.USE_SSL,
            **self.settings.SERVER_OPTIONS
        )

    def _create_connection(self) -> Connection:
        return Connection(
            self.server,
            user=self.settings.USERNAME,
            password=self.settings.PASSWORD,
            auto_bind=True,
            **self.settings.CONNECTION_OPTIONS,
        )

    @property
    def connection(self) -> Connection:
        if not self._conn.bound:
            with LogExecutionTime(f"Rebinding connection for domain {self.domain}"):
                self._conn.rebind()
        return self._conn

    def get_definition(self, object_class: Union[str, List[str]], attributes: Iterable[str] = None) -> ObjectDef:
        """
        Get a new object class definition automatically from LDAP Schema.
        object definitions are save as cache for later use in connection.
        :param object_class: The LDAP objectClass type to define
        :param attributes: Extra LDAP attributes to include
        :return: ldap3 ObjectDef instance
        """
        # create definition if missing
        if object_class not in self.definitions:
            with LogExecutionTime(f"Loading LDAP Schema definition for objectClass {object_class}"):
                self.definitions[object_class] = ObjectDef(object_class, self.connection)

        # add missing attributes
        if attributes:
            for attr in attributes:
                if attr not in self.definitions[object_class]:
                    self.definitions[object_class] += AttrDef(attr)

        return self.definitions[object_class]

    def get_reader(self, object_class: Union[str, List[str]], query: str = None, attributes: Iterable[str] = None) -> Reader:
        """
        Create a new ldap3 Reader for an object.
        Object definition is generated using LDAP Schema and is cached in the LDAP Manager for later uses.
        Query may be an LDAP query filter or ldap3 Simplified Query Language.
        See the docs https://ldap3.readthedocs.io/en/latest/abstraction.html#simplified-query-language
        :param object_class: LDAP objectClass type to refer to
        :param query: Optional query to narrow down the search
        :param attributes: Specific attributes to read
        :return: ldap3 Reader object
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
    """
    Get or create new LDAP Manager using local process memory as cache
    :param domain: LDAP Manager for domain
    :param settings: Custom LDAP Settings
    :return: LDAP Manager
    """
    if domain not in _ldap_connections:
        _ldap_connections[domain] = LDAPManager(domain, settings=settings)

    return _ldap_connections[domain]
