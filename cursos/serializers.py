from rest_framework import serializers

from .models import Curso


class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ["id", "nombre", "descripcion", "profesor", "fecha_inicio"]
        read_only_fields = ["id"]

    def validate_nombre(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError(
                "El nombre debe tener al menos 3 caracteres."
            )
        return value

    def validate_profesor(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("El profesor no puede estar vacío.")
        return value
