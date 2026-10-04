from django.urls import path
from . import views


urlpatterns = [

    path(
        "show/<int:show_id>/",
        views.select_seats,
        name="select_seats"
    ),

    path(
        "summary/<int:booking_id>/",
        views.booking_summary,
        name="booking_summary"
    ),

    path(
        "verify/<int:booking_id>/",
        views.verify_otp,
        name="verify_otp"
    ),

    path(
        "success/<int:booking_id>/",
        views.booking_success,
        name="booking_success"
    ),
    path(
    "my-bookings/",
    views.my_bookings,
    name="my_bookings"
),

]