# django-windowsauth

[![Documentation Status](https://readthedocs.org/projects/django-windowsauth/badge/?version=latest)](https://django-windowsauth.readthedocs.io/en/latest/?badge=latest)

##### Easy integration and deployment of Django projects into Windows Environments.
Documentation is available at [https://django-windowsauth.readthedocs.io/en/latest/](https://django-windowsauth.readthedocs.io/en/latest/)

#### Features
- Deploy to **Microsoft IIS** quickly using [wfastcgi](https://pypi.org/project/wfastcgi/)
- Authenticate via [IIS's Windows Authentication](https://docs.microsoft.com/en-us/iis/configuration/system.webserver/security/authentication/windowsauthentication/#:~:text=You%20can%20use%20Windows%20authentication,Windows%20accounts%20to%20identify%20users.&text=When%20you%20install%20and%20enable,the%20default%20protocol%20is%20Kerberos.)
- Authorize against **Active Directory** using [ldap3](https://ldap3.readthedocs.io/en/latest/) package
- Manage **LDAP Connections** for easy integrations
- (Coming soon) Integration with [django-debug-toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/)

## Quick Start
1. Install with `pip install django-windowsauth`
2. Run `py manage.py migrate windows_auth`
3. Add "fastcgi application" with `wfastcgi-enable`
4. Configure project settings
    ```python
    INSTALLED_APPS = [
       "windows_auth",
   ]
   
   MIDDLEWARE = [
       'django.contrib.auth.middleware.AuthenticationMiddleware',
       'django.contrib.auth.middleware.RemoteUserMiddleware',
   ]
   
   AUTHENTICATION_BACKENDS = [
       "windows_auth.backends.WindowsAuthBackend",
       "django.contrib.auth.backends.ModelBackend",
   ]
   
   WAUTH_DOMAINS = {
       "<your domain's NetBIOS Name> (EXAMPLE)": {
           "SERVER": "<domain FQDN> (example.local)",
           "SEARCH_SCOPE": "<search scope> (DC=example,DC=local)",
           "USERNAME": "<bind account username>",
           "PASSWORD": "<bind account password>",
       }
   }
   
   # optional
   STATIC_URL = '/static/'
   STATIC_ROOT = BASE_DIR / "static"
    
   MEDIA_URL = '/media/'
   MEDIA_ROOT = BASE_DIR / "media"
    ```
5. Generate **web.config** files with `py manage.py createwebconfig -s -m`
6. Create new IIS Website from the project files
<!--TODO script to add IIS website-->

For more details visit the docs for installation:
<!--TODO-->

## Prerequisites
1. IIS with the default + following features:
   ([See the docs](http://www.iis.net/learn/install))
    2. Application / CGI Easy integration and deployment of Django projects into Windows Systems.
    3. Security / Windows Authentication
    4. (suggested) Performance Features / Dynamic Content Compression
    5. (suggested) Health and Diagnostics / Request Monitor
    6. (suggested) Health and Diagnostics / Tracing
2. Unlock handlers configuration
   1. Open IIS Manager > Configuration Editor
   2. Select section ``system.webServer/handlers``
   3. Click ``Unlock section`` on the right sidebar


## Getting help

In case you have trouble while using this module, you can use
<!--TODO link to StackOverflow Tag-->

For any bug or issue, see how to create a GitHub Issue


## Contributing


<!--TODO-->