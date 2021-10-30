from unittest import mock

from django.test import TestCase, override_settings, RequestFactory
from django.urls import reverse

from windows_auth.conf import wauth_settings
from windows_auth.ldap import get_ldap_manager
from windows_auth.middleware import SimulateWindowsAuthMiddleware
from windows_auth.settings import LDAPSettings


class ModelTestCase(TestCase):
    pass

    # def test_create_user(self):
    #     user = LDAPUser.objects.create_user("EXAMPLE\\Administrator")
    #     self.assertEqual(user.ldap.domain, "EXAMPLE")


class SettingsTestCase(TestCase):

    def test_flag_propagation(self):
        ldap_settings = LDAPSettings(
            SERVER="",
            SEARCH_BASE="",
            USERNAME="",
            PASSWORD="",
            SUPERUSER_GROUPS=["Super"],
            STAFF_GROUPS=["Staff", "Duplicate"],
            ACTIVE_GROUPS=["Active", "Duplicate"],
            FLAG_MAP={
                "extra": "Extra",
            },
        )
        flag_map = ldap_settings.get_flag_map()
        self.assertEqual(set(flag_map.get("is_superuser")), {"Super"})
        self.assertEqual(set(flag_map.get("is_staff")), {"Staff", "Super", "Duplicate"})
        self.assertEqual(set(flag_map.get("is_active")), {"Active", "Duplicate", "Staff", "Super"})
        self.assertEqual(set(flag_map.get("extra")), {"Extra"})

    def test_flag_propagation_disabled(self):
        ldap_settings = LDAPSettings(
            SERVER="",
            SEARCH_BASE="",
            USERNAME="",
            PASSWORD="",
            SUPERUSER_GROUPS=["Super"],
            STAFF_GROUPS=["Staff"],
            ACTIVE_GROUPS=["Active"],
            FLAG_MAP={
                "extra": "Extra",
            },
            PROPAGATE_GROUPS=False,
        )
        self.assertEqual(
            ldap_settings.get_flag_map(),
            dict(
                is_superuser=["Super"],
                is_staff=["Staff"],
                is_active=["Active"],
                extra=["Extra"],
            )
        )


class MiddlewareTestCase(TestCase):
    middleware_class = SimulateWindowsAuthMiddleware

    def setUp(self):
        self.factory = RequestFactory()

    @property
    def middleware(self):
        get_response = mock.MagicMock()
        return self.middleware_class(get_response)

    @override_settings(DEBUG=True, WAUTH_SIMULATE_USER="test_user")
    def test_auth_simulation(self):
        request = self.factory.get(reverse("demo:index"))
        self.middleware(request)
        self.assertEqual(request.META.get("REMOTE_USER"), wauth_settings.WAUTH_SIMULATE_USER)

    # @override_settings(DEBUG=True)
    # def test_skip_simulation(self, username="test_user"):
    #     """Keep existing REMOTE_USER header"""
    #     request = self.factory.get(reverse("demo:index"), REMOTE_ADDR=username)
    #     self.middleware(request)
    #     self.assertEqual(request.META.get("REMOTE_USER"), username)

    @override_settings(DEBUG=False)
    def test_bypass_auth(self):
        """Bypass user simulation when not in debug"""
        request = self.factory.get(reverse("demo:index"))
        self.middleware(request)
        self.assertEqual(request.META.get("REMOTE_USER"), None)


class ManagerTestCase(TestCase):

    def test_connection(self):
        manager = get_ldap_manager("EXAMPLE")
        self.assertTrue(manager.connection.bound)
