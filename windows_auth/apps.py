from django.apps import AppConfig
from django.db.models import Count

from windows_auth import logger


class WindowsAuthConfig(AppConfig):
    name = 'windows_auth'

    def ready(self):
        from windows_auth.conf import settings, WAUTH_IGNORE_SETTING_WARNINGS

        if not WAUTH_IGNORE_SETTING_WARNINGS:
            # check about users with domain missing from settings
            from windows_auth.models import LDAPUser
            missing_domains = LDAPUser.objects.exclude(domain__in=settings.WAUTH_DOMAINS.keys())
            if missing_domains.exists():
                for result in missing_domains.values("domain").annotate(count=Count("pk")):
                    logger.warning(f"Settings for domain \"{result.get('domain')}\" are missing from WAUTH_DOMAINS "
                                   f"({result.get('count')} users found)")
