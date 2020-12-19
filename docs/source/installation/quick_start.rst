Quick Start
===========

#. Install with ``pip install django-windowsauth``
#. Run ``py manage.py migrate windows_auth``
#. Add "fastcgi application" with ``wfastcgi-enable``
#. Configure project settings:

   .. code-block:: python

      INSTALLED_APPS = [
         "windows_auth",
      ]

      MIDDLEWARE = [
          'django.contrib.auth.middleware.AuthenticationMiddleware',
          'django.contrib.auth.middleware.RemoteUserMiddleware',
          'windows_auth.middleware.UserSyncMiddleware',
      ]

      AUTHENTICATION_BACKENDS = [
          "windows_auth.backends.WindowsAuthBackend",
          "django.contrib.auth.backends.ModelBackend",
      ]

      WAUTH_DOMAINS = {
          "<your domain's NetBIOS Name> (EXAMPLE)": {
              "SERVER": "<domain FQDN> (example.local)",
              "SEARCH_BASE": "<search base> (DC=example,DC=local)",
              "USERNAME": "<bind account username>",
              "PASSWORD": "<bind account password>",
          }
      }

      # optional
      STATIC_URL = '/static/'
      STATIC_ROOT = BASE_DIR / "static"

      MEDIA_URL = '/media/'
      MEDIA_ROOT = BASE_DIR / "media"

#. Generate **web.config** files with ``py manage.py createwebconfig -s -m -w``.
#. Create new IIS Website from the project files
