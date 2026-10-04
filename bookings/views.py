import secrets

from collections import OrderedDict
from datetime import timedelta

from django.conf import settings

from django.contrib import messages

from django.contrib.auth.decorators import (
    login_required
)

from django.core.mail import send_mail

from django.db import (
    transaction,
    IntegrityError,
)

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.utils import timezone


from movies.models import (
    Show,
    Seat,
)

from .models import (
    Booking,
    BookingSeat,
    OTPVerification,
    SeatHold,
)


MAX_SEATS_PER_BOOKING = 6


# ==========================================================
# PRICE
# ==========================================================

def get_seat_price(
    show,
    seat
):

    return show.get_price_for_class(
        seat.seat_class
    )


# ==========================================================
# BUILD FRONTEND SEAT LAYOUT
# ==========================================================

def build_seat_sections(
    show,
    seats,
    booked_ids,
    held_ids,
    my_hold_ids
):

    sections = []


    class_configuration = [

        (
            "PLATINUM",
            "Platinum",
            show.platinum_price
        ),

        (
            "FIRST",
            "First Class",
            show.first_class_price
        ),

        (
            "SECOND",
            "Second Class",
            show.second_class_price
        ),

    ]


    for (
        class_code,
        class_name,
        class_price
    ) in class_configuration:


        class_seats = [

            seat

            for seat in seats

            if (
                seat.seat_class
                ==
                class_code
            )

        ]


        if not class_seats:
            continue


        rows = OrderedDict()


        for seat in class_seats:

            seat.current_price = (
                class_price
            )


            if seat.id in booked_ids:

                seat.status = (
                    "booked"
                )


            elif seat.id in held_ids:

                seat.status = (
                    "held"
                )


            elif seat.id in my_hold_ids:

                seat.status = (
                    "mine"
                )


            else:

                seat.status = (
                    "available"
                )


            if seat.row not in rows:

                rows[seat.row] = []


            rows[seat.row].append(
                seat
            )


        row_list = [

            {
                "name": row_name,
                "seats": row_seats,
            }

            for (
                row_name,
                row_seats
            )
            in rows.items()

        ]


        sections.append({

            "code":
                class_code,

            "name":
                class_name,

            "price":
                class_price,

            "rows":
                row_list,

        })


    return sections


# ==========================================================
# SELECT SEATS
# ==========================================================

@login_required
def select_seats(
    request,
    show_id
):

    show = get_object_or_404(
        Show,
        id=show_id
    )


    # Remove expired holds
    SeatHold.objects.filter(
        expires_at__lte=
        timezone.now()
    ).delete()


    seats = list(

        Seat.objects.filter(

            screen=show.screen,

            is_active=True

        ).order_by(
            "row",
            "number"
        )

    )


    booked_ids = set(

        BookingSeat.objects.filter(

            booking__show=show,

            booking__status=
            "CONFIRMED"

        ).values_list(
            "seat_id",
            flat=True
        )

    )


    other_hold_ids = set(

        SeatHold.objects.filter(

            show=show,

            expires_at__gt=
            timezone.now()

        ).exclude(

            user=request.user

        ).values_list(
            "seat_id",
            flat=True
        )

    )


    my_hold_ids = set(

        SeatHold.objects.filter(

            show=show,

            user=request.user,

            expires_at__gt=
            timezone.now()

        ).values_list(
            "seat_id",
            flat=True
        )

    )


    seat_sections = (
        build_seat_sections(

            show,

            seats,

            booked_ids,

            other_hold_ids,

            my_hold_ids
        )
    )


    # ======================================================
    # POST
    # ======================================================

    if request.method == "POST":

        selected_ids = (
            request.POST.getlist(
                "seats"
            )
        )


        if not selected_ids:

            messages.error(
                request,
                "Please select at least one seat."
            )

            return redirect(
                "select_seats",
                show_id=show.id
            )


        if (
            len(selected_ids)
            >
            MAX_SEATS_PER_BOOKING
        ):

            messages.error(
                request,
                "Maximum 6 seats can be booked at once."
            )

            return redirect(
                "select_seats",
                show_id=show.id
            )


        try:

            selected_ids = [

                int(seat_id)

                for seat_id
                in selected_ids
            ]

        except ValueError:

            messages.error(
                request,
                "Invalid seat selection."
            )

            return redirect(
                "select_seats",
                show_id=show.id
            )


        # Prevent duplicate POST IDs
        if (
            len(set(selected_ids))
            !=
            len(selected_ids)
        ):

            messages.error(
                request,
                "Invalid duplicate seat selection."
            )

            return redirect(
                "select_seats",
                show_id=show.id
            )


        selected_seats = list(

            Seat.objects.filter(

                id__in=
                selected_ids,

                screen=
                show.screen,

                is_active=True

            )

        )


        if (
            len(selected_seats)
            !=
            len(selected_ids)
        ):

            messages.error(
                request,
                "Invalid seat selection."
            )

            return redirect(
                "select_seats",
                show_id=show.id
            )


        try:

            with transaction.atomic():


                # -----------------------------------------
                # CONFIRMED SEAT CONFLICT
                # -----------------------------------------

                booked_conflict = (

                    BookingSeat.objects.filter(

                        booking__show=
                        show,

                        booking__status=
                        "CONFIRMED",

                        seat_id__in=
                        selected_ids

                    ).exists()

                )


                if booked_conflict:

                    messages.error(
                        request,
                        "One of those seats is already booked."
                    )

                    return redirect(
                        "select_seats",
                        show_id=show.id
                    )


                # -----------------------------------------
                # TEMPORARY HOLD CONFLICT
                # -----------------------------------------

                hold_conflict = (

                    SeatHold.objects.filter(

                        show=show,

                        seat_id__in=
                        selected_ids,

                        expires_at__gt=
                        timezone.now()

                    ).exclude(

                        user=request.user

                    ).exists()

                )


                if hold_conflict:

                    messages.error(
                        request,
                        "Another user is currently selecting one of those seats."
                    )

                    return redirect(
                        "select_seats",
                        show_id=show.id
                    )


                # -----------------------------------------
                # REMOVE USER'S PREVIOUS HOLD
                # -----------------------------------------

                SeatHold.objects.filter(

                    user=request.user,

                    show=show

                ).delete()


                hold_expiry = (

                    timezone.now()

                    +
                    timedelta(
                        minutes=5
                    )

                )


                # -----------------------------------------
                # HOLD NEW SEATS
                # -----------------------------------------

                for seat in selected_seats:

                    SeatHold.objects.create(

                        user=request.user,

                        show=show,

                        seat=seat,

                        expires_at=
                        hold_expiry
                    )


                # -----------------------------------------
                # REAL PRICE CALCULATION
                # -----------------------------------------

                total_amount = sum(

                    get_seat_price(
                        show,
                        seat
                    )

                    for seat
                    in selected_seats

                )


                # Cancel previous unfinished
                # bookings for this show/user.

                Booking.objects.filter(

                    user=request.user,

                    show=show,

                    status="PENDING"

                ).update(

                    status="CANCELLED"

                )


                booking = (
                    Booking.objects.create(

                        user=request.user,

                        show=show,

                        total_amount=
                        total_amount,

                        status="PENDING"

                    )
                )


                for seat in selected_seats:

                    BookingSeat.objects.create(

                        booking=booking,

                        seat=seat

                    )


                return redirect(

                    "booking_summary",

                    booking_id=
                    booking.id

                )


        except IntegrityError:

            messages.error(
                request,
                "Another user selected one of those seats. Please select again."
            )

            return redirect(
                "select_seats",
                show_id=show.id
            )


    context = {

        "show":
            show,

        "seat_sections":
            seat_sections,

        "max_seats":
            MAX_SEATS_PER_BOOKING,

    }


    return render(
        request,
        "bookings/select_seats.html",
        context
    )


# ==========================================================
# BOOKING SUMMARY + SEND OTP
# ==========================================================

@login_required
def booking_summary(
    request,
    booking_id
):

    booking = get_object_or_404(

        Booking,

        id=booking_id,

        user=request.user

    )


    if (
        booking.status
        ==
        "CONFIRMED"
    ):

        return redirect(

            "booking_success",

            booking_id=
            booking.id

        )


    if (
        booking.status
        ==
        "CANCELLED"
    ):

        messages.error(
            request,
            "This booking is no longer active."
        )

        return redirect(
            "select_seats",
            show_id=
            booking.show.id
        )


    booking_seats = (

        booking.booking_seats
        .select_related(
            "seat"
        )
        .all()

    )


    seat_ids = list(

        booking_seats
        .values_list(
            "seat_id",
            flat=True
        )

    )


    valid_holds = (

        SeatHold.objects.filter(

            user=request.user,

            show=
            booking.show,

            seat_id__in=
            seat_ids,

            expires_at__gt=
            timezone.now()

        )

    )


    if (
        valid_holds.count()
        !=
        len(seat_ids)
    ):

        booking.status = (
            "CANCELLED"
        )

        booking.save(
            update_fields=[
                "status"
            ]
        )


        SeatHold.objects.filter(

            user=request.user,

            show=booking.show,

            seat_id__in=
            seat_ids

        ).delete()


        messages.error(
            request,
            "Your seat hold expired. Please select seats again."
        )


        return redirect(

            "select_seats",

            show_id=
            booking.show.id

        )


    # ======================================================
    # SEND OTP
    # ======================================================

    if request.method == "POST":


        if not request.user.email:

            messages.error(
                request,
                "Your account does not have an email address."
            )

            return redirect(
                "booking_summary",
                booking_id=
                booking.id
            )


        otp = (

            f"{secrets.randbelow(1000000):06d}"

        )


        OTPVerification.objects.filter(
            booking=booking
        ).delete()


        otp_record = (

            OTPVerification.objects.create(

                booking=booking,

                otp=otp,

                is_verified=False

            )

        )


        new_expiry = (

            timezone.now()

            +
            timedelta(
                minutes=5
            )

        )


        SeatHold.objects.filter(

            user=request.user,

            show=
            booking.show,

            seat_id__in=
            seat_ids

        ).update(

            expires_at=
            new_expiry

        )


        try:

            result = send_mail(

                subject=
                "MovieHub Booking OTP",

                message=(
                    f"Hi {request.user.username},\n\n"
                    f"Your MovieHub OTP is: {otp}\n\n"
                    f"Movie: {booking.show.movie.title}\n"
                    f"Theatre: {booking.show.screen.theatre.name}\n"
                    f"Date: {booking.show.show_date}\n"
                    f"Time: {booking.show.show_time}\n"
                    f"Amount: ₹{booking.total_amount}\n\n"
                    f"This OTP is valid for 5 minutes."
                ),

                from_email=
                settings.DEFAULT_FROM_EMAIL,

                recipient_list=[
                    request.user.email
                ],

                fail_silently=False,

            )


            if result == 1:

                messages.success(
                    request,
                    "OTP sent successfully. Check your email."
                )

                return redirect(

                    "verify_otp",

                    booking_id=
                    booking.id

                )


            otp_record.delete()


            messages.error(
                request,
                "Unable to send OTP."
            )


        except Exception as error:

            print(
                "EMAIL ERROR:",
                repr(error)
            )


            otp_record.delete()


            messages.error(
                request,
                "Unable to send OTP. Please try again."
            )


        return redirect(

            "booking_summary",

            booking_id=
            booking.id

        )


    return render(

        request,

        "bookings/booking_summary.html",

        {

            "booking":
                booking,

            "booking_seats":
                booking_seats,

        }

    )


# ==========================================================
# VERIFY OTP
# ==========================================================

@login_required
def verify_otp(
    request,
    booking_id
):

    booking = get_object_or_404(

        Booking,

        id=booking_id,

        user=request.user

    )


    if (
        booking.status
        ==
        "CONFIRMED"
    ):

        return redirect(

            "booking_success",

            booking_id=
            booking.id

        )


    otp_record = (

        OTPVerification.objects
        .filter(
            booking=booking
        )
        .first()

    )


    if not otp_record:

        messages.error(
            request,
            "OTP not found. Request another OTP."
        )

        return redirect(

            "booking_summary",

            booking_id=
            booking.id

        )


    if request.method == "POST":

        entered_otp = (

            request.POST
            .get(
                "otp",
                ""
            )
            .strip()

        )


        otp_expiry = (

            otp_record.created_at

            +
            timedelta(
                minutes=5
            )

        )


        if (
            timezone.now()
            >
            otp_expiry
        ):

            otp_record.delete()


            messages.error(
                request,
                "OTP expired. Request another OTP."
            )


            return redirect(

                "booking_summary",

                booking_id=
                booking.id

            )


        if (
            entered_otp
            !=
            otp_record.otp
        ):

            messages.error(
                request,
                "Incorrect OTP."
            )

            return redirect(

                "verify_otp",

                booking_id=
                booking.id

            )


        seat_ids = list(

            booking.booking_seats
            .values_list(
                "seat_id",
                flat=True
            )

        )


        try:

            with transaction.atomic():


                booking = (

                    Booking.objects
                    .select_for_update()
                    .get(

                        id=booking.id,

                        user=request.user

                    )

                )


                conflict = (

                    BookingSeat.objects.filter(

                        booking__show=
                        booking.show,

                        booking__status=
                        "CONFIRMED",

                        seat_id__in=
                        seat_ids

                    ).exclude(

                        booking=booking

                    ).exists()

                )


                if conflict:

                    booking.status = (
                        "CANCELLED"
                    )

                    booking.save(
                        update_fields=[
                            "status"
                        ]
                    )


                    messages.error(
                        request,
                        "One of the seats is no longer available."
                    )


                    return redirect(

                        "select_seats",

                        show_id=
                        booking.show.id

                    )


                valid_holds = list(

                    SeatHold.objects
                    .select_for_update()
                    .filter(

                        user=
                        request.user,

                        show=
                        booking.show,

                        seat_id__in=
                        seat_ids,

                        expires_at__gt=
                        timezone.now()

                    )

                )


                if (
                    len(valid_holds)
                    !=
                    len(seat_ids)
                ):

                    booking.status = (
                        "CANCELLED"
                    )

                    booking.save(
                        update_fields=[
                            "status"
                        ]
                    )


                    messages.error(
                        request,
                        "Seat hold expired."
                    )


                    return redirect(

                        "select_seats",

                        show_id=
                        booking.show.id

                    )


                booking.status = (
                    "CONFIRMED"
                )


                booking.save(
                    update_fields=[
                        "status"
                    ]
                )


                otp_record.is_verified = (
                    True
                )


                otp_record.save(
                    update_fields=[
                        "is_verified"
                    ]
                )


                SeatHold.objects.filter(

                    user=request.user,

                    show=
                    booking.show,

                    seat_id__in=
                    seat_ids

                ).delete()


        except Exception as error:

            print(
                "BOOKING ERROR:",
                repr(error)
            )


            messages.error(
                request,
                "Booking confirmation failed."
            )


            return redirect(

                "verify_otp",

                booking_id=
                booking.id

            )


        messages.success(
            request,
            "Booking confirmed successfully."
        )


        return redirect(

            "booking_success",

            booking_id=
            booking.id

        )


    return render(

        request,

        "bookings/verify_otp.html",

        {
            "booking":
                booking
        }

    )


# ==========================================================
# BOOKING SUCCESS
# ==========================================================

@login_required
def booking_success(
    request,
    booking_id
):

    booking = get_object_or_404(

        Booking,

        id=booking_id,

        user=request.user,

        status="CONFIRMED"

    )


    booking_seats = (

        booking.booking_seats
        .select_related(
            "seat"
        )
        .all()

    )


    return render(

        request,

        "bookings/booking_success.html",

        {

            "booking":
                booking,

            "booking_seats":
                booking_seats,

        }

    )
@login_required
def my_bookings(request):

    bookings = (
        Booking.objects
        .filter(
            user=request.user,
            status="CONFIRMED"
        )
        .select_related(
            "show__movie",
            "show__screen__theatre"
        )
        .prefetch_related(
            "booking_seats__seat"
        )
        .order_by(
            "-created_at"
        )
    )

    return render(
        request,
        "bookings/my_bookings.html",
        {
            "bookings": bookings
        }
    )