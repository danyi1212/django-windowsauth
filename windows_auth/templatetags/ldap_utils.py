from re import finditer

from django import template


register = template.Library()


@register.filter()
def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return " ".join(m.group(0) for m in matches)


@register.filter()
def ldap_scope_label(value):
    # docs https://ldapwiki.com/wiki/LDAP%20Search%20Scopes
    return (
        "Base Object",
        "Single Level",
        "Whole Subtree",
        "Subordinate Subtree",
    )[int(value)]


@register.filter()
def ldap_dereference_alias_label(value):
    # docs https://ldapwiki.com/wiki/Dereference%20Policy
    return (
        "Never Dereference Aliases",
        "Dereference In Searching",
        "Dereference Finding Base Object",
        "Always Dereference",
    )[int(value)]


@register.filter()
def filter_response(value):
    for entry in value:
        if "dn" in entry:
            yield entry
