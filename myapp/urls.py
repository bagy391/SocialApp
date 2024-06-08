from django.urls import path, include
from rest_framework.routers import DefaultRouter

from myapp import views

router = DefaultRouter()
router.register("users", views.UserViewSet, "users")
router.register("request", views.RequestViewSet, "request")


urlpatterns = [
    path("", include(router.urls)),
]
