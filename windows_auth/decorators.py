from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone

from windows_auth.conf import WAUTH_USE_CACHE
from windows_auth.models import LDAPUser


def domain_required(function=None, domain=None, login_url=None, bypass_superuser=True):
    """
    Decorator for views that checks whether a user is a domain member, redirecting to the log-in page if necessary.
    :param domain: member in a specific domain (default: None)
    :param login_url: redirect on failure
    :param bypass_superuser: allow superusers to access anyway (default: True)
    """
    def check_domain(user):
        # bypass if is superuser
        if bypass_superuser and user.is_superuser:
            return True

        if user.is_authenticated and LDAPUser.objects.filter(user=user).exists():
            if domain:
                # for specific domain
                return user.ldap.domain == domain
            else:
                # for all domains
                return True
        else:
            return False

    actual_decorator = user_passes_test(check_domain, login_url=login_url)
    if function:
        return actual_decorator(function)
    else:
        return actual_decorator


def ldap_sync_required(function=None, timedelta=None, login_url=None, allow_non_ldap=True, raise_exception=False):
    """
    Decorator for views that checks whether a user is synchronized against LDAP, re-syncing if necessary.
    When timedelta is None or when using cache, the user is re-synced on every request.
    If the raise_exception parameter is given the sync exception is raised and will cause status code 500.

    Notice: when WAUTH_USE_CACHE is True, the user will be re-synced on every request

    :param timedelta: maximum acceptable timedelta since last synchronization (default: None)
    :param login_url: redirect on failure
    :param allow_non_ldap: allow non-LDAP users to access (default: True)
    :param raise_exception: raise sync exception and cause status code 500
    """
    def check_sync(user):
        if user.is_authenticated and LDAPUser.objects.filter(user=user).exists():
            try:
                if WAUTH_USE_CACHE:
                    user.ldap.sync()
                else:
                    # check via database query
                    if not timedelta or user.ldap.last_sync < timezone.now() - timedelta:
                        user.ldap.sync()

                return True
            except Exception as e:
                if raise_exception:
                    raise e
                else:
                    return False
        else:
            return allow_non_ldap

    actual_decorator = user_passes_test(check_sync, login_url=login_url)
    if function:
        return actual_decorator(function)
    else:
        return actual_decorator
