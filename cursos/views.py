from rest_framework import status, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import Curso
from .serializers import CursoSerializer


class CursoViewSet(viewsets.ModelViewSet):
    """CRUD de cursos: GET (lista/detalle) público; POST, PUT, PATCH y DELETE con token."""

    queryset = Curso.objects.order_by("id")
    serializer_class = CursoSerializer


class LoginTokenView(ObtainAuthToken):
    """POST con username y password; devuelve el token. Limitado por la tasa "login"."""

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"


class RevokeTokenView(APIView):
    """DELETE elimina el token usado en la petición (cierre de sesión de la API)."""

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
