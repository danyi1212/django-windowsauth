from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from ldap3 import Writer

from demo.forms import ComputerDescriptionForm
from windows_auth.ldap import get_ldap_manager


class IndexView(TemplateView):
    template_name = "demo/index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context["remote_user"] = self.request.META.get('REMOTE_USER')
        return context


class ComputersView(FormView):
    template_name = "demo/computers.html"
    form_class = ComputerDescriptionForm
    success_url = reverse_lazy("demo:computers")

    def get_context_data(self, **kwargs):
        context = super(ComputersView, self).get_context_data(**kwargs)
        manager = get_ldap_manager("EXAMPLE")
        reader = manager.get_reader("computer", attributes=("name", "description"))
        context["computers"] = reader.search()
        return context

    def form_valid(self, form: ComputerDescriptionForm):
        # write new description
        reader = form.get_reader()
        writer = Writer.from_cursor(reader)
        computer = writer[0]
        computer.description = form.data["description"]
        writer.commit()
        return super(ComputersView, self).form_valid(form)
