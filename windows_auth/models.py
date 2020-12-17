from typing import Union, Iterable, Optional, Dict

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from django.db import models
from django.forms import model_to_dict
from django.utils import timezone
from ldap3 import Reader, Entry, Attribute

from windows_auth import logger
from windows_auth.conf import WAUTH_USE_CACHE, WAUTH_USE_SPN
from windows_auth.ldap import LDAPManager, get_ldap_manager
from windows_auth.utils import LogExecutionTime


def _match_groups(reader: Reader, groups: Optional[Union[Iterable[str], str]], attributes, default=False) -> bool:
    """
    Check if at least one of the provided groups exists in a LDAP Reader for Groups.
    :param reader: LDAP Reader for Groups
    :param groups: One or more group names
    :param attributes: List of attributes to check for comparing group's name
    :param default: Default value when no group is provided.
    :return: Boolean if exist
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

    _ldap_user_cache: Optional[Entry] = None

    def get_ldap_manager(self) -> LDAPManager:
        return get_ldap_manager(self.domain)

    def get_ldap_attr(self, attribute: str, as_list: bool = False, refresh_cache: bool = False):
        """
        Get a specific attribute of the related LDAP User.
        LDAP User entry is saved as cache in process memory to avoid unnecessary LDAP queries.
        :param attribute: The name of the LDAP attribute to get
        :param as_list: The attribute's value is a list
        :param refresh_cache: Ignore cached entry, and overwrite value with new one
        :return: Value of attribute from the related LDAP User
        """
        if refresh_cache or not self._ldap_user_cache or attribute not in self._ldap_user_cache:
            ldap_user = self.get_ldap_user(attributes=(attribute,))
            if attribute not in ldap_user:
                raise AttributeError(f"User {self.user} does not have LDAP Attribute {attribute}")
        else:
            ldap_user = self._ldap_user_cache

        attribute_obj: Attribute = getattr(ldap_user, attribute)
        if as_list:
            return attribute_obj.values
        else:
            return attribute_obj.value

    def get_ldap_user(self, attributes: Optional[Iterable[str]] = None, refresh_cache: bool = False) -> Entry:
        """
        Query LDAP for related user entry.
        LDAP User entry is saved as cache in process memory to avoid unnecessary LDAP queries.
        :param attributes: List of attributes to get
        :param refresh_cache: Ignore cached entry, and overwrite value with new one
        :return: ldap3 Entry of the related LDAP User
        """
        # re-query when no cache available or is missing a requested attribute
        if refresh_cache or not self._ldap_user_cache or all(attr not in self._ldap_user_cache for attr in attributes):
            manager = self.get_ldap_manager()
            user_reader = manager.get_reader(
                "user",
                f"objectCategory: person, {manager.settings.USER_FIELD_MAP[manager.settings.USER_QUERY_FIELD]}: "
                f"{getattr(self.user, manager.settings.USER_QUERY_FIELD)}",
                attributes=attributes or manager.settings.USER_FIELD_MAP.values(),
            )
            with LogExecutionTime(f"Query LDAP User {self}"):
                self._ldap_user_cache = user_reader.search()[0]

        return self._ldap_user_cache

    def get_ldap_groups(self, attributes: Optional[Iterable[str]] = None, preload: bool = True) -> Reader:
        """
        Get a reader for all groups this user is member of, recursively.
        See the docs https://docs.microsoft.com/en-us/windows/win32/adsi/search-filter-syntax?redirectedfrom=MSDN
        :param attributes: LDAP Group attributes to get
        :param preload: Perform search automatically
        :return: ldap3 Reader for the related LDAP Groups
        """
        manager = self.get_ldap_manager()
        user_dn = self.get_ldap_attr("distinguishedName")
        reader = manager.get_reader(
            "group",
            f"(member:1.2.840.113556.1.4.1941:={user_dn})",
            attributes=attributes or manager.settings.GROUP_ATTRS
        )
        # search groups
        if preload:
            with LogExecutionTime(f"Query LDAP Group membership for user {self}"):
                reader.search()

        return reader

    def sync(self) -> None:
        """
        Synchronizes Django User against related LDAP User.

        Fields are synchronized using USER_FIELD_MAP from the domain's LDAP Settings.
        User flags are using SUPERUSER_GROUPS, STAFF_GROUPS and ACTIVE_GROUPS settings.
        Group membership is replicated using GROUPS_MAP setting.

        :return: None
        """
        logger.info(f"Syncing LDAP User {self}")
        manager = self.get_ldap_manager()

        # query user
        # add distinguishedName to user query to be used in group query and avoid two user queries
        ldap_user = self.get_ldap_user(attributes=("distinguishedName", *manager.settings.USER_FIELD_MAP.values()))

        # query groups
        group_reader = self.get_ldap_groups()

        # calculate new fields
        updated_fields = {
            field: ldap_user[attr].value
            for field, attr in manager.settings.USER_FIELD_MAP.items()
            if field is not manager.settings.USER_QUERY_FIELD and ldap_user[attr].value is not None
        }

        # check user flags
        flags = []
        if manager.settings.SUPERUSER_GROUPS:
            flags.append(("is_superuser", manager.settings.SUPERUSER_GROUPS, False))
        if manager.settings.STAFF_GROUPS:
            flags.append(("is_staff", manager.settings.STAFF_GROUPS, False))
        if manager.settings.ACTIVE_GROUPS:
            flags.append(("is_active", manager.settings.ACTIVE_GROUPS, True))

        # update user flags
        for flag, groups, default in flags:
            updated_fields[flag] = _match_groups(group_reader, groups, manager.settings.GROUP_ATTRS, default=default)

        # check group membership
        group_membership: Dict[Group, bool] = {}
        for local_group_name, remote_groups in manager.settings.GROUP_MAP.items():
            # get group model object
            local_group, created = Group.objects.get_or_create(name=local_group_name)

            if created:
                logger.info(f"The group \"{local_group_name}\" from GROUP_MAP setting for domain {self.domain}"
                            f" was not found and was created automatically.")

            # check if user supposes to me a member
            group_membership[local_group] = _match_groups(group_reader, remote_groups, manager.settings.GROUP_ATTRS)

        # add to groups
        self.user.groups.add(*(
            local_group
            for local_group, membership_check in group_membership.items()
            if membership_check
        ))

        # remove from groups
        self.user.groups.remove(*(
            local_group
            for local_group, membership_check in group_membership.items()
            if not membership_check
        ))

        # update changed fields for user
        current_fields = model_to_dict(self.user, fields=updated_fields.keys())
        if current_fields != updated_fields:
            with LogExecutionTime(f"Perform field updates for user {self}"):
                get_user_model().objects.filter(pk=self.user.pk).update(**updated_fields)

        # update sync time
        if not WAUTH_USE_CACHE:
            with LogExecutionTime(f"Save LDAP User {self}"):
                self.last_sync = timezone.now()
                self.save()

    def __str__(self):
        if WAUTH_USE_SPN:
            return f"{self.user.username}@{self.domain}"
        else:
            return f"{self.domain}\\{self.user.username}"

    def __repr__(self):
        return self.__str__()
