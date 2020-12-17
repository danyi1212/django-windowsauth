
Installation and Setup
=================

| This is a **detailed** walk-through the *django-windowsauth* installation and setup process.
| For easy and quick installation please refer to the :doc:`quick_start` guide.

Install and Setup IIS
---------------------

1. IIS with the default + following features:
   ([See the docs](http://www.iis.net/learn/install))
    2. Application / CGI
    3. Security / Windows Authentication
    4. (suggested) Performance Features / Dynamic Content Compression
    5. (suggested) Health and Diagnostics / Request Monitor
    6. (suggested) Health and Diagnostics / Tracing
2. Unlock handlers configuration
    1. Open IIS Manager > Configuration Editor
    2. Select section ``system.webServer/handlers``
    3. Click ``Unlock section`` on the right sidebar.
    4. Repeat for sections ``system.webServer/security/authentication/anonymousAuthentication`` and ``system.webServer/security/authentication/windowsAuthentication``.

.. Note::
    | Those instruction are provided as "Best Practices" advice, your setup may vary.
    | For more information visit the IIS Topic on Microsoft Docs: https://docs.microsoft.com/en-us/iis

.. todo: rewrite section

Getting it
----------
You can get django-windowsauth by using pip::

 $ pip install django-windowsauth

If you want to install it from source, grab the git repository and run setup.py::

 $ git clone https://github.com/danyi1212/django-windowsauth.git
 $ python setup.py install

Installing
----------

You will need to add the ``windows_auth`` application to the INSTALLED_APPS setting in you Django project settings file.

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'windows_auth',
        ...
    ]

This will allow to execute the ``createwebconfig`` command, add the new model *LDAPUer* and register it's Django Admin page.

Next, you will need to run the ``migrate`` management command to create the new SQL table of the new models.::

$ py manage.py migrate windows_auth

.. note::
    This will perform migrations only for **windows_auth** app.
    If you have other migrations pending, you may want to omit the **windows_auth** argument to perform all available migrations.

Configure
---------

In order to receive correctly the authenticated user from the **IIS Windows Authentication**, you will need to add a middleware called ``RemoteUserMiddleware``.
This middleware must be after ``AuthenticationMiddleware``, that is usually provided by default with Django's ``startproject`` template.

.. code-block:: python

    MIDDLEWARE = [
        ...
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.RemoteUserMiddleware',
        ...
    ]

To process the information passed from the **IIS Windows Authentication** and translate it into a **Django User**, you will need to specify the ``WindowsAuthBackend`` authentication backend.

.. code-block:: python

    AUTHENTICATION_BACKENDS = [
        'windows_auth.backends.WindowsAuthBackend',
        'django.contrib.auth.backends.ModelBackend',
    ]

.. note::
    Be aware, this configuration keeps the Django's default **ModelBackend** in order to allow for fallback to **Django Native Users**.
    It can be used to authenticate without IIS, when using the ``runserver`` management command for example.

    This is usually not advised to configure for **Production** setups, but only for **Development**.

.. seealso:: Django documentation about *Authenticating using REMOTE_USER* https://docs.djangoproject.com/en/3.1/howto/auth-remote-user/

Next you will need to configure the settings for your **Domain** to allow for LDAP integration with **Active Directory**.

.. code-block:: python

    WAUTH_DOMAINS = {
       "EXAMPLE": {  # this is your domain's NetBIOS Name, same as in "EXAMPLE\\username" login scheme
           "SERVER": "example.local",  # the FQDN of the DC server, usually is the FQDN of the domain itself
           "SEARCH_BASE": "DC=example,DC=local",  # the default Search Base to use when searching
           "USERNAME": "EXAMPLE\\bind_account",  # username of the account used to authenticate your Django project to Active Directory
           "PASSWORD": "<super secret>",  # password for the binding account
       }
   }

.. TODO link to setting reference

.. seealso:: About LDAP Search Base: https://docs.microsoft.com/en-us/windows/win32/ad/binding-to-a-search-start-point

(optionally) Configure **file path** and **url path** settings for your ``static`` and ``media`` files.

.. code-block:: python

    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / "static"

    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / "media"

You may need to execute ``$ py manage.py collectstatic`` management command after modifying the ``STATIC_ROOT`` setting.

.. seealso:: Full how-to guide for Serving Static Files though IIS

.. TODO link to how-to guide

Publish to IIS
--------------

First, we will need to create the ``web.config`` files for the IIS Website configuration.
This can be done simply by running the management command:::

$ py manage.py createwebconfig -s -m -w

Notice the ``-s`` and ``-m`` switches, those are to add configurations for **Serving Static Files though IIS**.
You may want to omit those switches if you are not planning to serve static files though IIS.

The ``-w`` parameter configures IIS's ``Windows Authentication`` and disables ``Anonymous Authentication`` in the ``web.config`` file.
You may want to change those settings manually to avoid **unlocking those configuration sections**.

.. seealso:: Reference for the ``createwebconfig`` management command

.. todo link to createwebconfig reference

Next you will need to create a new IIS Website for your Django Project

.. TODO how to create IIS Website

## Setup Windows Authentication
1. Open IIS Manager > *Your Website* > Authentication
2. Enable "Windows Authe 1. Open IIS Manager > *Your Website* > Authentication
2. Enable "Windows Authentication" and Disable "Anonymous
   Authentication"ntication" and Disable "Anonymous
   Authentication"

