from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("cursos", views.CursoViewSet, basename="curso")

urlpatterns = [
    path("token/", views.LoginTokenView.as_view(), name="token"),
    path("token/revoke/", views.RevokeTokenView.as_view(), name="token-revoke"),
    path("", include(router.urls)),
]
