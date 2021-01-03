from debug_toolbar.panels import Panel

from windows_auth.ldap import _ldap_connections


class LDAPPanel(Panel):
    title = "LDAP Connection Usage Metrics"
    nav_title = "LDAP Metrics"
    template = "windows_auth/panel.html"
    has_content = True

    def generate_stats(self, request, response):
        # TODO merge similar operations
        self.record_stats({
            "domains": {
                domain: {
                    "usage": manager.get_usage(),
                    "operations": manager.get_operation_history(),
                }
                for domain, manager in _ldap_connections.items()
            }
        })
