from django import forms

from windows_auth.ldap import get_ldap_manager


class ComputerDescriptionForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField()

    _reader = None

    def get_reader(self):
        if not self._reader:
            manager = get_ldap_manager("EXAMPLE")
            self._reader = manager.get_reader("computer", f"name: {self.data.get('name')}")

        return self._reader

    def is_valid(self):
        return len(self.get_reader().search()) > 0
