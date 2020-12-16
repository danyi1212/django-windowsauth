from django.contrib.auth.backends import RemoteUserBackend
from django.core.cache import cache
from django.utils import timezone

from windows_auth.models import LDAPUser
from windows_auth.conf import WAUTH_USE_SPN, WAUTH_RESYNC_DELTA, WAUTH_USE_CACHE, WAUTH_REQUIRE_RESYNC, WAUTH_LOWERCASE_USERNAME


class WindowsAuthBackend(RemoteUserBackend):
    domain = None

    def clean_username(self, username: str):
        r"""
        Split the domain NetBIOS name and user's sAMAccountName from the REMOTE_USER header
        added to the request by IIS Windows Authentication feature.

        By default, value is expected in Credentials Management API's Down-Level Logon Name scheme (DOMAIN\UserName).
        Use WAUTH_USE_SPN to expect value to be is Credentials Management API's User Principle Name scheme (UserName@DomainFQDN.com).

        For more information see docs at https://docs.microsoft.com/en-us/windows/win32/secauthn/user-name-formats#down-level-logon-name.
        :param username: raw REMOTE_USER header value
        :return: cleaned sAMAccountName value from the
        """
        if WAUTH_USE_SPN:
            sam_account_name, self.domain = username.rsplit("@", 2)
        else:
            self.domain, sam_account_name = username.split("\\", 2)

        if WAUTH_LOWERCASE_USERNAME:
            return str(sam_account_name).lower()
        else:
            return sam_account_name

    def configure_user(self, request, user):
        """
        Create new LDAP User object and perform initialize LDAP sync
        """
        ldap_user = LDAPUser(
            user=user,
            domain=self.domain,
        )
        ldap_user.sync()

    def get_user(self, user_id):
        """
        Re-sync the user from LDAP, if necessary.
        :param user_id: user_id to re-sync
        """
        try:
            if WAUTH_RESYNC_DELTA not in (None, False):
                # convert timeout to seconds
                if isinstance(WAUTH_RESYNC_DELTA, timezone.timedelta):
                    timeout = WAUTH_RESYNC_DELTA.total_seconds()
                else:
                    timeout = int(WAUTH_RESYNC_DELTA)

                if WAUTH_USE_CACHE:
                    # if cache does not exist
                    if not cache.get(f"wauth_resync_user_{user_id}"):
                        ldap_user = LDAPUser.objects.get(user__pk=user_id)
                        ldap_user.sync()

                        # create new cache key
                        cache.set(f"wauth_rsync_user_{user_id}", True, timeout)
                else:
                    # check via database query
                    ldap_user = LDAPUser.objects.get(user__pk=user_id)
                    if ldap_user.last_sync < timezone.now() - timezone.timedelta(seconds=timeout):
                        ldap_user.sync()
        except LDAPUser.DoesNotExist:
            # user is getting created the first time
            pass
        except Exception as e:
            # TODO log
            if WAUTH_REQUIRE_RESYNC:
                raise e

        return super(WindowsAuthBackend, self).get_user(user_id)
