import atexit

from django.conf import settings
from django.db import DatabaseError
from ldap3.core.exceptions import LDAPException
from django.apps import AppConfig
from django.db.models import Count

from windows_auth import logger


class WindowsAuthConfig(AppConfig):
    name = 'windows_auth'
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        from windows_auth.conf import wauth_settings
        from windows_auth.settings import DEFAULT_DOMAIN_SETTING
        from windows_auth.ldap import get_ldap_manager, close_connections

        # Note, when using "runserver" command this method will run multiple times due to the server first validating
        # models before loading the project. When using WAUTH_PRELOAD_DOMAINS, this may cause multiple LDAP connections
        # to be established and terminate quickly for each domain.
        # You can avoid this behavior by using "runserver --noreload" parameter,
        # or modifying the WAUTH_PRELOAD_DOMAINS setting to False.

        if (
                not hasattr(settings, "WAUTH_DOMAINS")
                and not getattr(settings, "WAUTH_IGNORE_SETTING_WARNINGS", False)
        ):
            logger.warn("The required setting WAUTH_DOMAINS is missing.")

        # check about users with domain missing from settings
        if not wauth_settings.WAUTH_IGNORE_SETTING_WARNINGS and DEFAULT_DOMAIN_SETTING not in wauth_settings.WAUTH_DOMAINS:
            try:
                from windows_auth.models import LDAPUser
                missing_domains = LDAPUser.objects.exclude(domain__in=wauth_settings.WAUTH_DOMAINS.keys())
                if missing_domains.exists():
                    for result in missing_domains.values("domain").annotate(count=Count("pk")):
                        logger.warning(f"Settings for domain \"{result.get('domain')}\" are missing from WAUTH_DOMAINS "
                                       f"({result.get('count')} users found)")
            except DatabaseError as e:
                # Table probably does not exist yet, migration is pending
                logger.warn(e)

        # configure default preload domains
        preload_domains = wauth_settings.WAUTH_PRELOAD_DOMAINS
        if preload_domains in (None, True):
            preload_domains = list(wauth_settings.WAUTH_DOMAINS.keys())
            if DEFAULT_DOMAIN_SETTING in preload_domains:
                preload_domains.remove(DEFAULT_DOMAIN_SETTING)

        # preload domains
        if preload_domains:
            for domain in preload_domains:
                try:
                    # attempt to load LDAP connection
                    manager = get_ldap_manager(domain)
                    if manager.connection.bound:
                        logger.debug(f"Preloaded LDAP connection to domain {domain} successfully.")
                    else:
                        logger.warning(f"Failed to preload connection to domain {domain}.")
                except LDAPException as e:
                    logger.exception(f"Failed to preload connection to domain {domain}.")

        # unbind all connection at exit
        atexit.register(close_connections)

