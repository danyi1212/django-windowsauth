from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, HttpRequest
from django.utils import timezone

from windows_auth import logger
from windows_auth.conf import wauth_settings
from windows_auth.models import LDAPUser


class UserSyncMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Check and re-sync user against LDAP.
        :param request: HTTP Request
        :return: HTTP Response
        """

        if (request.user and request.user.is_authenticated
                and LDAPUser.objects.filter(user=request.user).exists() and wauth_settings.WAUTH_RESYNC_DELTA not in (None, False)):
            try:
                # convert timeout to seconds
                if isinstance(wauth_settings.WAUTH_RESYNC_DELTA, timezone.timedelta):
                    timeout = wauth_settings.WAUTH_RESYNC_DELTA.total_seconds()
                else:
                    timeout = int(wauth_settings.WAUTH_RESYNC_DELTA)

                ldap_user = LDAPUser.objects.get(user=request.user)

                if wauth_settings.WAUTH_USE_CACHE:
                    # if cache does not exist
                    cache_key = f"wauth_resync_user_{ldap_user.user.id}"
                    if not cache.get(cache_key):
                        ldap_user.sync()

                        # create new cache key
                        cache.set(cache_key, True, timeout)
                else:
                    # check via database query
                    if not ldap_user.last_sync or ldap_user.last_sync < timezone.now() - timezone.timedelta(seconds=timeout):
                        ldap_user.sync()
            except LDAPUser.DoesNotExist:
                # user is getting created the first time
                pass
            except Exception as e:
                logger.exception(f"Failed to synchronize user {request.user} against LDAP")
                # return error response
                if wauth_settings.WAUTH_REQUIRE_RESYNC:
                    if isinstance(wauth_settings.WAUTH_ERROR_RESPONSE, int):
                        return HttpResponse(f"Authorization Failed.", status=wauth_settings.WAUTH_ERROR_RESPONSE)
                    elif callable(wauth_settings.WAUTH_ERROR_RESPONSE):
                        return wauth_settings.WAUTH_ERROR_RESPONSE(request, e)
                    else:
                        raise e
        response = self.get_response(request)
        return response


class SimulateWindowsAuthMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if settings.DEBUG and not request.META.get("REMOTE_USER"):
            # Set remote user
            request.META['REMOTE_USER'] = wauth_settings.WAUTH_SIMULATE_USER
        return self.get_response(request)

