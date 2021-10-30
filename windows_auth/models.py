from functools import lru_cache
from typing import Union, Iterable, Optional, Dict

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from django.db import models
from django.forms import model_to_dict
from django.utils import timezone
from ldap3 import Reader, Entry, Attribute

from windows_auth import logger
from windows_auth.conf import wauth_settings
from windows_auth.ldap import LDAPManager, get_ldap_manager
from windows_auth.signals import ldap_user_sync
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
    if not groups:
        return default
    elif isinstance(groups, str):
        return bool(reader.match(attributes, groups))
    else:
        return bool(any(reader.match(attributes, group) for group in groups))


class LDAPUserManager(models.Manager):

    def create_user(self, username: str) -> User:
        r"""
        Create, save, synchronize against LDAP and return a User object.
        :param username: Logon username (DOMAIN\username or username@domain.com)
        :return: User object (not LDAPUser)
        """
        if wauth_settings.WAUTH_USE_SPN:
            if "@" not in username:
                raise ValueError("Username must be in username@domain.com format.")

            sam_account_name, domain = username.split("@", 2)
        else:
            if "\\" not in username:
                raise ValueError("Username must be in DOMAIN\\username format.")

            domain, sam_account_name = username.split("\\", 2)

        if wauth_settings.WAUTH_LOWERCASE_USERNAME:
            sam_account_name = sam_account_name.lower()

        user = get_user_model().objects.create_user(username=sam_account_name)
        ldap_user = self.create(user=user, domain=domain)
        ldap_user.sync()
        return user


class LDAPUser(models.Model):
    user: User = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="ldap")

    domain: str = models.CharField(max_length=128, help_text="User Domain NetBIOS Name")

    last_sync = models.DateTimeField(blank=True, null=True, default=None,
                                     help_text="Last time performed LDAP sync for user attributes and group membership")

    objects = LDAPUserManager()

    _ldap_user_cache: Optional[Entry] = None

    def get_ldap_manager(self) -> LDAPManager:
        return get_ldap_manager(self.domain)

    def get_ldap_attr(self, attribute: str, as_list: bool = False):
        """
        Get a specific attribute of the related LDAP User.
        :param attribute: The name of the LDAP attribute to get
        :param as_list: The attribute's value is a list
        :return: Value of attribute from the related LDAP User
        """
        ldap_user = self.get_ldap_user()

        # check if is already in default cached entry
        if attribute not in ldap_user:
            ldap_user = self.get_ldap_user(attributes=[attribute])

        if attribute not in ldap_user:
            raise AttributeError(f"User {self.user} does not have LDAP Attribute {attribute}")

        attribute_obj: Attribute = getattr(ldap_user, attribute)
        if as_list:
            return attribute_obj.values
        else:
            return attribute_obj.value

    @lru_cache()
    def get_ldap_user(self, attributes: Optional[Iterable[str]] = None) -> Entry:
        """
        Query LDAP for related user entry.
        :param attributes: List of attributes to get
        :return: ldap3 Entry of the related LDAP User
        """
        # re-query when no cache available or is missing a requested attribute
        manager = self.get_ldap_manager()
        username_ldap_field = manager.settings.USER_FIELD_MAP[manager.settings.USER_QUERY_FIELD]
        ldap_filter = {
            **manager.settings.USER_QUERY_FILTER,
            username_ldap_field: getattr(self.user, manager.settings.USER_QUERY_FIELD)
        }
        user_reader = manager.get_reader(
            "user",
            ", ".join(f"{key}: {value}" for key, value in ldap_filter.items()),
            attributes=attributes or manager.settings.USER_FIELD_MAP.values(),
        )
        with LogExecutionTime(f"Query LDAP User {self}"):
            return user_reader.search()[0]

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
        for flag, groups in manager.settings.get_flag_map().items():
            if groups:
                updated_fields[flag] = _match_groups(group_reader, groups, manager.settings.GROUP_ATTRS)

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

        # send signals
        ldap_user_sync.send(self, ldap_user=ldap_user, group_reader=group_reader)

        # update sync time
        if not wauth_settings.WAUTH_USE_CACHE:
            with LogExecutionTime(f"Save LDAP User {self}"):
                self.last_sync = timezone.now()
                self.save()

    def __str__(self):
        if wauth_settings.WAUTH_USE_SPN:
            return f"{self.user.username}@{self.domain}"
        else:
            return f"{self.domain}\\{self.user.username}"

    def __repr__(self):
        return self.__str__()
