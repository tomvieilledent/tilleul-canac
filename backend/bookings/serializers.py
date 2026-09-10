from datetime import date

from rest_framework import serializers

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    check_in = serializers.SerializerMethodField()
    check_out = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = (
            "id",
            "guest_name",
            "email",
            "phone",
            "status",
            "check_in",
            "check_out",
            "hold_until",
            "created_at",
        )

    def get_check_in(self, obj):
        return obj.stay.lower

    def get_check_out(self, obj):
        return obj.stay.upper


class BookingCreateSerializer(serializers.Serializer):
    guest_name = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=40, required=False, allow_blank=True)
    check_in = serializers.DateField()
    check_out = serializers.DateField()

    def validate(self, data):
        if data["check_out"] <= data["check_in"]:
            raise serializers.ValidationError(
                "La date de départ doit être postérieure à la date d'arrivée."
            )
        if data["check_in"] < date.today():
            raise serializers.ValidationError("La date d'arrivée est dans le passé.")
        return data
