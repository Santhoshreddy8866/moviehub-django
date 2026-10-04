from django.core.management.base import (
    BaseCommand
)

from movies.models import (
    Screen,
    Seat
)


class Command(BaseCommand):

    help = (
        "Generate complete theatre "
        "seat layout for a screen"
    )


    def add_arguments(
        self,
        parser
    ):

        parser.add_argument(
            "screen_id",
            type=int
        )


    def handle(
        self,
        *args,
        **options
    ):

        screen_id = (
            options["screen_id"]
        )


        try:

            screen = Screen.objects.get(
                id=screen_id
            )

        except Screen.DoesNotExist:

            self.stdout.write(
                self.style.ERROR(
                    "Screen not found."
                )
            )

            return


        # ---------------------------------------
        # Disable existing layout first.
        #
        # This prevents old seats from appearing
        # if layout is changed later.
        # ---------------------------------------

        Seat.objects.filter(
            screen=screen
        ).update(
            is_active=False
        )


        created_count = 0
        updated_count = 0


        # =======================================
        # PLATINUM
        #
        # Rows A B
        #
        # 8 seats
        #
        # 1 2 3 4   |   5 6 7 8
        # =======================================

        for row in [
            "A",
            "B"
        ]:

            for number in range(
                1,
                9
            ):

                seat, created = (
                    Seat.objects.update_or_create(

                        screen=screen,

                        row=row,

                        number=number,

                        defaults={

                            "seat_class":
                                "PLATINUM",

                            "aisle_after":
                                number == 4,

                            "is_active":
                                True,
                        }
                    )
                )

                if created:
                    created_count += 1

                else:
                    updated_count += 1


        # =======================================
        # FIRST CLASS
        #
        # C D E F
        #
        # 12 seats
        #
        # 1-4 | 5-8 | 9-12
        # =======================================

        for row in [
            "C",
            "D",
            "E",
            "F"
        ]:

            for number in range(
                1,
                13
            ):

                seat, created = (
                    Seat.objects.update_or_create(

                        screen=screen,

                        row=row,

                        number=number,

                        defaults={

                            "seat_class":
                                "FIRST",

                            "aisle_after":
                                number in [
                                    4,
                                    8
                                ],

                            "is_active":
                                True,
                        }
                    )
                )

                if created:
                    created_count += 1

                else:
                    updated_count += 1


        # =======================================
        # SECOND CLASS
        #
        # G H I J
        #
        # 14 seats
        #
        # 1-5 | 6-10 | 11-14
        # =======================================

        for row in [
            "G",
            "H",
            "I",
            "J"
        ]:

            for number in range(
                1,
                15
            ):

                seat, created = (
                    Seat.objects.update_or_create(

                        screen=screen,

                        row=row,

                        number=number,

                        defaults={

                            "seat_class":
                                "SECOND",

                            "aisle_after":
                                number in [
                                    5,
                                    10
                                ],

                            "is_active":
                                True,
                        }
                    )
                )

                if created:
                    created_count += 1

                else:
                    updated_count += 1


        active_total = (
            Seat.objects.filter(
                screen=screen,
                is_active=True
            ).count()
        )


        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Seat generation completed."
            )
        )

        self.stdout.write(
            f"Screen: {screen}"
        )

        self.stdout.write(
            f"Active seats: "
            f"{active_total}"
        )

        self.stdout.write(
            f"New seats: "
            f"{created_count}"
        )

        self.stdout.write(
            f"Updated seats: "
            f"{updated_count}"
        )