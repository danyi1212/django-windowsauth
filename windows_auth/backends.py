from django.contrib.auth.backends import RemoteUserBackend

from windows_auth.conf import WAUTH_USE_SPN, WAUTH_LOWERCASE_USERNAME
from windows_auth.models import LDAPUser


class WindowsAuthBackend(RemoteUserBackend):
    domain = None

    def clean_username(self, username: str):
        r"""
        Split the domain NetBIOS name and user's sAMAccountName from the REMOTE_USER header
        added to the request by IIS Windows Authentication feature.

        By default, value is expected in Credentials Management API's Down-Level Logon Name scheme (DOMAIN\UserName).
        Use WAUTH_USE_SPN to expect value to be is Credentials Management API's User Principal Name scheme (UserName@DomainFQDN.com).

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
