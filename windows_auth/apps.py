from django.apps import AppConfig
from django.db.models import Count

from windows_auth import logger


class WindowsAuthConfig(AppConfig):
    name = 'windows_auth'

    def ready(self):
        from django.conf import settings
        from windows_auth.conf import WAUTH_IGNORE_SETTING_WARNINGS, WAUTH_PRELOAD_DOMAINS
        from windows_auth.settings import DEFAULT_DOMAIN_SETTING
        from windows_auth.ldap import get_ldap_manager

        # Note, when using "runserver" command this method will run multiple times due to the server first validating
        # models before loading the project. When using WAUTH_PRELOAD_DOMAINS, this may cause multiple LDAP connections
        # to be established and terminate quickly for each domain.
        # You can avoid this behavior by using "runserver --noreload" parameter,
        # or modifying the WAUTH_PRELOAD_DOMAINS setting to False.

        if not WAUTH_IGNORE_SETTING_WARNINGS and DEFAULT_DOMAIN_SETTING not in settings.WAUTH_DOMAINS:
            # check about users with domain missing from settings
            from windows_auth.models import LDAPUser
            missing_domains = LDAPUser.objects.exclude(domain__in=settings.WAUTH_DOMAINS.keys())
            if missing_domains.exists():
                for result in missing_domains.values("domain").annotate(count=Count("pk")):
                    logger.warning(f"Settings for domain \"{result.get('domain')}\" are missing from WAUTH_DOMAINS "
                                   f"({result.get('count')} users found)")

        # configure default preload domains
        preload_domains = WAUTH_PRELOAD_DOMAINS
        if preload_domains in (None, True):
            preload_domains = list(settings.WAUTH_DOMAINS.keys())
            if DEFAULT_DOMAIN_SETTING in preload_domains:
                preload_domains.remove(DEFAULT_DOMAIN_SETTING)

        if preload_domains:
            for domain in preload_domains:
                # TODO try catch to avoid failing the whole server
                # TODO log failed connections
                manager = get_ldap_manager(domain)
                if manager.connection.bound:
                    logger.info(f"Preloaded {domain} connection successfully.")
                else:
                    logger.warning(f"Failed to preload connection to domain {domain}.")

