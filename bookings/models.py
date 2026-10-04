from django.db import models
from django.contrib.auth.models import User

from movies.models import (
    Show,
    Seat
)


# ==========================================================
# BOOKING
# ==========================================================

class Booking(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    show = models.ForeignKey(
        Show,
        on_delete=models.CASCADE
    )

    total_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.user.username} - "
            f"{self.show} - "
            f"{self.status}"
        )


# ==========================================================
# BOOKING SEATS
# ==========================================================

class BookingSeat(models.Model):

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="booking_seats"
    )

    seat = models.ForeignKey(
        Seat,
        on_delete=models.CASCADE
    )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "booking",
                    "seat"
                ],
                name="unique_booking_seat"
            )

        ]

    def __str__(self):

        return (
            f"{self.booking.id} - "
            f"{self.seat}"
        )


# ==========================================================
# OTP
# ==========================================================

class OTPVerification(models.Model):

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE
    )

    otp = models.CharField(
        max_length=6
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    def __str__(self):

        return (
            f"OTP - Booking "
            f"{self.booking.id}"
        )


# ==========================================================
# TEMPORARY SEAT HOLD
# ==========================================================

class SeatHold(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    show = models.ForeignKey(
        Show,
        on_delete=models.CASCADE
    )

    seat = models.ForeignKey(
        Seat,
        on_delete=models.CASCADE
    )

    expires_at = models.DateTimeField()


    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "show",
                    "seat"
                ],
                name="unique_show_seat_hold"
            )

        ]


    def __str__(self):

        return (
            f"{self.show} - "
            f"{self.seat}"
        )