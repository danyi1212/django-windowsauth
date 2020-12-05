from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "demo/index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context["remote_user"] = self.request.META.get('REMOTE_USER')
        return context

