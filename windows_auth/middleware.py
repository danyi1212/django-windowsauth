from django.core.cache import cache
from django.http import HttpResponse
from django.utils import timezone

from windows_auth import logger
from windows_auth.conf import WAUTH_RESYNC_DELTA, WAUTH_USE_CACHE, WAUTH_REQUIRE_RESYNC, WAUTH_ERROR_RESPONSE
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
                and request.user.ldap and WAUTH_RESYNC_DELTA not in (None, False)):
            try:
                # convert timeout to seconds
                if isinstance(WAUTH_RESYNC_DELTA, timezone.timedelta):
                    timeout = WAUTH_RESYNC_DELTA.total_seconds()
                else:
                    timeout = int(WAUTH_RESYNC_DELTA)

                ldap_user = LDAPUser.objects.get(user=request.user)

                if WAUTH_USE_CACHE:
                    # if cache does not exist
                    cache_key = f"wauth_resync_user_{ldap_user.user.id}"
                    if not cache.get(cache_key):
                        ldap_user.sync()

                        # create new cache key
                        cache.set(cache_key, True, timeout)
                else:
                    # check via database query
                    if ldap_user.last_sync < timezone.now() - timezone.timedelta(seconds=timeout):
                        ldap_user.sync()
            except LDAPUser.DoesNotExist:
                # user is getting created the first time
                pass
            except Exception as e:
                logger.exception(f"Failed to synchronize user {request.user} against LDAP")
                # return error response
                if WAUTH_REQUIRE_RESYNC:
                    if isinstance(WAUTH_ERROR_RESPONSE, int):
                        return HttpResponse(f"Authorization Failed.", status=WAUTH_ERROR_RESPONSE)
                    elif callable(WAUTH_ERROR_RESPONSE):
                        return WAUTH_ERROR_RESPONSE(request, e)
                    else:
                        raise e

        response = self.get_response(request)
        return response
