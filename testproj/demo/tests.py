from django.test import TestCase, override_settings

from windows_auth.models import LDAPUser
from windows_auth.settings import LDAPSettings


class ModelTestCase(TestCase):

    def test_create_user(self):
        user = LDAPUser.objects.create_user("EXAMPLE\\Administrator")
        self.assertEqual(user.ldap.domain, "EXAMPLE")


class SettingsTestCase(TestCase):

    def test_flag_settings(self):
        settings = LDAPSettings(
            SERVER="example.local",
            SEARCH_BASE="DC=example,DC=local",
            USERNAME="EXAMPLE\\django_sync",
            PASSWORD="Aa123456!",
            SUPERUSER_GROUPS=None,
            STAFF_GROUPS=["List"],
            ACTIVE_GROUPS=["Explicit"],
            FLAG_MAP={
                "extra": "Hello world!",
            },
        )
        # check propagation
        self.assertEqual(settings.get_flag_map(), {
            "is_superuser": [],
            "is_staff": ["List"],
            "is_active": ["Explicit", "List"],
            "extra": ["Hello world!"],
        })
        # check without propagation
        settings.PROPAGATE_GROUPS = False
        self.assertEqual(settings.get_flag_map(), {
            "is_superuser": [],
            "is_staff": ["List"],
            "is_active": ["Explicit"],
            "extra": ["Hello world!"],
        })
        # check unique
        settings.PROPAGATE_GROUPS = True
        settings.ACTIVE_GROUPS = ["Explicit", "List"]
        self.assertEqual(settings.get_flag_map(), {
            "is_superuser": [],
            "is_staff": ["List"],
            "is_active": ["Explicit", "List"],
            "extra": ["Hello world!"],
        })
