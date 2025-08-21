import os
from typing import List

import ldap3
from django.conf import settings
from django.core.checks import register, CheckMessage, Error, Warning, Info
from django.db import DatabaseError
from django.db.models import Count
from ldap3.core.exceptions import LDAPException

from windows_auth import logger
from windows_auth.conf import WAUTH_IGNORE_SETTING_WARNINGS, WAUTH_DOMAINS, WAUTH_USE_CACHE, WAUTH_USE_SPN
from windows_auth.ldap import get_ldap_manager
from windows_auth.models import LDAPUser
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

    return messages


@register()
def check_missing_domains(app_configs, **kwargs):
    messages: List[CheckMessage] = []

    # TODO deprecate WAUTH_IGNORE_SETTING_WARNINGS
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


@register(deploy=True)
def check_deployment_settings(app_configs, **kwargs):
    messages: List[CheckMessage] = []

    # check cache system enabled
    if not WAUTH_USE_CACHE:
        messages.append(
            Info(
                "Using the database to check LDAP user last sync time is slow. "
                "If you can, you should use cache system instead.",
                hint="Set WAUTH_USE_CACHE to True",
                id="wauth.I011",
            )
        )

    # check LDAP settings
    for domain in WAUTH_DOMAINS.keys():
        # skip loading default domain
        if domain == DEFAULT_DOMAIN_SETTING:
            continue

        manager = get_ldap_manager(domain)

        # check SSL
        if not manager.settings.USE_SSL:
            messages.append(
                Warning(
                    "USE_SSL is not set to True. It is recommended to use only secure LDAP connection.",
                    obj=domain,
                    id="wauth.W012",
                )
            )

        # check authentication method
        if not manager.settings.CONNECTION_OPTIONS.get("authentication") in (ldap3.SASL, ldap3.NTLM):
            messages.append(
                Warning(
                    "You should use a stronger authentication method for you LDAP connection.",
                    hint="Configure \"authentication\" to SASL or NTLM in you CONNECTION_OPTIONS.",
                    obj=domain,
                    id="wauth.W013"
                )
            )

        # check bind user
        if WAUTH_USE_SPN:
            username, user_domain = manager.settings.USERNAME.rsplit("@", 2)
        else:
            user_domain, username = manager.settings.USERNAME.split("\\", 2)

        if LDAPUser.objects.filter(user__username=username, domain=user_domain).exists():
            messages.append(
                Warning(
                    "You should use a dedicated bind account with the minimum permissions needed.",
                    hint="Your bind account has logged in to website.",
                    obj=domain,
                    id="wauth.W014",
                )
            )

        # check dedicated writeable connections
        if not manager.settings.READ_ONLY and LDAPUser.objects.filter(domain=domain).exists():
            messages.append(
                Warning(
                    "You should use a dedicated connection for you write operations. "
                    "Using a different connection, and even another bind account, is considered best-practice.",
                    obj=domain,
                    id="wauth.W015",
                )
            )

    return messages


@register(deploy=True)
def check_deployment_setup(app_configs, **kwargs):
    messages: List[CheckMessage] = []

    # check project drive is not OS drive
    system_drive = os.environ.get('SYSTEMDRIVE')
    current_drive, path = os.path.splitdrive(__file__)
    if system_drive == current_drive:
        messages.append(
            Info(
                "You should keep your site and project files on a separate disk from the OS.",
                id="wauth.I020",
            )
        )

    return messages
