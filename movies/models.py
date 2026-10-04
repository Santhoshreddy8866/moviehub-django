from django.db import models


class Movie(models.Model):

    LANGUAGE_CHOICES = [
        ("TELUGU", "Telugu"),
        ("ENGLISH", "English"),
        ("HINDI", "Hindi"),
    ]

    title = models.CharField(
        max_length=150
    )

    language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES
    )

    description = models.TextField(
        blank=True
    )

    poster = models.ImageField(
        upload_to="movies/",
        blank=True,
        null=True
    )

    duration = models.PositiveIntegerField(
        help_text="Duration in minutes"
    )

    def __str__(self):
        return self.title


# ==========================================================
# THEATRE
# ==========================================================

class Theatre(models.Model):

    name = models.CharField(
        max_length=150
    )

    location = models.CharField(
        max_length=150
    )

    def __str__(self):

        return (
            f"{self.name} - "
            f"{self.location}"
        )


# ==========================================================
# SCREEN
# ==========================================================

class Screen(models.Model):

    theatre = models.ForeignKey(
        Theatre,
        on_delete=models.CASCADE,
        related_name="screens"
    )

    name = models.CharField(
        max_length=50
    )

    def __str__(self):

        return (
            f"{self.theatre.name} - "
            f"{self.name}"
        )


# ==========================================================
# SHOW
# ==========================================================

class Show(models.Model):

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="shows"
    )

    screen = models.ForeignKey(
        Screen,
        on_delete=models.CASCADE,
        related_name="shows"
    )

    show_date = models.DateField()

    show_time = models.TimeField()


    # Separate class prices

    platinum_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=300
    )

    first_class_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=200
    )

    second_class_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=150
    )


    def get_price_for_class(
        self,
        seat_class
    ):

        if seat_class == "PLATINUM":
            return self.platinum_price

        if seat_class == "FIRST":
            return self.first_class_price

        return self.second_class_price


    def __str__(self):

        return (
            f"{self.movie.title} - "
            f"{self.show_date} - "
            f"{self.show_time}"
        )


# ==========================================================
# SEAT
# ==========================================================

class Seat(models.Model):

    SEAT_CLASS_CHOICES = [
        ("PLATINUM", "Platinum"),
        ("FIRST", "First Class"),
        ("SECOND", "Second Class"),
    ]

    screen = models.ForeignKey(
        Screen,
        on_delete=models.CASCADE,
        related_name="seats"
    )

    row = models.CharField(
        max_length=2
    )

    number = models.PositiveIntegerField()

    seat_class = models.CharField(
        max_length=20,
        choices=SEAT_CLASS_CHOICES,
        default="FIRST"
    )

    # Creates visual walking gap
    # after this seat
    aisle_after = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True
    )


    class Meta:

        ordering = [
            "row",
            "number"
        ]

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "screen",
                    "row",
                    "number"
                ],
                name="unique_screen_seat"
            )

        ]


    @property
    def label(self):

        return (
            f"{self.row}"
            f"{self.number}"
        )


    def __str__(self):

        return (
            f"{self.screen} - "
            f"{self.row}{self.number} - "
            f"{self.get_seat_class_display()}"
        )