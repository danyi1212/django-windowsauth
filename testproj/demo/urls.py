from django.urls import path

from demo.views import IndexView, ComputersView

app_name = "demo"
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("computers/", ComputersView.as_view(), name="computers"),
]
