from django.contrib import admin

from .models import (
    Movie,
    Theatre,
    Screen,
    Show,
    Seat,
)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "language",
        "duration",
    )

    list_filter = (
        "language",
    )

    search_fields = (
        "title",
    )


@admin.register(Theatre)
class TheatreAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "location",
    )

    search_fields = (
        "name",
        "location",
    )


@admin.register(Screen)
class ScreenAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "theatre",
        "id",
    )

    list_filter = (
        "theatre",
    )


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):

    list_display = (
        "movie",
        "screen",
        "show_date",
        "show_time",
        "platinum_price",
        "first_class_price",
        "second_class_price",
    )

    list_filter = (
        "show_date",
        "screen",
    )


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):

    list_display = (
        "seat_name",
        "screen",
        "seat_class",
        "is_active",
    )

    list_filter = (
        "screen",
        "seat_class",
        "is_active",
    )

    search_fields = (
        "row",
    )


    def seat_name(
        self,
        obj
    ):

        return (
            f"{obj.row}"
            f"{obj.number}"
        )

    seat_name.short_description = "Seat"