import json
from functools import wraps

from debug_toolbar.panels import Panel
from debug_toolbar.utils import ThreadCollector, tidy_stacktrace, get_stack, render_stacktrace
from debug_toolbar import settings as dt_settings
from django.utils import timezone
from django.utils.functional import cached_property
from ldap3.utils.conv import format_json

from windows_auth.ldap import _ldap_connections
from windows_auth.utils import camel_case_split


collector = ThreadCollector()


class OperationInfo:
    """
    Collected information about an LDAP Operation
    """

    def __init__(self, domain, response, result, request, start_time=None, end_time=None):
        self.domain = domain
        self.request = request
        self.result = result
        self.response = response
        self.start_time = start_time
        self.end_time = end_time

        if dt_settings.get_config()['ENABLE_STACKTRACES']:
            # cut the first 6 lines, exactly until the original operation call
            self.raw_stacktrace = tidy_stacktrace(reversed(get_stack()[6:]))
        else:
            self.raw_stacktrace = []
            
    @cached_property
    def title(self) -> str:
        req_type = self.request.get("type")
        if req_type == "searchRequest":
            return self.request.get("filter")
        elif req_type in ("modifyRequest", "addRequest", "delRequest", "compareRequest"):
            return self.request.get("entry")
        else:
            return self.request

    @cached_property
    def raw_request(self) -> str:
        return json.dumps(dict(self.request), indent=4)

    @cached_property
    def raw_result(self) -> str:
        return json.dumps(dict(self.result), indent=4)

    @cached_property
    def stacktrace(self) -> str:
        return render_stacktrace(self.raw_stacktrace)

    @cached_property
    def time_elapsed(self) -> timezone.timedelta:
        return self.end_time - self.start_time

    @cached_property
    def entries(self) -> list:
        result = []
        for entry in self.response:
            if entry.get("type") not in ("searchResRef", ):
                # entry json serialization
                try:
                    if entry.get("type") == "searchResEntry":
                        entry["json"] = json.dumps({
                            "dn": entry.get("dn"),
                            "type": entry.get("type"),
                            "attributes": dict(entry.get("attributes"))
                        }, indent=4, default=format_json)
                    else:
                        entry["json"] = json.dumps(entry, indent=4, default=format_json)
                except TypeError:
                    entry["json"] = "Failed to serialize entry"

                # template
                if entry.get("type") == "searchResEntry":
                    entry["template"] = "windows_auth/search_entry.html"
                elif entry.get("type") in ("modifyResponse", "addResponse", "delResponse", "modDNResponse"):
                    entry["template"] = "windows_auth/modify_entry.html"
                else:
                    entry["template"] = "windows_auth/entry_base.html"

                result.append(entry)

        return result

    @cached_property
    def entry_count(self) -> int:
        return len(self.entries)

    @cached_property
    def result_description(self) -> str:
        return camel_case_split(self.result.get("description")).title()

    @cached_property
    def type_label(self) -> str:
        return camel_case_split(self.request.get("type")).title()

    @cached_property
    def type_icon(self) -> str:
        return {
            "bindRequest": "🔗",
            "unbindRequest": "🛑",
            "searchRequest": "🔍",
            "modifyRequest": "🖊",
            "modDNRequest": "📦",
            "addRequest": "➕",
            "delRequest": "🗑️",
            "compareRequest": "⚖",
            "extendedReq": "❔",
            "abandonRequest": "❌",
        }[self.request.get("type")]

    @cached_property
    def status_icon(self) -> str:
        if self.result.get("result") == 0:
            return "✅"
        else:
            return "❌"

    @cached_property
    def scope_label(self) -> str:
        """
        Display value for scope
        """
        # docs https://ldapwiki.com/wiki/LDAP%20Search%20Scopes
        return (
            "Base Object",
            "Single Level",
            "Whole Subtree",
            "Subordinate Subtree",
        )[self.request.get("scope")] if "scope" in self.request else ""

    @cached_property
    def dereference_alias_label(self) -> str:
        """
        Display value for dereferenceAlias
        """
        # docs https://ldapwiki.com/wiki/Dereference%20Policy
        return (
            "Never Dereference Aliases",
            "Dereference In Searching",
            "Dereference Finding Base Object",
            "Always Dereference",
        )[self.request.get("dereferenceAlias")] if "dereferenceAlias" in self.request else ""

    @cached_property
    def details_template(self) -> str:
        """
        HTML template path for entry details
        """
        req_type = self.request.get("type")
        if req_type == "searchRequest":
            return "windows_auth/search_details.html"
        elif req_type in ("modifyRequest", "addRequest", "delRequest", "compareRequest"):
            return "windows_auth/modify_details.html"
        else:
            return "windows_auth/details_base.html"

    @cached_property
    def change_labels(self) -> list:
        """
        Describe change in a sentence
        """
        changes = []
        for change in self.request.get("changes"):
            operation = change.get("operation")
            attribute = change.get("attribute").get("type")
            value = change.get("attribute").get("value")
            # docs https://ldap.com/ldapv3-wire-protocol-reference-modify/
            if operation == 0:
                changes.append(f"Add <strong>{value}</strong>  to <strong>{attribute}</strong> ")
            elif operation == 1:
                changes.append(f"Delete <strong>{value}</strong>  from <strong>{attribute}</strong> ")
            elif operation == 2:
                changes.append(f"Replace <strong>{attribute}</strong>  to <strong>{value}</strong> ")
            else:
                changes.append(f"Unknown operation on <strong>{attribute}</strong> with <strong>{value}</strong> ")

        return changes


def get_response_decorator(func, domain: str):

    @wraps(func)
    def wrapper(message_id, timeout=None, get_request=False):
        start_time = timezone.now()
        # always ask for request too
        response, result, request = func(message_id, timeout=timeout, get_request=True)

        collector.collect(OperationInfo(
            domain,
            response,
            result,
            request,
            start_time=start_time,
            end_time=timezone.now(),
        ))

        # mimic the original logic about get_request
        if get_request:
            return response, result, request
        else:
            return response, result

    wrapper.original = func
    return wrapper


class LDAPPanel(Panel):
    title = "LDAP Connection Tracing"
    nav_title = "LDAP"
    template = "windows_auth/panel.html"
    has_content = True

    def enable_instrumentation(self):
        # wrap LDAP connection strategy's get_response to collect operation info
        for domain, manager in _ldap_connections.items():
            strategy = manager.connection.strategy
            strategy.get_response = get_response_decorator(strategy.get_response, domain)

    def disable_instrumentation(self):
        # unwrap the connection
        for domain, manager in _ldap_connections.items():
            strategy = manager.connection.strategy
            if hasattr(strategy.get_response, "original"):
                strategy.get_response = strategy.get_response.original

    def generate_stats(self, request, response):
        self.record_stats({
            "domains": {
                domain: {
                    "manager": manager,
                    "usage": manager.get_usage(),
                    "operations": collector.get_collection(),
                }
                for domain, manager in _ldap_connections.items()
            }
        })
        # reserve LDAP operations from unsuccessful requests or non GET requests
        if request.method == "GET" and response.status_code < 300:
            collector.clear_collection()
