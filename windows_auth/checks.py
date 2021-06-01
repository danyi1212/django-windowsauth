from typing import List

from django.conf import settings
from django.core.checks import register, CheckMessage, Error, Warning
from django.db import DatabaseError
from django.db.models import Count
from ldap3.core.exceptions import LDAPException

from windows_auth import logger
from windows_auth.conf import WAUTH_IGNORE_SETTING_WARNINGS, WAUTH_DOMAINS
from windows_auth.ldap import get_ldap_manager
from windows_auth.settings import DEFAULT_DOMAIN_SETTING


@register()
def check_widows_auth_settings(app_configs, **kwargs):
    messages: List[CheckMessage] = []

    # Require WAUTH_DOMAINS
    if not hasattr(settings, "WAUTH_DOMAINS"):
        messages.append(
            Error(
                "Required setting \"WAUTH_DOMAINS\" is not configured.",
                hint="Add \"WAUTH_DOMAINS\" to your settings file.",
                id="wauth.E001"
            )
        )

    # Require WAUTH_SIMULATE_USER
    if 'windows_auth.middleware.SimulateWindowsAuthMiddleware' in settings.MIDDLEWARE \
            and not hasattr(settings, "WAUTH_SIMULATE_USER"):
        messages.append(
            Error(
                "You have \'windows_auth.middleware.SimulateWindowsAuthMiddleware\' in your MIDDLEWARE, "
                "but you have not configured WAUTH_SIMULATE_USER.",
                id="wauth.E006",
            )
        )

    # TODO deprecate WAUTH_IGNORE_SETTING_WARNINGS
    # Search missing domains
    if not WAUTH_IGNORE_SETTING_WARNINGS and DEFAULT_DOMAIN_SETTING not in WAUTH_DOMAINS:
        try:
            from windows_auth.models import LDAPUser
            missing_domains = LDAPUser.objects.exclude(domain__in=WAUTH_DOMAINS.keys())
            for result in missing_domains.values("domain").annotate(count=Count("pk")):
                messages.append(
                    Warning(
                        f"Found missing domain settings for \"{result.get('domain')}\" "
                        f"({result.get('count')} LDAP users from this domain found in the database).",
                        hint=f"Add settings for \"{result.get('domain')}\" in WAUTH_DOMAINS.",
                        obj=result.get("domain"),
                        id="wauth.W002"
                    )
                )
        except DatabaseError as e:
            logger.exception(f"Unable to load LDAPUser model: {e}")
            # Table probably does not exist yet, migration is pending
            messages.append(
                Error(
                    "Unable to load LDAPUser model",
                    hint="Try running \"py manage.py migrate windows_auth\".",
                    id="wauth.E003",
                )
            )

    return messages


@register()
def check_ldap_domains(app_configs, **kwargs):
    messages: List[CheckMessage] = []

    for domain in WAUTH_DOMAINS.keys():
        # skip loading default domain
        if domain == DEFAULT_DOMAIN_SETTING:
            continue

        try:
            # attempt to load LDAP connection
            manager = get_ldap_manager(domain)
            if not manager.connection.bound:
                messages.append(
                    Warning(
                        f"Unable to create LDAP connection with domain {domain}.",
                        obj=domain,
                        id="wauth.W004",
                    ),
                )
        except LDAPException as e:
            messages.append(
                Error(
                    f"Error while creating LDAP connection with domain {domain}: {e}",
                    obj=domain,
                    id="wauth.E005",
                ),
            )

    return messages


@register(deploy=True)
def check_simulate_wauth(app_configs, **kwargs):
    messages: List[CheckMessage] = []

    if 'windows_auth.middleware.SimulateWindowsAuthMiddleware' in settings.MIDDLEWARE:
        messages.append(
            Warning(
                "You should not have \'windows_auth.middleware.SimulateWindowsAuthMiddleware\' "
                "in your middleware in production.",
                id="wauth.W010"
            )
        )

    return messages
