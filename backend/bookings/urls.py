from django.urls import path

from . import views

urlpatterns = [
    path("availability", views.availability, name="availability"),
    path("bookings", views.create_booking, name="create-booking"),
    path("calendar.ics", views.calendar_ics, name="calendar-ics"),
    path("healthz", views.healthz, name="healthz"),
]
