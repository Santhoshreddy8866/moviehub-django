from django.contrib import admin
from .models import Booking, BookingSeat, OTPVerification

admin.site.register(Booking)
admin.site.register(BookingSeat)
admin.site.register(OTPVerification)