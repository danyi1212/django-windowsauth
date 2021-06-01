from unittest import mock

from django.test import TestCase, override_settings, RequestFactory
from django.urls import reverse

from windows_auth.middleware import SimulateWindowsAuthMiddleware
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


class MiddlewareTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def pass_middleware(self, request):
        get_response = mock.MagicMock()
        middleware = SimulateWindowsAuthMiddleware(get_response)
        return middleware(request)

    @override_settings(DEBUG=True)
    def test_auth_simulation(self):
        request = self.factory.get(reverse("demo:index"))
        self.pass_middleware(request)
        self.assertTrue(request.META.get("REMOTE_USER"))

    @override_settings(DEBUG=True)
    def test_skip_simulation(self):
        request = self.factory.get(reverse("demo:index"), REMOTE_ADDR="test")
        self.pass_middleware(request)
        self.assertEqual(request.META.get("REMOTE_USER"), "test")

    @override_settings(DEBUG=False)
    def test_bypass_auth(self):
        request = self.factory.get(reverse("demo:index"))
        self.pass_middleware(request)
        self.assertFalse(request.META.get("REMOTE_USER"))
