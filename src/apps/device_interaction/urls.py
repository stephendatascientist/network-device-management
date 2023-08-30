from django.urls import path

from .views import (
    ConfigureLoopbackView,
    DeleteLoopbackView,
    ListInterfaceView,
    DryRunConfigView,
)

urlpatterns = [
    path("configure-dry-run/", DryRunConfigView.as_view(), name="configure-dry-run"),
    path("interfaces/", ListInterfaceView.as_view(), name="list-interfaces"),
    path(
        "configure-loopback/",
        ConfigureLoopbackView.as_view(),
        name="configure-loopback",
    ),
    path(
        "delete-loopback/<str:loopback_number>/",
        DeleteLoopbackView.as_view(),
        name="delete-loopback",
    ),
]
