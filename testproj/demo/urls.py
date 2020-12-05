from django.urls import path

from demo.views import IndexView

app_name = "demo"
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
]
