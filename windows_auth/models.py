from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models

from windows_auth.ldap import LDAPManager


class LDAPUser(models.Model):
    user: User = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="ldap")

    domain: str = models.CharField(max_length=128, help_text="User Domain NetBIOS Name")

    last_sync = models.DateTimeField(blank=True, null=True, default=None,
                                     help_text="Last time performed LDAP sync for user attributes and group membership")

    def sync(self):
        manager = LDAPManager(self.domain)
        conn = manager.get_connection()

    def __str__(self):
        return f"{self.domain}\\{self.user.username}"

    def __repr__(self):
        return self.__str__()
