import atexit

from django.apps import AppConfig


class LdapMetricsConfig(AppConfig):
    name = 'windows_auth.ldap_metrics'
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        from windows_auth.ldap_metrics.utils import collect_metrics
        atexit.register(collect_metrics)
