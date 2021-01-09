"""
Django settings for testproj project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from dataclasses import dataclass
from pathlib import Path

from ldap3.utils.log import set_library_log_detail_level, BASIC, EXTENDED

from windows_auth.settings import LDAPSettings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^u%bv67^*p%@ww^gapg-p8_y$gs+9%ixm5n++_%vf#%ephf6ve'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "example.local",
]

# Application definition

INSTALLED_APPS = [
    # Django Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third Party Apps
    'windows_auth',
    'windows_auth.ldap_metrics',
    'debug_toolbar',

    # Project Apps
    'demo',
]

MIDDLEWARE = [
    'demo.middleware.FakeRemoteUserMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'windows_auth.middleware.UserSyncMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    "windows_auth.backends.WindowsAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

ROOT_URLCONF = 'testproj.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'testproj.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(os.path.join(BASE_DIR, "db.sqlite3")),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': "INFO",
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 2 ** 20 * 100,  # 100MB
            'backupCount': 10,
            'filename': BASE_DIR / 'logs' / 'debug.log',
        },
        'ldap': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 2 ** 20 * 100,  # 100MB
            'backupCount': 10,
            'filename': BASE_DIR / 'logs' / 'ldap.log',
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'wauth': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'formatter': 'simple',
            'propagate': True,
        },
        'ldap3': {
            'handlers': ['console', 'ldap'],
            'level': 'INFO',
            'propagate': False,
        }
    },
}

set_library_log_detail_level(BASIC)


# Debug Toolbar
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda r: True,
}
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.history.HistoryPanel',
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
    'windows_auth.panels.LDAPPanel',
]

# WAUTH_RESYNC_DELTA = True
WAUTH_REQUIRE_RESYNC = False
# WAUTH_USE_CACHE = True


@dataclass()
class MyLDAPSettings(LDAPSettings):
    USE_SSL: bool = False
    EXTRA_SETTING: str = "Hello, world!"


WAUTH_DOMAINS = {
    "EXAMPLE": MyLDAPSettings(
        SERVER="example.local",
        SEARCH_BASE="DC=example,DC=local",
        USERNAME="EXAMPLE\\django_sync",
        PASSWORD="Aa123456!",
        SUPERUSER_GROUPS=None,
        COLLECT_METRICS=True,
        READ_ONLY=False,
        # USER_QUERY_FIELD="email",
        GROUP_MAP={
            "demo": "Domain Admins",
            "demo2": "Domain Admins",
        },
    ),
    # "EXAMPLE": {
    #         "SERVER": "example.local",
    #         "SEARCH_BASE": "DC=example,DC=local",
    #         "USERNAME": lambda domain: f"{domain}\\django_sync",
    #         "PASSWORD": "Aa123456!",
    #         "USE_SSL": False,
    #         "BLABLABLA": True,
    #     },
}
