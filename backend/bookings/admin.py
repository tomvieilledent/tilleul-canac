from django.contrib import admin

from .models import Booking, ExternalBlock


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("guest_name", "email", "stay", "status", "hold_until", "created_at")
    list_filter = ("status",)
    search_fields = ("guest_name", "email", "phone")
    readonly_fields = ("id", "created_at", "stripe_payment_intent_id")
    actions = ("mark_confirmed", "mark_cancelled")

    @admin.action(description="Marquer comme confirmée")
    def mark_confirmed(self, request, queryset):
        updated = queryset.update(status=Booking.Status.CONFIRMED)
        self.message_user(request, f"{updated} réservation(s) confirmée(s).")

    @admin.action(description="Marquer comme annulée")
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status=Booking.Status.CANCELLED)
        self.message_user(request, f"{updated} réservation(s) annulée(s).")


@admin.register(ExternalBlock)
class ExternalBlockAdmin(admin.ModelAdmin):
    list_display = ("source", "stay", "summary", "synced_at")
    list_filter = ("source",)
    search_fields = ("uid", "summary")
    readonly_fields = ("source", "uid", "stay", "summary", "synced_at")

    def has_add_permission(self, request):
        return False
