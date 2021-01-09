
View Decorators
===============

Provided with this module are some useful decorators to use on your views.
Those decorators can be used on function based view normally:

.. code-block:: python

    @domain_required
    def my_view(request):
        # ...

And for class-based view with the ``@method_decorator`` decorator

.. code-block:: python

    @method_decorator(domain_required, name='dispatch')
    class MyView(TemplateView):
        # ...

.. seealso::
    https://docs.djangoproject.com/en/3.1/topics/class-based-views/intro/#decorating-class-based-views

domain_required
---------------

Require that the logged on user has LDAP relation with a domain.
In case it is not, redirect to login page.

Parameters
    - **domain**: Check if is member in a specific domain (default: None)
    - **login_url**: Login page URL (default: None)
    - **bypass_superuser**: Allow superusers to bypass this requirement (default: True)

ldap_sync_required
------------------

Require the logged on user to be synced against LDAP.
This can be used to override the global ``WAUTH_REQUIRE_RESYNC`` and ``WAUTH_RESYNC_DELTA`` settings.

Parameters
    - **timedelta**: Maximum acceptable time since the last synchronization (default: None)
    - **login_url**: Login page URL (default: None)
    - **allow_non_ldap**: Allow non-LDAP users to access (default: True)
    - **raise_exception**: When sync fails, raise the exception and cause response status code 500 (default: False

.. warning::
    When configuring ``WAUTH_USE_CACHE`` to True, this decorator will re-sync the user in regards to the ``timedelta`` parameter
