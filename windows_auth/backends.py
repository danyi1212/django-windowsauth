from django.contrib import messages
from django.contrib.auth.backends import RemoteUserBackend
from django.core.exceptions import ImproperlyConfigured

from windows_auth.models import LDAPUser


class WindowsAuthBackend(RemoteUserBackend):
    domain = None

    def clean_username(self, username: str):
        r"""
        Split the domain NetBIOS name and user's sAMAccountName from the REMOTE_USER header
        added to the request by IIS Windows Authentication feature in the
        Credentials Management API's Down-Level Logon Name scheme (DOMAIN\UserName).

        For more information see docs at https://docs.microsoft.com/en-us/windows/win32/secauthn/user-name-formats#down-level-logon-name.
        :param username:
        :return:
        """
        self.domain, sam_account_name = username.split("\\", 2)
        return sam_account_name

    def configure_user(self, request, user):
        ldap_user = LDAPUser(
            user=user,
            domain=self.domain,
        )

        try:
            ldap_user.sync()
        except ImproperlyConfigured as e:
            messages.error(request, f"Domain {self.domain} is not allowed")

        ldap_user.save()

