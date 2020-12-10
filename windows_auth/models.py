from typing import Union, Iterable, Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from django.db import models
from django.forms import model_to_dict
from django.utils import timezone
from ldap3 import Reader, Entry, Attribute

from windows_auth import logger
from windows_auth.conf import WAUTH_USE_CACHE
from windows_auth.ldap import LDAPManager, get_ldap_manager
from windows_auth.utils import debug_exec_time


def _match_groups(reader: Reader, groups: Optional[Union[Iterable[str], str]], attributes, default=False) -> bool:
    """

    :param reader:
    :param groups:
    :param attributes:
    :param default:
    :return:
    """
    if groups:
        if isinstance(groups, str):
            return bool(reader.match(attributes, groups))
        else:
            return bool(any(reader.match(attributes, group) for group in groups))
    else:
        return default


class LDAPUser(models.Model):
    user: User = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="ldap")

    domain: str = models.CharField(max_length=128, help_text="User Domain NetBIOS Name")

    last_sync = models.DateTimeField(blank=True, null=True, default=None,
                                     help_text="Last time performed LDAP sync for user attributes and group membership")

    def get_ldap_manager(self) -> LDAPManager:
        return get_ldap_manager(self.domain)

    def get_ldap_attr(self, attribute: str, as_list: bool = False):
        ldap_user = self.get_ldap_user(attributes=(attribute,))
        if attribute not in ldap_user:
            raise AttributeError(f"User {self.user} does not have LDAP Attribute {attribute}")

        attribute_obj: Attribute = getattr(ldap_user, attribute)
        if as_list:
            return attribute_obj.values
        else:
            return attribute_obj.value

    @debug_exec_time(lambda self, **kwargs: f"Query LDAP User {self}")
    def get_ldap_user(self, attributes: Optional[Iterable[str]] = None) -> Entry:
        manager = self.get_ldap_manager()
        user_reader = manager.get_reader(
            "user",
            f"objectCategory: person, {manager.settings.FIELD_MAP[manager.settings.QUERY_FIELD]}: "
            f"{getattr(self.user, manager.settings.QUERY_FIELD)}",
            attributes=attributes or ("distinguishedName", *manager.settings.FIELD_MAP.values()),
        )
        return user_reader.search()[0]

    def sync(self):
        start_time = timezone.now()

        logger.info(f"Syncing LDAP User {self}")

        # load settings
        manager = self.get_ldap_manager()

        # create user reader
        ldap_user = self.get_ldap_user()

        # create group reader
        # see the docs https://docs.microsoft.com/en-us/windows/win32/adsi/search-filter-syntax?redirectedfrom=MSDN
        group_query = f"(member:1.2.840.113556.1.4.1941:={ldap_user.distinguishedName})"
        group_reader = manager.get_reader("group", group_query, attributes=manager.settings.GROUP_ATTRS)
        logger.debug(f"Create group reader: {timezone.now() - start_time}")

        # calculate new fields
        updated_fields = {
            field: ldap_user[attr].value
            for field, attr in manager.settings.FIELD_MAP.items()
            if field is not manager.settings.QUERY_FIELD and ldap_user[attr].value is not None
        }

        group_reader.search()
        logger.debug(f"Query groups: {timezone.now() - start_time}")

        # update user flags
        for flag, groups, default in (
                ("is_superuser", manager.settings.SUPERUSER_GROUPS, False),
                ("is_staff", manager.settings.STAFF_GROUPS, False),
                ("is_active", manager.settings.ACTIVE_GROUPS, True),
        ):
            updated_fields[flag] = _match_groups(group_reader, groups, manager.settings.GROUP_ATTRS, default=default)

        logger.debug(f"Sync bool fields: {timezone.now() - start_time}")

        # add to groups
        for local_group_name, remote_groups in manager.settings.GROUP_MAP:
            local_group: Group = Group.objects.get(name=local_group_name)
            # translate single group to list
            if isinstance(remote_groups, str):
                remote_groups = [remote_groups]

            # when user is member in at least one group
            if any(group_reader.match(manager.settings.GROUP_ATTRS, remote_group) for remote_group in remote_groups):
                local_group.user_set.add(self.user)

        logger.debug(f"Sync groups: {timezone.now() - start_time}")

        # update changed fields for user
        current_fields = model_to_dict(self.user, fields=updated_fields.keys())
        if current_fields != updated_fields:
            get_user_model().objects.filter(pk=self.user.pk).update(**updated_fields)

        logger.debug(f"Update user fields: {timezone.now() - start_time}")

        # update sync time
        if not WAUTH_USE_CACHE:
            self.last_sync = timezone.now()
            self.save()
            logger.debug(f"Save LDAP User: {timezone.now() - start_time}")

    def __str__(self):
        return f"{self.domain}\\{self.user.username}"

    def __repr__(self):
        return self.__str__()
